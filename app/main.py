from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from contextlib import asynccontextmanager
import logging

from app.core.auth_service.superuser_auth import superuser_create
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
        await superuser_create()
        logger.info(f"Superuser checked")
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


setup_exception_handlers(app)


app.add_middleware(
    SessionMiddleware,
    secret_key=settings.APP_SECRET_KEY,
    session_cookie="session",
    max_age=14 * 24 * 60 * 60,
    same_site="lax",
    https_only=False,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ALLOWED_ORIGINS,
    allow_credentials=True,
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
