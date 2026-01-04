from app.core.email import email_service
from app.core.utils.generator import GeneratorManager, IDPrefix
from app.core.response.success import Success
from app.core.response.exceptions import Exceptions
from app.core.utils.settings import settings
from app.crud import user_crud
from app.models.user_models import UserRole


async def superuser_create():
    """
    Ensures a single superuser exists in the system.
    - Creates one if not found.
    - Sends the unique_id to configured email.
    - Runs safely even if called multiple times.
    """
    # Check if a superuser already exists
    existing_superuser = await user_crud.get_by_email(settings.API_SUPERUSER_EMAIL)
    if existing_superuser:
        if existing_superuser.user_role == UserRole.superuser:
            return Success.ok("Superuser already exists")
        else:
            raise Exceptions.forbidden("User exists but not a superuser")

    # Generate a unique ID for the superuser
    unique_id = GeneratorManager.generate_id(prefix=IDPrefix.SUPERUSER)

    # Create superuser record
    new_superuser = await user_crud.create(
        email=settings.API_SUPERUSER_EMAIL,
        user_role=UserRole.superuser,
        unique_id=unique_id,
        is_active=True,
        is_email_verified=True,
    )

    # Save document (Beanie model)
    await new_superuser.save()

    # Send unique ID via email
    await email_service.send_unique_id_email(new_superuser.email, unique_id)

    return Success.ok("Superuser created and email sent")
