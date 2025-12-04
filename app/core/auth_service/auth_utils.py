from typing import Optional

from pydantic import EmailStr

from app.core.generator import IDPrefix, GeneratorManager
from app.core.response.exceptions import Exceptions
from app.core.response.success import Success
from app.core.security import SecurityManager
from app.core.token_manager import token_manager
from app.crud import user_crud
from app.crud.refreshed_token_crud import refreshed_token_crud
from app.crud.verification_code_crud import verification_code_crud
from app.models.user_models import UserRole, User


async def get_verification(user_email):
    """
    Generate and store a new verification code for the user.
    Returns the code so it can be sent by email.
    """
    db_user = await user_crud.get_by_email(user_email)
    if not db_user:
        raise Exceptions.email_not_registered()

    # Optional: Delete any old verification code for the same user
    await verification_code_crud.delete_verification_code(str(db_user.id))

    # Create a new one
    code_record = await verification_code_crud.create_verification_code(str(db_user.id))

    # Return the code (for testing or sending via email)
    return Success.ok(
        message="Verification code generated successfully",
        verification_code=code_record
    )


async def verify_email(user_email, code: str):
    """
    Verify the user's email by matching their verification code.
    """
    db_user = await user_crud.get_by_email(user_email)
    if not db_user:
        raise Exceptions.email_not_registered()

    if db_user.is_email_verified:
        raise Exceptions.already_verified()

    # Validate verification code
    verification_result = await verification_code_crud.verify_code(db_user.id, code)

    if not verification_result:
        raise Exceptions.invalid_verification_code()

    # Mark email as verified
    db_user.is_email_verified = True
    await db_user.save()

    return Success.ok(message="Email verified successfully")


async def login_superuser_or_admins(email: EmailStr, unique_id: str, password: str):
    """
    Login flow for superuser, super_admin, or admin.

    Args:
        email (EmailStr): User email
        unique_id (str): Unique ID assigned to user
        password (str): Plain password

    Returns:
        dict: Success.login_success response with access + refresh tokens

    Raises:
        Exceptions.forbidden: Invalid credentials
    """
    # 1️⃣ Retrieve user by email
    user = await user_crud.get_by_email(email)

    # 2️⃣ Validate credentials
    if (
            not user
            or user.user_role not in [UserRole.superuser, UserRole.super_admin, UserRole.admin]
            or not SecurityManager.verify_password(password, user.hashed_password)
            or user.unique_id != unique_id
    ):
        # Constant-time comparison to mitigate timing attacks
        SecurityManager.constant_time_compare(0.5, 1.5)
        raise Exceptions.forbidden(detail="Invalid credentials")

    # 3️⃣ Generate JWT tokens
    access_token, refresh_token = await token_manager.generate_token_pair(user.email)

    # 4️⃣ Optional: update last login
    await user_crud.update_last_login(str(user.id))

    # 5️⃣ Return structured success response
    return Success.login_success(access_token, refresh_token, user)


# -----------------------------
# Logout current device
# -----------------------------
async def logout_current_device(current_refresh_token: str):
    """
    Logout from current device/session only.
    """
    revoked = await refreshed_token_crud.revoke_token(current_refresh_token)
    return Success.ok(message=f"Current device logged out: {revoked}")


# -----------------------------
# Logout all other devices
# -----------------------------
async def logout_all_other_devices(
    user: User,
    target_user_id: Optional[str] = None,
):
    """
    Logout from all other devices except the current session.
    - Normal users/admins: only their own devices
    - SuperAdmin/SuperUser: can revoke for any user by passing target_user_id
    """
    # Permission check
    if target_user_id and user.user_role not in ["super_admin", "superuser"]:
        raise PermissionError("Only SuperAdmin/SuperUser can revoke tokens for other users")

    user_id = target_user_id or str(user.id)
    revoked_count = await token_manager.revoke_user_tokens(user_id)

    # Keep current device alive for normal user
    if not target_user_id:
        await token_manager.create_refresh_token(user_id, token_version=+1)
    return Success.ok(message=f"Other devices logged out: {revoked_count}")


