import asyncio
from pathlib import Path

import resend
from jinja2 import Environment, FileSystemLoader, select_autoescape

from src.core.settings import settings

BASE_DIR = Path(__file__).resolve().parent.parent


class EmailService:
    def __init__(self) -> None:
        resend.api_key = settings.RESEND_API_KEY
        self.templates = Environment(
            loader=FileSystemLoader(BASE_DIR / "templates"),
            autoescape=select_autoescape(["html", "xml"]),
        )

    async def send_verification_email(self, email: str, token: str) -> None:
        verification_url = f"{settings.FRONTEND_URL}/verify-email?token={token}"
        html = self._render_template(
            "verify_email.html",
            verification_url=verification_url,
        )
        await self._send(email, subject="Verify your email address", template=html)

    async def send_reset_password(self, email: str, token: str) -> None:
        verification_url = f"{settings.FRONTEND_URL}/reset-password?token={token}"
        html = self._render_template(
            "reset_password.html",
            verification_url=verification_url,
        )
        await self._send(
            email, subject="Reset your Trello Clone password", template=html
        )

    async def _send(self, email: str, subject: str, template: str) -> None:
        try:
            await asyncio.to_thread(
                resend.Emails.send,
                {
                    "from": settings.EMAIL_FROM,
                    "to": email,
                    "subject": subject,
                    "html": template,
                },
            )
        except Exception:
            raise RuntimeError("Failed to send email")

    def _render_template(
        self,
        template_name: str,
        **context,
    ) -> str:
        template = self.templates.get_template(template_name)
        return template.render(**context)
