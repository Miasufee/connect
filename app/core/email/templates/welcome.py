"""Welcome email template."""

from app.core.email.base_template import get_email_template


def get_welcome_html(user_name: str = None) -> str:
    """Generate HTML content for welcome email."""
    greeting = user_name if user_name else "there"
    
    content = f"""
        <h2>Hey {greeting}! 👋</h2>
        <p>Welcome aboard! We're thrilled to have you join our community. Your account has been created and is ready to go.</p>
        
        <div class="alert alert-success">
            <span>✅</span>
            <div>
                <p><strong>Account Created Successfully</strong></p>
                <p style="margin-top: 4px; font-size: 13px;">You now have full access to all features.</p>
            </div>
        </div>
        
        <h3 style="font-size: 16px; font-weight: 600; margin-top: 28px; margin-bottom: 16px;">Get Started</h3>
        
        <ul class="list">
            <li>
                <span class="check">✓</span>
                <span><strong>Complete your profile</strong> — Add your details to personalize your experience</span>
            </li>
            <li>
                <span class="check">✓</span>
                <span><strong>Explore features</strong> — Discover what you can do with our platform</span>
            </li>
            <li>
                <span class="check">✓</span>
                <span><strong>Start your first project</strong> — Put your ideas into action</span>
            </li>
        </ul>
        
        <div style="text-align: center; margin-top: 32px;">
            <a href="#" class="button button-success">Go to Dashboard →</a>
        </div>
        
        <div class="divider"></div>
        
        <p style="color: #94a3b8; font-size: 13px;">
            Need help getting started? Check out our <a href="#" style="color: #6366f1;">documentation</a> or reach out to our <a href="#" style="color: #6366f1;">support team</a>.
        </p>
    """
    return get_email_template("🎉", "Welcome!", content)


def get_welcome_text(user_name: str = None) -> str:
    """Generate plain text content for welcome email."""
    greeting = user_name if user_name else "there"
    
    return f"""
WELCOME TO OUR PLATFORM!

Hey {greeting}!

We're thrilled to have you join our community. Your account has been created and is ready to go.

GET STARTED:

✓ Complete your profile — Add your details to personalize your experience
✓ Explore features — Discover what you can do with our platform  
✓ Start your first project — Put your ideas into action

Need help? Visit our documentation or contact our support team.

Best regards,
The Team
    """.strip()
