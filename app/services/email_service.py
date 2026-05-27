import asyncio
import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from functools import partial

from app.core.config import settings

log = logging.getLogger("orderbot.email")


class EmailService:

    async def send(self, subject: str, body: str) -> bool:
        """Send email asynchronously using a thread pool executor."""
        if not settings.EMAIL_ENABLED:
            log.info("[Email disabled] %s", subject)
            return True
        if not all([settings.SMTP_USERNAME,
                    settings.SMTP_PASSWORD, settings.CAM_EMAIL]):
            log.warning("Email config missing — skipping")
            return False

        loop = asyncio.get_event_loop()
        try:
            await loop.run_in_executor(
                None,
                partial(self._send_sync, subject, body)
            )
            return True
        except Exception as e:
            log.error("Email failed: %s", e)
            return False

    def _send_sync(self, subject: str, body: str) -> None:
        msg = MIMEMultipart()
        msg["From"]    = settings.SMTP_USERNAME
        msg["To"]      = settings.CAM_EMAIL
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))
        with smtplib.SMTP(settings.SMTP_SERVER,
                          settings.SMTP_PORT, timeout=10) as s:
            s.starttls()
            s.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            s.send_message(msg)
        log.info("Email sent: %s", subject)


email_service = EmailService()
