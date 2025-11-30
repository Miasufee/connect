"""Password changed confirmation email template."""

from app.core.services.email.base_template import get_email_template


def get_password_changed_html() -> str:
    """Generate HTML content for password changed confirmation email."""
    content = """
        <h2>Password Changed Successfully</h2>
        
        <div class="alert alert-success">
            <span>✅</span>
            <div>
                <p><strong>Your password has been updated</strong></p>
                <p style="margin-top: 4px; font-size: 13px;">You can now use your new password to sign in to your account.</p>
            </div>
        </div>
        
        <div class="divider"></div>
        
        <div class="alert alert-danger">
            <span>🚨</span>
            <div>
                <p><strong>Didn't make this change?</strong></p>
                <p style="margin-top: 4px; font-size: 13px;">If you did not change your password, please contact our support team immediately. Someone may have gained unauthorized access to your account.</p>
            </div>
        </div>
        
        <div style="text-align: center; margin-top: 24px;">
            <a href="#" class="button">Contact Support</a>
        </div>
        
        <p style="color: #94a3b8; font-size: 13px; margin-top: 24px;">
            For your security, we recommend using a strong, unique password and enabling two-factor authentication.
        </p>
    """
    return get_email_template("🔒", "Password Changed", content)


def get_password_changed_text() -> str:
    """Generate plain text content for password changed confirmation email."""
    return """
PASSWORD CHANGED SUCCESSFULLY

Your password has been updated. You can now use your new password to sign in to your account.

DIDN'T MAKE THIS CHANGE?
If you did not change your password, please contact our support team immediately. Someone may have gained unauthorized access to your account.

For your security, we recommend using a strong, unique password and enabling two-factor authentication.
    """.strip()
