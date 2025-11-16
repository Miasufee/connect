from app.core.email_services.base import email_service
from app.core.email_services.templates import build_verification_template


async def send_verification_code_email(email: str, code: str, expires_in_minutes: int = 10):
    subject = "Your Verification Code"
    html, text = build_verification_template(code, expires_in_minutes)
    return await email_service.send_email(email, subject, html, text)
