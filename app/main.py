from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.core.auth_service.superuser_auth import superuser_create
from app.core.email_service import send_password_reset_email
from app.core.exception_handlers import setup_exception_handlers
from app.core.settings import settings
from app.core.database import mongodb
from app.routes.api_routes import api_router

# Configure logging
logging.basicConfig(level=settings.LOG_LEVEL)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    # -------------------- STARTUP --------------------
    await mongodb.connect()
    logger.info("MongoDB connected successfully.")

    # Create superuser only once
    try:
        result = await superuser_create()
        logger.info(f"Superuser check: {result.get('message', result)}")
    except Exception as e:
        logger.error(f"Superuser creation failed: {e}")

    yield  # Application runs here

    # -------------------- SHUTDOWN --------------------
    await mongodb.disconnect()
    logger.info("MongoDB disconnected.")


# -------------------- APP SETUP --------------------
app = FastAPI(
    title="User Management API",
    description="Video content live stream app",
    version="1.0.0",
    openapi_url="/api/v1/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Setup exception handlers FIRST
setup_exception_handlers(app)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ALLOWED_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOWED_METHODS,
    allow_headers=settings.CORS_ALLOWED_HEADERS,
    expose_headers=settings.CORS_EXPOSE_HEADERS.split(",") if settings.CORS_EXPOSE_HEADERS else [],
)

# Include routes
app.include_router(api_router)


# -------------------- ROOT ENDPOINTS --------------------
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "User Management API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "environment": settings.APP_ENV,
    }


@app.post("/test-email")
async def test_email(background_tasks: BackgroundTasks):
    """Test endpoint to verify email setup"""
    try:
        test_url = "https://yourapp.com/reset-password?token=test123&email=test@example.com"

        background_tasks.add_task(
            send_password_reset_email,
            email=settings.EMAIL_HOST_USER,
            reset_url=test_url,
            expires_in_minutes=60
        )

        return {"message": "Test email sent - check your inbox"}
    except Exception as e:
        return {"error": str(e)}