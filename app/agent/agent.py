import json
import logging
from datetime import datetime
from typing import AsyncGenerator, Optional

from openai import AsyncOpenAI
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models import Customer
from app.repositories import ChatRepository
from app.tools import OrderTools
from .prompts import SYSTEM_PROMPT, TOOL_DEFINITIONS

log    = logging.getLogger("orderbot.agent")
client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)


class OrderBotAgent:
    """
    Fully async LLM agent using OpenAI streaming + tool calling.

    Flow:
      1. Load conversation history from DB
      2. Stream first GPT response
      3. If tool call → execute tool async → stream final response
      4. All chunks yielded as plain text strings
    """

    def __init__(self, db: AsyncSession,
                 session_id: str,
                 customer: Optional[Customer]):
        self.db         = db
        self.session_id = session_id
        self.customer   = customer
        self.chat_repo  = ChatRepository(db)
        self.tools      = (
            OrderTools(db, customer.id) if customer else None
        )

    async def _build_messages(self, user_message: str) -> list:
        """Load history + system prompt + new message."""
        history  = await self.chat_repo.get_recent_messages(
            self.session_id, limit=20)
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        for m in history:
            role = "user" if m.role == "user" else "assistant"
            messages.append({"role": role, "content": m.content})
        messages.append({"role": "user", "content": user_message})
        return messages

    async def _execute_tool(self, name: str, args: dict) -> str:
        """Call the right tool method and return result as string."""
        if not self.tools:
            return "❌ No customer profile found."

        if name == "place_order":
            try:
                delivery = datetime.strptime(
                    args["delivery_date"], "%Y-%m-%d")
            except (ValueError, KeyError):
                return "Invalid date format. Please use YYYY-MM-DD."
            r = await self.tools.place_order(
                args["product"], args["quantity"], delivery)
            if not r.success:
                return r.error
            d = r.data
            return (
                f"Order #{d['id']} placed.\n"
                f"Product: {d['product']} | "
                f"Quantity: {d['quantity']} units | "
                f"Delivery: {d['delivery_date']} | "
                f"Status: {d['status']}"
            )

        if name == "track_order":
            r = await self.tools.get_order(args["order_id"])
            if not r.success:
                return r.error
            d = r.data
            return (
                f"Order #{d['id']}: {d['product']} x{d['quantity']} | "
                f"Status: {d['status']} | Delivery: {d['delivery_date']}"
            )

        if name == "list_orders":
            r = await self.tools.list_orders()
            if not r.success:
                return r.error
            if not r.data:
                return "No orders found."
            return "\n".join(
                f"#{o['id']}: {o['product']} x{o['quantity']} | "
                f"{o['status']} | {o['delivery_date']}"
                for o in r.data
            )

        if name == "cancel_order":
            r = await self.tools.cancel_order(args["order_id"])
            if not r.success:
                return r.error
            return (f"Order #{r.data['id']} "
                    f"({r.data['product']}) cancelled.")

        if name == "speed_up_order":
            r = await self.tools.speed_up_order(
                args["order_id"], args["reason"])
            if not r.success:
                return r.error
            return (f"Speed-up request submitted for "
                    f"Order #{r.data['order_id']}. CAM notified.")

        if name == "swap_order":
            r = await self.tools.swap_order(
                args["order_id"], args["details"])
            if not r.success:
                return r.error
            return (f"Swap request submitted for "
                    f"Order #{r.data['order_id']}. CAM notified.")

        return f"Unknown tool: {name}"

    async def stream(
        self, user_message: str
    ) -> AsyncGenerator[str, None]:
        """
        Main entry point.
        Yields text chunks as they arrive from GPT-4o.
        Handles tool calls transparently.
        """
        if not self.customer:
            yield "❌ No customer profile found for your account."
            return

        messages = await self._build_messages(user_message)

        log.info("[%s] Streaming %s — %d history msgs",
                 self.session_id, settings.OPENAI_MODEL, len(messages))

        # ── First streaming call ───────────────────────────────────────────
        stream = await client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=messages,
            tools=TOOL_DEFINITIONS,
            tool_choice="auto",
            stream=True,
        )

        collected_content    = ""
        collected_tool_calls = {}   # index → {id, name, arguments}

        async for chunk in stream:
            delta = chunk.choices[0].delta if chunk.choices else None
            if not delta:
                continue

            # Plain text — yield immediately
            if delta.content:
                collected_content += delta.content
                yield delta.content

            # Tool call chunks — accumulate
            if delta.tool_calls:
                for tc in delta.tool_calls:
                    idx = tc.index
                    if idx not in collected_tool_calls:
                        collected_tool_calls[idx] = {
                            "id":        "",
                            "name":      "",
                            "arguments": "",
                        }
                    if tc.id:
                        collected_tool_calls[idx]["id"] = tc.id
                    if tc.function:
                        if tc.function.name:
                            collected_tool_calls[idx]["name"] += \
                                tc.function.name
                        if tc.function.arguments:
                            collected_tool_calls[idx]["arguments"] += \
                                tc.function.arguments

        # No tool calls — done
        if not collected_tool_calls:
            return

        # ── Execute tools ──────────────────────────────────────────────────
        tool_calls_for_msg = [
            {
                "id":   v["id"],
                "type": "function",
                "function": {
                    "name":      v["name"],
                    "arguments": v["arguments"],
                },
            }
            for v in collected_tool_calls.values()
        ]

        messages.append({
            "role":       "assistant",
            "content":    collected_content or None,
            "tool_calls": tool_calls_for_msg,
        })

        tool_results = []
        for v in collected_tool_calls.values():
            try:
                args = json.loads(v["arguments"])
            except json.JSONDecodeError:
                args = {}
            log.info("[%s] Tool: %s(%s)",
                     self.session_id, v["name"], args)
            result = await self._execute_tool(v["name"], args)
            log.info("[%s] Result: %s", self.session_id, result)
            tool_results.append({
                "tool_call_id": v["id"],
                "role":         "tool",
                "content":      result,
            })

        messages.extend(tool_results)

        # ── Second streaming call — final response ─────────────────────────
        final_stream = await client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=messages,
            tools=TOOL_DEFINITIONS,
            tool_choice="none",
            stream=True,
        )

        async for chunk in final_stream:
            delta = chunk.choices[0].delta if chunk.choices else None
            if delta and delta.content:
                yield delta.content
