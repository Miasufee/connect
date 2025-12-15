from pydantic import EmailStr
from starlette.responses import JSONResponse

from app.core.response.exceptions import Exceptions
from app.core.response.success import Success
from app.core.utils.generator import IDPrefix, GeneratorManager
from app.crud import user_crud
from app.models.user_models import User, UserRole


class RoleService:
    """Handles user role validation and updates."""

    @staticmethod
    async def _validate_permissions(actor: User, target_user: User, new_role: UserRole):
        """Validate permissions for role changes between actor and target user."""
        actor_role = actor.user_role
        target_role = target_user.user_role

        if actor_role == UserRole.superuser:
            return

        elif actor_role == UserRole.super_admin:
            if target_role in [UserRole.super_admin, UserRole.superuser]:
                raise Exceptions.forbidden("SUPER_ADMIN cannot modify SUPER_ADMIN or SUPERUSER")
            if new_role not in [UserRole.user, UserRole.admin]:
                raise Exceptions.forbidden("SUPER_ADMIN can only set USER or ADMIN")
            if target_role not in [UserRole.user, UserRole.admin]:
                raise Exceptions.forbidden("SUPER_ADMIN cannot change this account")
        else:
            raise Exceptions.forbidden("Insufficient permissions to change roles")

    @staticmethod
    async def _validate_business_rules(target_user: User, new_role: UserRole):
        """Validate business rules for role changes."""
        if target_user.user_role == UserRole.superuser and new_role != UserRole.superuser:
            raise Exceptions.forbidden("Cannot change role of SUPERUSER")
        if target_user.user_role == new_role:
            raise Exceptions.already_verified("User already has this role")

    @staticmethod
    async def _apply_role_change(user: User, new_role: UserRole):
        """Apply role change to user."""
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

    @staticmethod
    async def update_role(actor: User, target_email: EmailStr, new_role: UserRole) -> JSONResponse:
        """Update a user's role with proper validation and permissions."""
        db_user = await user_crud.get_by_email(target_email)
        if not db_user:
            raise Exceptions.not_found("User not found")

        if not isinstance(new_role, UserRole):
            raise Exceptions.bad_request("Invalid role")

        await RoleService._validate_permissions(actor, db_user, new_role)
        await RoleService._validate_business_rules(db_user, new_role)
        await RoleService._apply_role_change(db_user, new_role)
        return Success.ok(detail="User role update success")

role_service = RoleService()