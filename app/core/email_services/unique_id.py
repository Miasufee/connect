from app.core.email_services.base import email_service
from app.core.email_services.templates import build_unique_id_template


async def send_unique_id_email(email: str, unique_id: str):
    subject = "Your Unique Account ID"
    html, text = build_unique_id_template(unique_id)
    return await email_service.send_email(email, subject, html, text)
