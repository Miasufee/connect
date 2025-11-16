from app.core.email_services.base import email_service
from app.core.email_services.templates import build_welcome_template


async def send_welcome_email(email: str, user_name: str = None):
    subject = "Welcome to Our Platform!"
    html, text = build_welcome_template(user_name)
    return await email_service.send_email(email, subject, html, text)
