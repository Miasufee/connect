from app.core.email.templates.verification_code import (
    get_verification_code_html,
    get_verification_code_text,
)
from app.core.email.templates.welcome import (
    get_welcome_html,
    get_welcome_text,
)
from app.core.email.templates.unique_id import (
    get_unique_id_html,
    get_unique_id_text,
)
from app.core.email.templates.password_reset import (
    get_password_reset_html,
    get_password_reset_text,
)
from app.core.email.templates.password_changed import (
    get_password_changed_html,
    get_password_changed_text,
)

__all__ = [
    "get_verification_code_html",
    "get_verification_code_text",
    "get_welcome_html",
    "get_welcome_text",
    "get_unique_id_html",
    "get_unique_id_text",
    "get_password_reset_html",
    "get_password_reset_text",
    "get_password_changed_html",
    "get_password_changed_text",
]
