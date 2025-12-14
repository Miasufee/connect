from datetime import datetime, timedelta, timezone
from types import MappingProxyType
from uuid import UUID
from fastapi import status
from fastapi.responses import JSONResponse
from typing import Any, Optional, Dict, List, Union
from pydantic import BaseModel, ConfigDict
import enum

# Handle Beanie's PydanticObjectId if available
try:
    from beanie import PydanticObjectId

    BEANIE_AVAILABLE = True
except ImportError:
    BEANIE_AVAILABLE = False
    PydanticObjectId = None


def prepare_json_data(value: Any) -> Any:
    """
    Recursively prepare values for JSON serialization.
    Converts complex types (enums, datetimes, UUIDs, Pydantic models, ORM objects, Beanie ObjectIds)
    into JSON-compatible primitives.
    """
    # Handle Beanie PydanticObjectId
    if BEANIE_AVAILABLE and PydanticObjectId and isinstance(value, PydanticObjectId):
        return str(value)
    elif isinstance(value, enum.Enum):
        return value.value
    elif isinstance(value, datetime):
        return value.isoformat()
    elif isinstance(value, UUID):
        return str(value)
    elif isinstance(value, MappingProxyType):
        return {k: prepare_json_data(v) for k, v in value.items()}
    elif isinstance(value, dict):
        return {k: prepare_json_data(v) for k, v in value.items()}
    elif isinstance(value, (list, tuple)):
        return [prepare_json_data(v) for v in value]
    elif isinstance(value, BaseModel):
        # Use model_dump with mode='json' and by_alias=True for proper serialization
        try:
            dumped = value.model_dump(mode='json', by_alias=True)
            # Recursively process the dumped dict to handle nested PydanticObjectIds
            return prepare_json_data(dumped)
        except Exception:
            # Fallback to dict conversion if model_dump fails
            return prepare_json_data(value.model_dump(by_alias=True))
    elif hasattr(value, "model_dump"):  # Pydantic v2 models (fallback)
        return prepare_json_data(value.model_dump(mode='json', by_alias=True))
    elif hasattr(value, "dict"):  # Pydantic v1 models
        return prepare_json_data(value.dict())
    elif hasattr(value, "__dict__"):  # ORM objects
        # Filter out private attributes and serialize remaining
        obj_dict = {k: v for k, v in vars(value).items() if not k.startswith('_')}
        return prepare_json_data(obj_dict)
    return value


def create_json_response(content: Any, status_code: int = 200) -> JSONResponse:
    """
    Create a JSONResponse with proper serialization handling.
    Handles Beanie documents, Pydantic models, and other complex types.
    """
    # Prepare content for JSON serialization
    serialized_content = prepare_json_data(content)

    return JSONResponse(status_code=status_code, content=serialized_content)


def set_token_cookie(response: JSONResponse, token: str, token_type: str, expires_in: int) -> JSONResponse:
    """
    Helper function to set a token as an HTTP-only cookie.
    """
    cookie_key = "access_token" if token_type.lower() == "bearer" else "refresh_token"
    expiry_time = datetime.utcnow().replace(tzinfo=timezone.utc) + timedelta(seconds=expires_in)

    response.set_cookie(
        key=cookie_key,
        value=token,
        httponly=True,
        secure=False,  # Set to True in production with HTTPS
        samesite="lax",
        max_age=expires_in,
        expires=expiry_time.strftime("%a, %d %b %Y %H:%M:%S GMT")
    )
    return response


# ==================== PYDANTIC RESPONSE MODELS ====================

class SuccessResponse(BaseModel):
    """Base success response model with Pydantic validation"""
    model_config = ConfigDict(arbitrary_types_allowed=True)

    success: bool = True
    message: str
    status_code: int
    data: Optional[Dict[str, Any]] = None


class PaginationMeta(BaseModel):
    """Pagination metadata model"""
    total_count: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_prev: bool


class PaginatedResponse(BaseModel):
    """Paginated response with validation"""
    model_config = ConfigDict(arbitrary_types_allowed=True)

    success: bool = True
    message: str
    status_code: int
    data: Dict[str, Any]  # Contains 'items' and 'pagination'


