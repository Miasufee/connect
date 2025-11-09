import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.settings import settings

logger = logging.getLogger(__name__)


def send_verification_to_email(user, code_record):
    """
    Logs only the email and verification code.
    """
    email = getattr(user, "email", user)
    code = getattr(code_record, "code", code_record)

    logger.info(f"📧 Sent verification code '{code}' to {email}")
    return {"email": email, "code": code, "status": "logged"}

def send_unique_id_to_email(user, unique_d):
    """
    Logs only the email and verification code.
    """
    email = getattr(user, "email", user)
    unique_d = getattr(unique_d, "unique_d", unique_d)

    logger.info(f"📧 Sent unique_id code '{unique_d}' to {email}")
    return {"email": email, "unique_id": unique_d, "status": "logged"}

# def send_password_reset_email(email: str, token: str, role: str):
#     email = getattr(email, "email", email)
#     token = getattr(token, "token", token)
#     role = getattr(role, "role", role)
#
#     logger.info(f"sent reset token to the email{email} token {token} user role {role}")
#     return {"email": email, "token": token, "role":role}
#
#



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
        """
        Send email using Gmail SMTP.

        Args:
            to_email: Recipient email address
            subject: Email subject
            html_content: HTML content (optional)
            text_content: Plain text content (optional)

        Returns:
            bool: True if email sent successfully
        """
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = settings.DEFAULT_FROM_EMAIL
            msg['To'] = to_email

            # Attach both HTML and text parts
            if text_content:
                text_part = MIMEText(text_content, 'plain')
                msg.attach(text_part)

            if html_content:
                html_part = MIMEText(html_content, 'html')
                msg.attach(html_part)

            # Connect to SMTP server and send
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                if self.use_tls:
                    server.starttls()  # Enable TLS encryption

                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)

            logger.info(f"Email sent successfully to: {to_email}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            return False

    async def send_password_reset_email(
            self,
            email: str,
            reset_url: str,
            expires_in_minutes: int
    ) -> bool:
        """Send password reset email with the reset link."""
        subject = "Reset Your Password"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .button {{ display: inline-block; background: #007bff; color: white; padding: 12px 24px; 
                         text-decoration: none; border-radius: 4px; margin: 20px 0; }}
                .footer {{ margin-top: 30px; font-size: 12px; color: #666; }}
                .code {{ background: #f4f4f4; padding: 10px; border-radius: 4px; font-family: monospace; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h2>Password Reset Request</h2>
                <p>You requested to reset your password for your account.</p>
                <p>Click the button below to reset your password:</p>

                <p>
                    <a href="{reset_url}" class="button">Reset Password</a>
                </p>

                <p>Or copy and paste this link in your browser:</p>
                <p class="code">{reset_url}</p>

                <p>This reset link will expire in <strong>{expires_in_minutes} minutes</strong>.</p>

                <div class="footer">
                    <p>If you didn't request this password reset, please ignore this email.</p>
                    <p>Your account security is important to us.</p>
                </div>
            </div>
        </body>
        </html>
        """

        text_content = f"""
        Password Reset Request

        You requested to reset your password for your account.

        Reset your password by visiting this link:
        {reset_url}

        This reset link will expire in {expires_in_minutes} minutes.

        If you didn't request this password reset, please ignore this email.
        """

        return await self.send_email(
            to_email=email,
            subject=subject,
            html_content=html_content,
            text_content=text_content
        )


# Global instance
email_service = EmailService()


# Convenience functions
async def send_email(to_email: str, subject: str, html_content: str = None, text_content: str = None):
    return await email_service.send_email(to_email, subject, html_content, text_content)


async def send_password_reset_email(email: str, reset_url: str, expires_in_minutes: int):
    return await email_service.send_password_reset_email(email, reset_url, expires_in_minutes)