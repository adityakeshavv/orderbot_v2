SYSTEM_PROMPT = """You are OrderBot, a professional supply chain assistant for Tata Steel.
You help customers manage their steel orders through natural conversation.

You have access to these tools:
- place_order: Place a new order (needs product, quantity, delivery_date YYYY-MM-DD)
- track_order: Check status of an order (needs order_id)
- list_orders: Show all orders for the customer (no inputs needed)
- cancel_order: Cancel an order (needs order_id)
- speed_up_order: Request faster delivery (needs order_id, reason)
- swap_order: Request a product swap (needs order_id, details)

Rules:
1. Be professional and concise.
2. Ask for missing information one question at a time.
3. Before calling place_order, cancel_order, speed_up_order, or swap_order
   always show a clear summary and ask the user to confirm with yes or no.
4. For track_order and list_orders execute immediately without confirmation.
5. delivery_date must always be in YYYY-MM-DD format. If user gives a vague
   date like "end of december", ask them to confirm the exact date.
6. Never make up order IDs or product names.
7. Keep responses short and clear. Use markdown bold for important info.
8. If the user says something unrelated to orders, politely redirect them."""

TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name":        "place_order",
            "description": "Place a new steel order for the customer",
            "parameters": {
                "type": "object",
                "properties": {
                    "product": {
                        "type":        "string",
                        "description": "Name of the steel product",
                    },
                    "quantity": {
                        "type":        "integer",
                        "description": "Number of units to order",
                    },
                    "delivery_date": {
                        "type":        "string",
                        "description": "Requested delivery date in YYYY-MM-DD format",
                    },
                },
                "required": ["product", "quantity", "delivery_date"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name":        "track_order",
            "description": "Get the current status and details of an order",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {
                        "type":        "integer",
                        "description": "The order ID number",
                    },
                },
                "required": ["order_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name":        "list_orders",
            "description": "List all orders belonging to the customer",
            "parameters": {
                "type":       "object",
                "properties": {},
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name":        "cancel_order",
            "description": "Cancel an existing order",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {
                        "type":        "integer",
                        "description": "The order ID to cancel",
                    },
                },
                "required": ["order_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name":        "speed_up_order",
            "description": "Submit a request to expedite delivery of an order",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {
                        "type":        "integer",
                        "description": "The order ID to speed up",
                    },
                    "reason": {
                        "type":        "string",
                        "description": "Reason for the speed-up request",
                    },
                },
                "required": ["order_id", "reason"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name":        "swap_order",
            "description": "Submit a request to swap the product in an order",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {
                        "type":        "integer",
                        "description": "The order ID to swap",
                    },
                    "details": {
                        "type":        "string",
                        "description": "Details of what to swap to and why",
                    },
                },
                "required": ["order_id", "details"],
            },
        },
    },
]
