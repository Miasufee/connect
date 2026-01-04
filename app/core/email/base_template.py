"""Base email template wrapper."""

from app.core.email.styles import get_base_styles


def get_email_template(header_icon: str, header_title: str, content: str) -> str:
    """Generate a complete email template with header, content, and footer."""
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <title>{header_title}</title>
        <style>
            {get_base_styles()}
        </style>
    </head>
    <body>
        <div class="wrapper">
            <div class="container">
                <div class="header">
                    <div class="icon">{header_icon}</div>
                    <h1>{header_title}</h1>
                </div>
                <div class="content">
                    {content}
                </div>
                <div class="footer">
                    <p class="brand">Your Company Name</p>
                    <p>© 2025 All rights reserved.</p>
                    <div class="social-links">
                        <a href="#">Twitter</a> •
                        <a href="#">LinkedIn</a> •
                        <a href="#">Support</a>
                    </div>
                    <p style="margin-top: 12px; font-size: 11px;">
                        This is an automated message. Please do not reply directly to this email.
                    </p>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
