"""Password reset email template."""

from app.core.email.base_template import get_email_template


def get_password_reset_html(reset_url: str, expires_in_minutes: int = 30) -> str:
    """Generate HTML content for password reset email."""
    content = f"""
        <h2>Password Reset Request</h2>
        <p>We received a request to reset your password. Click the button below to create a new password.</p>
        
        <div style="text-align: center; margin: 32px 0;">
            <a href="{reset_url}" class="button button-danger">Reset My Password →</a>
        </div>
        
        <div style="text-align: center;">
            <span class="expiry-badge">
                ⏱️ Link expires in {expires_in_minutes} minutes
            </span>
        </div>
        
        <p style="color: #64748b; font-size: 13px; margin-top: 24px;">Button not working? Copy and paste this link into your browser:</p>
        <div class="link-box">
            <code>{reset_url}</code>
        </div>
        
        <div class="divider"></div>
        
        <div class="alert alert-warning">
            <span>⚠️</span>
            <div>
                <p><strong>Didn't request this?</strong></p>
                <p style="margin-top: 4px; font-size: 13px;">If you didn't request a password reset, you can safely ignore this email. Your password will remain unchanged.</p>
            </div>
        </div>
    """
    return get_email_template("🔑", "Password Reset", content)


def get_password_reset_text(reset_url: str, expires_in_minutes: int = 30) -> str:
    """Generate plain text content for password reset email."""
    return f"""
PASSWORD RESET REQUEST

We received a request to reset your password.

Reset your password by visiting this link:
{reset_url}

This link will expire in {expires_in_minutes} minutes.

DIDN'T REQUEST THIS?
If you didn't request a password reset, you can safely ignore this email. Your password will remain unchanged.
    """.strip()
