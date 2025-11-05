import logging
import traceback
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from pymongo.errors import PyMongoError, DuplicateKeyError, OperationFailure
from pydantic import ValidationError

logger = logging.getLogger(__name__)


def setup_exception_handlers(app):
    """Register all custom exception handlers with simplified error handling."""

    # ----------------------------
    #  HTTP Exceptions (400-499)
    # ----------------------------
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        logger.warning(f"HTTP {exc.status_code} at {request.method} {request.url.path}: {exc.detail}")

        # If it's already in our custom format, return as-is
        if isinstance(exc.detail, dict) and "success" in exc.detail:
            return JSONResponse(status_code=exc.status_code, content=exc.detail)

        # Convert to our standard error format
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "message": str(exc.detail),
                "error_code": _get_error_code(exc.status_code),
            },
        )

    # ----------------------------
    #  Validation Errors
    # ----------------------------
    @app.exception_handler(ValidationError)
    async def validation_handler(request: Request, exc: ValidationError):
        logger.warning(f"Validation error at {request.method} {request.url.path}: {exc}")

        return JSONResponse(
            status_code=422,
            content={
                "success": False,
                "message": "Validation failed",
                "error_code": "VALIDATION_ERROR",
                "errors": exc.errors(),
            },
        )

    # ----------------------------
    #  MongoDB Errors
    # ----------------------------
    @app.exception_handler(DuplicateKeyError)
    async def duplicate_key_handler(request: Request, exc: DuplicateKeyError):
        logger.warning(f"Duplicate key at {request.method} {request.url.path}: {exc}")

        return JSONResponse(
            status_code=409,
            content={
                "success": False,
                "message": "Resource already exists",
                "error_code": "DUPLICATE_KEY",
            },
        )

    @app.exception_handler(OperationFailure)
    async def operation_failure_handler(request: Request, exc: OperationFailure):
        logger.error(f"MongoDB operation failed at {request.method} {request.url.path}: {exc}")

        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "message": "Database operation failed",
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
    #  Catch-All Handler
    # ----------------------------
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        # Log the full error with traceback
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


def _get_error_code(status_code: int) -> str:
    """Map HTTP status codes to custom error codes."""
    error_map = {
        # 4xx Client Errors
        400: "BAD_REQUEST",
        401: "UNAUTHORIZED",
        402: "PAYMENT_REQUIRED",
        403: "FORBIDDEN",
        404: "NOT_FOUND",
        405: "METHOD_NOT_ALLOWED",
        406: "NOT_ACCEPTABLE",
        408: "REQUEST_TIMEOUT",
        409: "CONFLICT",
        410: "GONE",
        411: "LENGTH_REQUIRED",
        412: "PRECONDITION_FAILED",
        413: "PAYLOAD_TOO_LARGE",
        414: "URI_TOO_LONG",
        415: "UNSUPPORTED_MEDIA_TYPE",
        416: "RANGE_NOT_SATISFIABLE",
        417: "EXPECTATION_FAILED",
        418: "IM_A_TEAPOT",
        421: "MISDIRECTED_REQUEST",
        422: "VALIDATION_ERROR",
        423: "LOCKED",
        424: "FAILED_DEPENDENCY",
        425: "TOO_EARLY",
        426: "UPGRADE_REQUIRED",
        428: "PRECONDITION_REQUIRED",
        429: "RATE_LIMIT_EXCEEDED",
        431: "REQUEST_HEADER_FIELDS_TOO_LARGE",
        451: "UNAVAILABLE_FOR_LEGAL_REASONS",

        # 5xx Server Errors
        500: "INTERNAL_ERROR",
        501: "NOT_IMPLEMENTED",
        502: "BAD_GATEWAY",
        503: "SERVICE_UNAVAILABLE",
        504: "GATEWAY_TIMEOUT",
        505: "HTTP_VERSION_NOT_SUPPORTED",
        506: "VARIANT_ALSO_NEGOTIATES",
        507: "INSUFFICIENT_STORAGE",
        508: "LOOP_DETECTED",
        510: "NOT_EXTENDED",
        511: "NETWORK_AUTHENTICATION_REQUIRED",
    }

    return error_map.get(status_code, "UNKNOWN_ERROR")