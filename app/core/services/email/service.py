"""Email service for sending emails via SMTP."""

import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from app.core.utils.settings import settings
from app.core.services.email.templates import (
    get_verification_code_html,
    get_verification_code_text,
    get_welcome_html,
    get_welcome_text,
    get_unique_id_html,
    get_unique_id_text,
    get_password_reset_html,
    get_password_reset_text,
    get_password_changed_html,
    get_password_changed_text,
)

logger = logging.getLogger(__name__)


class EmailService:
    def __init__(self):
        self.smtp_server = settings.EMAIL_HOST
        self.smtp_port = settings.EMAIL_PORT
        self.smtp_username = settings.EMAIL_HOST_USER
        self.smtp_password = settings.EMAIL_HOST_PASSWORD
        self.use_tls = settings.EMAIL_USE_TLS

    async def send_email(
            self,
            to_email: str,
            subject: str,
            html_content: str = None,
            text_content: str = None
    ) -> bool:
        """Send email using SMTP."""
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = settings.DEFAULT_FROM_EMAIL
            msg['To'] = to_email

            if text_content:
                text_part = MIMEText(text_content, 'plain')
                msg.attach(text_part)

            if html_content:
                html_part = MIMEText(html_content, 'html')
                msg.attach(html_part)

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                if self.use_tls:
                    server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)

            logger.info(f"Email sent successfully to: {to_email}")
            return True
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            return False

    async def send_verification_code_email(
            self,
            email: str,
            verification_code: str,
            expires_in_minutes: int = 10
    ) -> bool:
        """Send verification code email for login/account creation."""
        return await self.send_email(
            to_email=email,
            subject="Your Verification Code",
            html_content=get_verification_code_html(verification_code, expires_in_minutes),
            text_content=get_verification_code_text(verification_code, expires_in_minutes),
        )

    async def send_welcome_email(
            self,
            email: str,
            user_name: str = None
    ) -> bool:
        """Send welcome email after account creation."""
        return await self.send_email(
            to_email=email,
            subject="Welcome to Our Platform!",
            html_content=get_welcome_html(user_name),
            text_content=get_welcome_text(user_name),
        )

    async def send_unique_id_email(
            self,
            email: str,
            unique_id: str
    ) -> bool:
        """Send unique ID to user (for account reference, etc.)."""
        return await self.send_email(
            to_email=email,
            subject="Your Account ID",
            html_content=get_unique_id_html(unique_id),
            text_content=get_unique_id_text(unique_id),
        )

    async def send_password_reset_email(
            self,
            email: str,
            reset_url: str,
            expires_in_minutes: int = 30
    ) -> bool:
        """Send password reset email with the reset link."""
        return await self.send_email(
            to_email=email,
            subject="Reset Your Password",
            html_content=get_password_reset_html(reset_url, expires_in_minutes),
            text_content=get_password_reset_text(reset_url, expires_in_minutes),
        )

    async def send_password_changed_confirmation(
            self,
            email: str
    ) -> bool:
        """Send confirmation when password is successfully changed."""
        return await self.send_email(
            to_email=email,
            subject="Your Password Has Been Changed",
            html_content=get_password_changed_html(),
            text_content=get_password_changed_text(),
        )


# Global instance
email_service = EmailService()