class Success:
    """
    Standardized success responses for the API with proper JSON serialization.
    Uses consistent response format: {"success": True, "message": "...", "data": {...}}

    Properly handles Beanie documents, Pydantic models, and complex types.
    """

    @staticmethod
    def json_response(
            message: str,
            status_code: int = status.HTTP_200_OK,
            data: Optional[Dict[str, Any]] = None,
            **kwargs
    ) -> JSONResponse:
        """
        Base method for all success responses.
        Handles Beanie documents and Pydantic models properly.
        """
        # Pre-process data to handle Beanie documents and complex types
        processed_data = prepare_json_data(data) if data is not None else None
        processed_kwargs = prepare_json_data(kwargs) if kwargs else {}

        # Create response content
        content = {
            "success": True,
            "message": message,
            "status_code": status_code
        }

        if processed_data is not None:
            content["data"] = processed_data

        if processed_kwargs:
            content.update(processed_kwargs)

        return JSONResponse(status_code=status_code, content=content)

    # ==================== GENERIC RESPONSES ====================

    @staticmethod
    def ok(message: str = "Request completed successfully", data: Optional[Dict[str, Any]] = None,
           **kwargs) -> JSONResponse:
        """Standard 200 OK response"""
        return Success.json_response(message, status.HTTP_200_OK, data, **kwargs)

    @staticmethod
    def created(message: str = "Resource created successfully", data: Optional[Dict[str, Any]] = None,
                **kwargs) -> JSONResponse:
        """Standard 201 Created response"""
        return Success.json_response(message, status.HTTP_201_CREATED, data, **kwargs)

    @staticmethod
    def accepted(message: str = "Request accepted for processing", data: Optional[Dict[str, Any]] = None,
                 **kwargs) -> JSONResponse:
        """Standard 202 Accepted response"""
        return Success.json_response(message, status.HTTP_202_ACCEPTED, data, **kwargs)

    @staticmethod
    def no_content() -> JSONResponse:
        """Standard 204 No Content response"""
        return JSONResponse(status_code=status.HTTP_204_NO_CONTENT, content=None)

    # ==================== USER MANAGEMENT RESPONSES ====================

    @staticmethod
    def account_created(user: Union[BaseModel, Dict, Any]) -> JSONResponse:
        """Response for successful user account creation"""
        # prepare_json_data handles Beanie documents automatically
        user_data = prepare_json_data(user)

        return Success.created(
            message="Account created successfully. Please verify your email.",
            data={"user": user_data}
        )

    @staticmethod
    def login_success(
            access_token: str,
            refresh_token: str,
            user: Union[BaseModel, Dict, Any],
            access_token_expires: int = 30 * 60,  # 30 minutes
            refresh_token_expires: int = 7 * 86400  # 7 days
    ) -> JSONResponse:
        """
        Successful login response with tokens set as HTTP-only cookies.
        """
        user_data = prepare_json_data(user)

        # Create base response
        response = Success.ok(
            message="Login successful",
            data={
                "user": user_data,
                "token_type": "bearer",
                "expires_in": access_token_expires
            }
        )

        # Set cookies with dynamic expiration times
        response = set_token_cookie(
            response=response,
            token=access_token,
            token_type="bearer",
            expires_in=access_token_expires
        )

        response = set_token_cookie(
            response=response,
            token=refresh_token,
            token_type="refresh",
            expires_in=refresh_token_expires
        )

        # Set security headers
        response.headers.update({
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "Cache-Control": "no-store"
        })

        return response

    @staticmethod
    def logout_success() -> JSONResponse:
        """Response for successful logout"""
        response = Success.ok(message="Logged out successfully")
        response.delete_cookie(key="access_token")
        response.delete_cookie(key="refresh_token")
        return response

    @staticmethod
    def verification_code_sent() -> JSONResponse:
        """Response for successful verification code sending"""
        return Success.ok(message="Verification code sent successfully")

    @staticmethod
    def email_verified() -> JSONResponse:
        """Response for successful email verification"""
        return Success.ok(message="Email verified successfully")

    @staticmethod
    def password_reset_requested() -> JSONResponse:
        """Response for successful password reset request"""
        return Success.ok(message="Password reset instructions sent to your email")

    @staticmethod
    def password_changed() -> JSONResponse:
        """Response for successful password change"""
        return Success.ok(message="Password changed successfully")

    # ==================== ADMIN RESPONSES ====================

    @staticmethod
    def admin_created(admin: Union[BaseModel, Dict, Any]) -> JSONResponse:
        """Response for successful admin account creation"""
        admin_data = prepare_json_data(admin)

        return Success.created(
            message="Admin account created successfully",
            data={"admin": admin_data}
        )

    @staticmethod
    def admin_login_success(
            access_token: str,
            admin: Union[BaseModel, Dict, Any],
            access_token_expires: int = 30 * 60
    ) -> JSONResponse:
        """Response for successful admin login"""
        admin_data = prepare_json_data(admin)

        response = Success.ok(
            message="Admin login successful",
            data={"admin": admin_data}
        )

        response = set_token_cookie(
            response=response,
            token=access_token,
            token_type="bearer",
            expires_in=access_token_expires
        )

        return response

    @staticmethod
    def user_updated(user: Union[BaseModel, Dict, Any]) -> JSONResponse:
        """Response for successful user update by admin"""
        user_data = prepare_json_data(user)

        return Success.ok(
            message="User updated successfully",
            data={"user": user_data}
        )

    @staticmethod
    def user_deleted() -> JSONResponse:
        """Response for successful user deletion by admin"""
        return Success.ok(message="User deleted successfully")

    # ==================== PAYMENT RESPONSES ====================

    @staticmethod
    def payment_success(
            transaction_id: str,
            amount: float,
            currency: str = "USD",
            **additional_details
    ) -> JSONResponse:
        """Response for successful payment processing"""
        return Success.ok(
            message="Payment processed successfully",
            data={
                "transaction_id": transaction_id,
                "amount": amount,
                "currency": currency,
                **additional_details
            }
        )

    @staticmethod
    def subscription_created(
            subscription_id: str,
            plan: str,
            start_date: datetime,
            end_date: datetime
    ) -> JSONResponse:
        """Response for successful subscription creation"""
        return Success.created(
            message="Subscription created successfully",
            data={
                "subscription_id": subscription_id,
                "plan": plan,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            }
        )

    @staticmethod
    def subscription_updated(subscription: Union[BaseModel, Dict, Any]) -> JSONResponse:
        """Response for successful subscription update"""
        subscription_data = prepare_json_data(subscription)

        return Success.ok(
            message="Subscription updated successfully",
            data={"subscription": subscription_data}
        )

    @staticmethod
    def subscription_cancelled() -> JSONResponse:
        """Response for successful subscription cancellation"""
        return Success.ok(message="Subscription cancelled successfully")

    # ==================== TOKEN RESPONSES ====================

    @staticmethod
    def token_refreshed(
            access_token: str,
            expires_in: int = 30 * 60
    ) -> JSONResponse:
        """Response for successful token refresh"""
        response = Success.ok(
            message="Token refreshed successfully",
            data={
                "token_type": "bearer",
                "expires_in": expires_in
            }
        )

        response = set_token_cookie(
            response=response,
            token=access_token,
            token_type="bearer",
            expires_in=expires_in
        )

        return response

    # ==================== CONTENT RESPONSES ====================

    @staticmethod
    def content_created(content: Union[BaseModel, Dict, Any]) -> JSONResponse:
        """Response for successful content creation"""
        content_data = prepare_json_data(content)

        return Success.created(
            message="Content created successfully",
            data={"content": content_data}
        )

    @staticmethod
    def content_updated(content: Union[BaseModel, Dict, Any]) -> JSONResponse:
        """Response for successful content update"""
        content_data = prepare_json_data(content)

        return Success.ok(
            message="Content updated successfully",
            data={"content": content_data}
        )

    @staticmethod
    def content_deleted() -> JSONResponse:
        """Response for successful content deletion"""
        return Success.ok(message="Content deleted successfully")

    @staticmethod
    def file_uploaded(file_url: str, file_name: str, file_size: int) -> JSONResponse:
        """Response for successful file upload"""
        return Success.created(
            message="File uploaded successfully",
            data={
                "file_url": file_url,
                "file_name": file_name,
                "file_size": file_size
            }
        )

    # ==================== CUSTOM RESPONSES ====================

    @staticmethod
    def custom_success(
            message: str,
            status_code: int = status.HTTP_200_OK,
            data: Optional[Dict[str, Any]] = None,
            **kwargs
    ) -> JSONResponse:
        """For non-standard success scenarios"""
        return Success.json_response(message, status_code, data, **kwargs)

    @staticmethod
    def data_list(
            items: List[Any],
            total_count: int,
            page: int = 1,
            page_size: int = 10,
            message: str = "Data retrieved successfully"
    ) -> JSONResponse:
        """Response for paginated data lists"""
        # Convert items using prepare_json_data to handle Beanie documents
        serialized_items = [prepare_json_data(item) for item in items]

        # Create pagination metadata
        pagination = {
            "total_count": total_count,
            "page": page,
            "page_size": page_size,
            "total_pages": (total_count + page_size - 1) // page_size,
            "has_next": page * page_size < total_count,
            "has_prev": page > 1
        }

        return Success.ok(
            message=message,
            data={
                "items": serialized_items,
                "pagination": pagination
            }
        )