"""Unique ID email template."""

from app.core.email.base_template import get_email_template


def get_unique_id_html(unique_id: str) -> str:
    """Generate HTML content for unique ID email."""
    content = f"""
        <h2>Your Unique Account ID</h2>
        <p>Here's your unique account identifier for administration. Keep it safe — you may need it for account verification or support requests.</p>
        
        <div class="id-box">
            <div class="id">{unique_id}</div>
        </div>
        
        <div class="alert alert-info">
            <span>💡</span>
            <div>
                <p><strong>When you might need this ID:</strong></p>
                <ul style="margin: 8px 0 0 16px; padding: 0; font-size: 13px;">
                    <li>Account verification requests</li>
                    <li>Account recovery situations</li>
                    <li>Account Login only administration</li>
                </ul>
            </div>
        </div>
        
        <div class="divider"></div>
        
        <p style="color: #94a3b8; font-size: 13px;">
            Store this ID somewhere safe. You can also find it anytime in your account settings.
        </p>
    """
    return get_email_template("🆔", "Account ID", content)


def get_unique_id_text(unique_id: str) -> str:
    """Generate plain text content for unique ID email."""
    return f"""
YOUR UNIQUE ACCOUNT ID

Here's your unique account identifier:

{unique_id}

WHEN YOU MIGHT NEED THIS ID:
• Account verification requests
• Contacting customer support
• Account recovery situations

Store this ID somewhere safe. You can also find it anytime in your account settings.
    """.strip()