# -----------------------------
# Logout all devices
# -----------------------------
async def logout_all_devices(user: User, target_user_id: Optional[str] = None):
    """
    Logout from all devices.
    - SuperAdmin/SuperUser: can log out any user if target_user_id provided
    - Normal users/admins: logout themselves only
    """
    if target_user_id and user.user_role not in ["super_admin", "superuser"]:
        raise PermissionError("Only SuperAdmin/SuperUser can logout all devices for other users")

    user_id = target_user_id or str(user.id)
    revoked_count = await refreshed_token_crud.revoke_user_tokens(user_id)
    return Success.ok(message=f"All devices logged out: {revoked_count}")


# -----------------------------
# Cleanup expired/revoked tokens
# -----------------------------
async def cleanup_tokens():
    revoked_deleted = await refreshed_token_crud.purge_revoked_tokens(older_than_days=30)
    expired_deleted = await refreshed_token_crud.cleanup_expired_tokens(older_than_days=7)
    return Success.ok(
        message=f"Cleaned up tokens - revoked: {revoked_deleted}, expired: {expired_deleted}"
    )

# -------------------- ROLE MANAGEMENT --------------------

# -------------------- ROLE MANAGEMENT --------------------

async def _validate_role_change_permissions(actor: User, target_user: User, new_role: UserRole):
    """Validate permissions for role changes between actor and target user."""
    actor_role = actor.user_role
    target_role = target_user.user_role

    # SUPERUSER → full control
    if actor_role == UserRole.superuser:
        return

    # SUPER_ADMIN → limited control
    elif actor_role == UserRole.super_admin:
        # SUPER_ADMIN cannot change SUPER_ADMIN or SUPERUSER
        if target_role in [UserRole.super_admin, UserRole.superuser]:
            raise Exceptions.forbidden("SUPER_ADMIN cannot modify SUPER_ADMIN or SUPERUSER")

        # SUPER_ADMIN can only toggle USER <-> ADMIN
        if new_role not in [UserRole.user, UserRole.admin]:
            raise Exceptions.forbidden("SUPER_ADMIN can only set USER or ADMIN")

        if target_role not in [UserRole.user, UserRole.admin]:
            raise Exceptions.forbidden("SUPER_ADMIN cannot change this account")

    # Normal users: forbidden
    else:
        raise Exceptions.forbidden("Insufficient permissions to change roles")


async def _validate_role_change_business_rules(target_user: User, new_role: UserRole):
    """Validate business rules for role changes."""
    target_role = target_user.user_role

    # Prevent downgrading SUPERUSER
    if target_role == UserRole.superuser and new_role != UserRole.superuser:
        raise Exceptions.forbidden("Cannot change role of SUPERUSER")

    # Prevent same role change
    if target_role == new_role:
        raise Exceptions.already_verified("User already has this role")


async def _apply_role_change(user: User, new_role: UserRole):
    """Apply the role change and update user properties accordingly."""
    if new_role == UserRole.admin:
        user.user_role = UserRole.admin
        user.unique_id = GeneratorManager.generate_id(IDPrefix.ADMIN, 12)

    elif new_role == UserRole.super_admin:
        user.user_role = UserRole.super_admin
        user.unique_id = GeneratorManager.generate_id(IDPrefix.SUPER_ADMIN, 12)

    elif new_role == UserRole.user:
        user.user_role = UserRole.user
        user.unique_id = None

    await user.save()


async def update_role(actor: User, target_email: EmailStr, new_role: UserRole):
    """Main function to update user roles with proper validation and permissions."""
    # Validate input
    db_user = await user_crud.get_by_email(email=target_email)
    if not db_user:
        raise Exceptions.not_found("User not found")

    if not isinstance(new_role, UserRole):
        raise Exceptions.bad_request("Invalid role")

    # Validate permissions and business rules
    await _validate_role_change_permissions(actor, db_user, new_role)
    await _validate_role_change_business_rules(db_user, new_role)

    # Apply the role change
    await _apply_role_change(db_user, new_role)

    return Success.ok(detail="User role update success")
