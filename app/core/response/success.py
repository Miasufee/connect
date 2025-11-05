from datetime import datetime, timedelta, timezone
from types import MappingProxyType
from uuid import UUID
from fastapi import status
from fastapi.responses import JSONResponse
from typing import Any, Optional, Dict, List
import enum
import json


# Custom JSON encoder that handles enums and other complex types
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, enum.Enum):
            return obj.value
        elif isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, UUID):
            return str(obj)
        elif hasattr(obj, "model_dump"):  # Pydantic v2 models
            return obj.model_dump()
        elif hasattr(obj, "dict"):  # Pydantic v1 models
            return obj.dict()
        elif hasattr(obj, "__dict__"):  # ORM objects
            # Convert ORM object to dict, then recursively serialize
            return {k: self.default(v) if not isinstance(v, (str, int, float, bool, type(None))) else v
                    for k, v in vars(obj).items() if not k.startswith('_')}
        return super().default(obj)


def serialize_value(value: Any) -> Any:
    """
    Recursively serialize values for JSON response compatibility.
    Handles complex types like enums, date times, UUIDs, and Pydantic models.
    """
    if isinstance(value, enum.Enum):
        return value.value
    elif isinstance(value, datetime):
        return value.isoformat()
    elif isinstance(value, UUID):
        return str(value)
    elif isinstance(value, MappingProxyType):
        return {k: serialize_value(v) for k, v in value.items()}
    elif isinstance(value, dict):
        return {k: serialize_value(v) for k, v in value.items()}
    elif isinstance(value, list):
        return [serialize_value(v) for v in value]
    elif hasattr(value, "model_dump"):  # Pydantic v2 models
        return serialize_value(value.model_dump())
    elif hasattr(value, "dict"):  # Pydantic v1 models
        return serialize_value(value.dict())
    elif hasattr(value, "__dict__"):  # ORM objects
        # Filter out private attributes and serialize remaining
        obj_dict = {k: v for k, v in vars(value).items() if not k.startswith('_')}
        return serialize_value(obj_dict)
    return value


def create_json_response(content: Any, status_code: int = 200) -> JSONResponse:
    """
    Create a JSONResponse with proper serialization handling.
    """
    # Serialize the content using our custom function
    serialized_content = serialize_value(content)

    # Use custom JSON encoder for additional safety
    json_content = json.loads(json.dumps(serialized_content, cls=CustomJSONEncoder))

    return JSONResponse(status_code=status_code, content=json_content)


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

    print(f"Setting {cookie_key} cookie with value: {token[:10]}... (expires in {expires_in} seconds)")
    return response


class Success:
    """
    Standardized success responses for the API with proper JSON serialization.
    Uses consistent response format: {"success": True, "message": "...", "data": {...}}
    """

    @staticmethod
    def json_response(
            message: str,
            status_code: int = status.HTTP_200_OK,
            data: Optional[Dict[str, Any]] = None,
            **kwargs
    ) -> JSONResponse:
        """Base method for all success responses with proper serialization"""
        content = {
            "success": True,
            "message": message,
            "status_code": status_code
        }

        # Add data if provided
        if data:
            content["data"] = serialize_value(data)

        # Add any additional kwargs as top-level fields
        if kwargs:
            content.update(serialize_value(kwargs))

        return create_json_response(content, status_code)

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
    def account_created(user: Any) -> JSONResponse:
        """Response for successful user account creation"""
        return Success.created(
            message="Account created successfully. Please verify your email.",
            data={"user": user}
        )

    @staticmethod
    def login_success(
            access_token: str,
            refresh_token: str,
            user: Any,
            access_token_expires: int = 30 * 60,  # 30 minutes
            refresh_token_expires: int = 7 * 86400  # 7 days
    ) -> JSONResponse:
        """
        Successful login response with tokens set as HTTP-only cookies.
        """
        # Create base response
        response = Success.ok(
            message="Login successful",
            data={
                "user": user,
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
    def admin_created(admin: Any) -> JSONResponse:
        """Response for successful admin account creation"""
        return Success.created(
            message="Admin account created successfully",
            data={"admin": admin}
        )

    @staticmethod
    def admin_login_success(
            access_token: str,
            admin: Any,
            access_token_expires: int = 30 * 60
    ) -> JSONResponse:
        """Response for successful admin login"""
        response = Success.ok(
            message="Admin login successful",
            data={"admin": admin}
        )

        response = set_token_cookie(
            response=response,
            token=access_token,
            token_type="bearer",
            expires_in=access_token_expires
        )

        return response

    @staticmethod
    def user_updated(user: Any) -> JSONResponse:
        """Response for successful user update by admin"""
        return Success.ok(
            message="User updated successfully",
            data={"user": user}
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
                "start_date": start_date,
                "end_date": end_date
            }
        )

    @staticmethod
    def subscription_updated(subscription: Any) -> JSONResponse:
        """Response for successful subscription update"""
        return Success.ok(
            message="Subscription updated successfully",
            data={"subscription": subscription}
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
    def content_created(content: Any) -> JSONResponse:
        """Response for successful content creation"""
        return Success.created(
            message="Content created successfully",
            data={"content": content}
        )

    @staticmethod
    def content_updated(content: Any) -> JSONResponse:
        """Response for successful content update"""
        return Success.ok(
            message="Content updated successfully",
            data={"content": content}
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
        return Success.ok(
            message=message,
            data={
                "items": items,
                "pagination": {
                    "total_count": total_count,
                    "page": page,
                    "page_size": page_size,
                    "total_pages": (total_count + page_size - 1) // page_size,
                    "has_next": page * page_size < total_count,
                    "has_prev": page > 1
                }
            }
        )