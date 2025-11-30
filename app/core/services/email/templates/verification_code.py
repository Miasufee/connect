"""Verification code email template."""

from app.core.services.email.base_template import get_email_template


def get_verification_code_html(verification_code: str, expires_in_minutes: int = 10) -> str:
    """Generate HTML content for verification code email."""
    content = f"""
        <h2>Verify Your Identity</h2>
        <p>Enter the verification code below to complete your sign-in. This helps us keep your account secure.</p>
        
        <div class="code-box">
            <div class="code">{verification_code}</div>
        </div>
        
        <div style="text-align: center;">
            <span class="expiry-badge">
                ⏱️ Expires in {expires_in_minutes} minutes
            </span>
        </div>
        
        <div class="divider"></div>
        
        <div class="alert alert-warning">
            <span>⚠️</span>
            <div>
                <p><strong>Security Reminder</strong></p>
                <p style="margin-top: 4px; font-size: 13px;">Never share this code with anyone. Our team will never ask for your verification code.</p>
            </div>
        </div>
        
        <p style="color: #94a3b8; font-size: 13px; margin-top: 20px;">
            If you didn't request this code, you can safely ignore this email. Someone may have entered your email address by mistake.
        </p>
    """
    return get_email_template("🔐", "Verification Code", content)


def get_verification_code_text(verification_code: str, expires_in_minutes: int = 10) -> str:
    """Generate plain text content for verification code email."""
    return f"""
VERIFICATION CODE

Enter this code to complete your sign-in:

{verification_code}

This code will expire in {expires_in_minutes} minutes.

SECURITY REMINDER
Never share this code with anyone. Our team will never ask for your verification code.

If you didn't request this code, please ignore this email.
    """.strip()

