from app.core.email_services.base import email_service
from app.core.email_services.templates import build_password_reset_template, build_password_changed_template


async def send_password_reset_email(email: str, reset_url: str, expires_in_minutes: int = 30):
    subject = "Reset Your Password"
    html, text = build_password_reset_template(reset_url, expires_in_minutes)
    return await email_service.send_email(email, subject, html, text)


async def send_password_changed_confirmation(email: str):
    subject = "Your Password Has Been Changed"
    html, text = build_password_changed_template()
    return await email_service.send_email(email, subject, html, text)
