import logging

from app.core.email_services.unique_id import send_unique_id_email
from app.core.email_services.verification import send_verification_code_email

logger = logging.getLogger(__name__)

def send_verification_to_email(user, code_record):
    email = getattr(user, "email", user)
    code = getattr(code_record, "code", code_record)
    send_verification_code_email(email, code)
    logger.info(f"📧 Sent verification code '{code}' to {email}")
    return {"email": email, "code": code, "status": "sent"}

def send_unique_id_to_email(user, unique_d):
    email = getattr(user, "email", user)
    unique_d = getattr(unique_d, "unique_d", unique_d)
    send_unique_id_email(email, unique_d)
    logger.info(f"📧 Sent unique_id '{unique_d}' to {email}")
    return {"email": email, "unique_id": unique_d, "status": "sent"}
