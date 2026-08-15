import asyncio
import logging
from pathlib import Path

import resend
from jinja2 import Environment, FileSystemLoader, select_autoescape

from src.core.settings import settings

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent


class EmailSendError(Exception):
    pass


class EmailService:
    def __init__(self) -> None:
        resend.api_key = settings.RESEND_API_KEY

        self.templates = Environment(
            loader=FileSystemLoader(BASE_DIR / "templates"),
            autoescape=select_autoescape(["html", "xml"]),
        )

    async def send_verification_email(
        self,
        email: str,
        token: str,
    ) -> None:
        verification_url = f"{settings.FRONTEND_URL}/verify-email?token={token}"

        html = self._render_template(
            "verify_email.html",
            verification_url=verification_url,
        )

        await self._send(
            email,
            subject="Verify your email address",
            template=html,
        )

    async def send_invitation_email(
        self,
        email: str,
        token: str,
        organization_name: str,
        inviter_name: str,
        role: str,
    ) -> None:
        invitation_url = f"{settings.FRONTEND_URL}/accept-invitation?token={token}"

        html = self._render_template(
            "invitation_email.html",
            invitation_url=invitation_url,
            organization_name=organization_name,
            inviter_name=inviter_name,
            role=role,
        )

        await self._send(
            email,
            subject=f"You've been invited to join {organization_name}",
            template=html,
        )

    async def _send(
        self,
        email: str,
        subject: str,
        template: str,
    ) -> None:
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
        except Exception as exc:
            logger.exception(
                "Failed to send email to %s",
                email,
            )
            raise EmailSendError("Failed to send email") from exc

    def _render_template(
        self,
        template_name: str,
        **context,
    ) -> str:
        try:
            template = self.templates.get_template(template_name)
            return template.render(**context)
        except Exception as exc:
            logger.exception(
                "Failed to render email template: %s",
                template_name,
            )
            raise EmailSendError("Failed to render email") from exc
