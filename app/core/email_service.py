import logging
logger = logging.getLogger("email_service")

def send_verification_to_email(user, code_record):
    """
    Logs only the email and verification code.
    """
    email = getattr(user, "email", user)
    code = getattr(code_record, "code", code_record)

    logger.info(f"📧 Sent verification code '{code}' to {email}")
    return {"email": email, "code": code, "status": "logged"}
