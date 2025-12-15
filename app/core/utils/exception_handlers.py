import logging
import traceback
from fastapi import Request, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pymongo.errors import PyMongoError, DuplicateKeyError, OperationFailure
from pydantic import ValidationError

logger = logging.getLogger(__name__)


def setup_exception_handlers(app):
    """Register all custom exception handlers."""

    # ----------------------------
    # HTTP Exceptions
    # ----------------------------
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        logger.warning(f"HTTP {exc.status_code} at {request.method} {request.url.path}: {exc.detail}")

        if isinstance(exc.detail, dict) and "success" in exc.detail:
            return JSONResponse(status_code=exc.status_code, content=exc.detail)

        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "message": str(exc.detail),
                "error_code": _get_error_code(exc.status_code),
            },
        )

    # ----------------------------
    # Validation Errors
    # ----------------------------
    @app.exception_handler(ValidationError)
    async def validation_handler(request: Request, exc: ValidationError):
        logger.warning(f"Validation error at {request.method} {request.url.path}: {exc}")

        # Clean up error messages for better UX
        errors = []
        for error in exc.errors():
            clean_error = {
                "loc": error["loc"],
                "msg": error["msg"],
                "type": error["type"]
            }
            errors.append(clean_error)

        return JSONResponse(
            status_code=422,
            content={
                "success": False,
                "message": "Validation failed",
                "error_code": "VALIDATION_ERROR",
                "errors": errors,
            },
        )

    # ----------------------------
    # Custom Business Logic Errors
    # Add this for domain-specific errors
    # ----------------------------
    class BusinessError(Exception):
        def __init__(self, message: str, status_code: int = 400, error_code: str = None):
            self.message = message
            self.status_code = status_code
            self.error_code = error_code or _get_error_code(status_code)
            super().__init__(message)

    @app.exception_handler(BusinessError)
    async def business_error_handler(request: Request, exc: BusinessError):
        logger.warning(f"Business error at {request.method} {request.url.path}: {exc.message}")

        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "message": exc.message,
                "error_code": exc.error_code,
            },
        )

    # ----------------------------
    # MongoDB Errors
    # ----------------------------
    @app.exception_handler(DuplicateKeyError)
    async def duplicate_key_handler(request: Request, exc: DuplicateKeyError):
        logger.warning(f"Duplicate key at {request.method} {request.url.path}: {exc}")

        # Extract field name from error for better message
        field = "unknown"
        if hasattr(exc, 'details'):
            field = exc.details.get('keyPattern', {}).keys()
            field = list(field)[0] if field else "unknown"

        return JSONResponse(
            status_code=409,
            content={
                "success": False,
                "message": f"Resource with this {field} already exists",
                "error_code": "DUPLICATE_KEY",
                "field": field,
            },
        )

    @app.exception_handler(OperationFailure)
    async def operation_failure_handler(request: Request, exc: OperationFailure):
        logger.error(f"MongoDB operation failed at {request.method} {request.url.path}: {exc}")

        # Don't expose internal MongoDB errors to users
        user_message = "Database operation failed"
        if exc.code in [13, 18]:  # Authentication errors
            user_message = "Database authentication failed"
        elif exc.code == 11600:  # Interrupted operation
            user_message = "Database operation interrupted"

        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "message": user_message,
                "error_code": "DATABASE_OPERATION_FAILED",
            },
        )

    @app.exception_handler(PyMongoError)
    async def mongodb_handler(request: Request, exc: PyMongoError):
        logger.error(f"MongoDB error at {request.method} {request.url.path}: {exc}")

        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": "Database error occurred",
                "error_code": "DATABASE_ERROR",
            },
        )

    # ----------------------------
    # Catch-All Handler
    # ----------------------------
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        # Check if it's a common client error we want to handle specially
        if isinstance(exc, (ValueError, TypeError, KeyError, AttributeError)):
            # Log as warning, not critical
            logger.warning(
                f"Client error at {request.method} {request.url.path}: {exc}"
            )
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "message": str(exc),
                    "error_code": "BAD_REQUEST",
                },
            )

        # Otherwise, it's a server error
        logger.critical(
            f"Unhandled exception at {request.method} {request.url.path}:\n"
            f"Error: {exc}\n"
            f"Traceback: {traceback.format_exc()}"
        )

        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": "Internal server error",
                "error_code": "INTERNAL_ERROR",
            },
        )

    # Make BusinessError available for import
    app.BusinessError = BusinessError



    @app.exception_handler(RequestValidationError)
    async def request_validation_handler(request: Request, exc: RequestValidationError):
        logger.warning(f"Request validation error at {request.url.path}: {exc}")

        return JSONResponse(
            status_code=422,
            content={
                "success": False,
                "message": "Invalid request data",
                "error_code": "VALIDATION_ERROR",
                "errors": exc.errors(),
            },
        )


def _get_error_code(status_code: int) -> str:
    """Map HTTP status codes to custom error codes."""
    error_map = {
        400: "BAD_REQUEST",
        401: "UNAUTHORIZED",
        403: "FORBIDDEN",
        404: "NOT_FOUND",
        409: "CONFLICT",
        422: "VALIDATION_ERROR",
        429: "RATE_LIMIT_EXCEEDED",
        500: "INTERNAL_ERROR",
        503: "SERVICE_UNAVAILABLE",
    }
    return error_map.get(status_code, f"HTTP_{status_code}")
