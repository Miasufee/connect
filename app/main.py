from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.core.exception_handlers import setup_exception_handlers
from app.core.settings import settings
from app.core.database import mongodb
from app.routes.api_routes import api_router

# Configure logging
logging.basicConfig(level=settings.LOG_LEVEL)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    # Startup
    await mongodb.connect()
    yield
    # Shutdown
    await mongodb.disconnect()


# Create FastAPI application
app = FastAPI(
    title="User Management API",
    description="Video content live stream app",
    version="1.0.0",
    openapi_url="/api/v1/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Setup exception handlers FIRST (before middleware)
setup_exception_handlers(app)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ALLOWED_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOWED_METHODS,
    allow_headers=settings.CORS_ALLOWED_HEADERS,
    expose_headers=settings.CORS_EXPOSE_HEADERS.split(",") if settings.CORS_EXPOSE_HEADERS else []
)

app.include_router(api_router)

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
        "status": "healthy ",
        "environment": settings.APP_ENV
    }