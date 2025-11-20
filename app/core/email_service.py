import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.settings import settings

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
        """
        Send email using SMTP.
        """
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
        subject = "Your Verification Code"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .code {{ 
                    background: #f4f4f4; 
                    padding: 15px; 
                    border-radius: 8px; 
                    font-family: monospace; 
                    font-size: 24px; 
                    font-weight: bold; 
                    text-align: center;
                    letter-spacing: 5px;
                    color: #007bff;
                    margin: 20px 0;
                    border: 2px dashed #007bff;
                }}
                .button {{ 
                    display: inline-block; 
                    background: #007bff; 
                    color: white; 
                    padding: 12px 24px; 
                    text-decoration: none; 
                    border-radius: 4px; 
                    margin: 20px 0; 
                }}
                .footer {{ margin-top: 30px; font-size: 12px; color: #666; }}
                .warning {{ color: #dc3545; font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h2>Verification Code</h2>
                <p>Use the verification code below to complete your login:</p>

                <div class="code">{verification_code}</div>

                <p class="warning">This code will expire in <strong>{expires_in_minutes} minutes</strong>.</p>

                <p>If you didn't request this code, please ignore this email.</p>

                <div class="footer">
                    <p>For security reasons, do not share this code with anyone.</p>
                </div>
            </div>
        </body>
        </html>
        """

        text_content = f"""
        Verification Code

        Use this code to complete your login:

        {verification_code}

        This code will expire in {expires_in_minutes} minutes.

        If you didn't request this code, please ignore this email.

        For security reasons, do not share this code with anyone.
        """

        return await self.send_email(
            to_email=email,
            subject=subject,
            html_content=html_content,
            text_content=text_content
        )

    async def send_welcome_email(
            self,
            email: str,
            user_name: str = None
    ) -> bool:
        """Send welcome email after account creation."""
        subject = "Welcome to Our Platform!"

        greeting = f"Hello {user_name}!" if user_name else "Hello!"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .welcome {{ color: #28a745; font-size: 24px; font-weight: bold; }}
                .button {{ 
                    display: inline-block; 
                    background: #28a745; 
                    color: white; 
                    padding: 12px 24px; 
                    text-decoration: none; 
                    border-radius: 4px; 
                    margin: 20px 0; 
                }}
                .footer {{ margin-top: 30px; font-size: 12px; color: #666; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="welcome">🎉 Welcome!</div>
                <h2>{greeting}</h2>

                <p>Thank you for creating an account with us! We're excited to have you on board.</p>

                <p>Your account has been successfully created and is ready to use.</p>

                <h3>What's Next?</h3>
                <ul>
                    <li>Complete your profile</li>
                    <li>Explore our features</li>
                    <li>Get started with your first project</li>
                </ul>

                <div class="footer">
                    <p>If you have any questions, feel free to contact our support team.</p>
                    <p>Best regards,<br>The Team</p>
                </div>
            </div>
        </body>
        </html>
        """

        text_content = f"""
        Welcome to Our Platform!

        {greeting}

        Thank you for creating an account with us! We're excited to have you on board.

        Your account has been successfully created and is ready to use.

        What's Next?
        • Complete your profile
        • Explore our features  
        • Get started with your first project

        If you have any questions, feel free to contact our support team.

        Best regards,
        The Team
        """

        return await self.send_email(
            to_email=email,
            subject=subject,
            html_content=html_content,
            text_content=text_content
        )

    async def send_unique_id_email(
            self,
            email: str,
            unique_id: str
    ) -> bool:
        """Send unique ID to user (for account reference, etc.)."""
        subject = "Your Account Unique ID"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .unique-id {{ 
                    background: #f8f9fa; 
                    padding: 15px; 
                    border-radius: 8px; 
                    font-family: monospace; 
                    font-size: 18px; 
                    font-weight: bold; 
                    text-align: center;
                    border: 2px solid #6c757d;
                    word-break: break-all;
                    margin: 20px 0;
                }}
                .footer {{ margin-top: 30px; font-size: 12px; color: #666; }}
                .note {{ background: #fff3cd; padding: 10px; border-radius: 4px; border-left: 4px solid #ffc107; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h2>Your Unique Account ID</h2>
                <p>Here is your unique account identifier:</p>

                <div class="unique-id">{unique_id}</div>

                <div class="note">
                    <p><strong>Please keep this ID safe.</strong> You may need it for:</p>
                    <ul>
                        <li>Account verification</li>
                        <li>Support requests</li>
                        <li>Account recovery</li>
                    </ul>
                </div>

                <div class="footer">
                    <p>This is an automated message. Please do not reply to this email.</p>
                </div>
            </div>
        </body>
        </html>
        """

        text_content = f"""
        Your Unique Account ID

        Here is your unique account identifier:

        {unique_id}

        Please keep this ID safe. You may need it for:
        • Account verification
        • Support requests  
        • Account recovery

        This is an automated message. Please do not reply to this email.
        """

        return await self.send_email(
            to_email=email,
            subject=subject,
            html_content=html_content,
            text_content=text_content
        )

    async def send_password_reset_email(
            self,
            email: str,
            reset_url: str,
            expires_in_minutes: int = 30
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
                .button {{ 
                    display: inline-block; 
                    background: #dc3545; 
                    color: white; 
                    padding: 12px 24px; 
                    text-decoration: none; 
                    border-radius: 4px; 
                    margin: 20px 0; 
                }}
                .footer {{ margin-top: 30px; font-size: 12px; color: #666; }}
                .code {{ 
                    background: #f8f9fa; 
                    padding: 10px; 
                    border-radius: 4px; 
                    font-family: monospace;
                    word-break: break-all;
                }}
                .warning {{ color: #dc3545; font-weight: bold; }}
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

                <p class="warning">This reset link will expire in <strong>{expires_in_minutes} minutes</strong>.</p>

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

    async def send_password_changed_confirmation(
            self,
            email: str
    ) -> bool:
        """Send confirmation when password is successfully changed."""
        subject = "Your Password Has Been Changed"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .alert {{ 
                    background: #d4edda; 
                    color: #155724; 
                    padding: 15px; 
                    border-radius: 4px; 
                    border: 1px solid #c3e6cb;
                    margin: 20px 0;
                }}
                .warning {{ 
                    background: #fff3cd; 
                    color: #856404; 
                    padding: 15px; 
                    border-radius: 4px; 
                    border: 1px solid #ffeaa7;
                    margin: 20px 0;
                }}
                .footer {{ margin-top: 30px; font-size: 12px; color: #666; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h2>Password Changed Successfully</h2>

                <div class="alert">
                    <p>Your password has been successfully updated.</p>
                </div>

                <div class="warning">
                    <p><strong>Security Notice:</strong></p>
                    <p>If you did not make this change, please contact our support team immediately.</p>
                </div>

                <div class="footer">
                    <p>This is an automated security notification.</p>
                </div>
            </div>
        </body>
        </html>
        """

        text_content = f"""
        Password Changed Successfully

        Your password has been successfully updated.

        Security Notice:
        If you did not make this change, please contact our support team immediately.

        This is an automated security notification.
        """

        return await self.send_email(
            to_email=email,
            subject=subject,
            html_content=html_content,
            text_content=text_content
        )


# Global instance
email_service = EmailService()
