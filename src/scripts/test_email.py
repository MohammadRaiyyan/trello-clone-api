import asyncio

from src.services.email import EmailService


async def main():
    email_service = EmailService()

    await email_service.send_verification_email(
        email="abcd@gmail.com",
        token="123456789",
    )


if __name__ == "__main__":
    asyncio.run(main())
