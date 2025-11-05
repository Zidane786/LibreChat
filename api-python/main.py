"""Main FastAPI application entry point"""
import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from app.config import get_settings
from app.db import init_db, close_db
from app.utils.logger import logger
from app.utils.exceptions import LibreChatException


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    settings = get_settings()
    logger.info(f"Starting LibreChat API v{app.version}")
    logger.info(f"Environment: {'DEBUG' if settings.debug else 'PRODUCTION'}")

    try:
        # Initialize database connection
        await init_db()
        logger.info("Database connected successfully")
        yield
    finally:
        # Shutdown
        logger.info("Shutting down LibreChat API")
        await close_db()


# Create FastAPI application
settings = get_settings()
app = FastAPI(
    title=settings.app_title,
    version="0.8.1-rc1",
    description="LibreChat API - Python/FastAPI Backend",
    docs_url="/api/docs" if settings.debug else None,
    redoc_url="/api/redoc" if settings.debug else None,
    lifespan=lifespan
)


# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Compression Middleware
if settings.enable_compression:
    app.add_middleware(GZipMiddleware, minimum_size=1000)


# Exception handlers
@app.exception_handler(LibreChatException)
async def librechat_exception_handler(request: Request, exc: LibreChatException):
    """Handle LibreChat custom exceptions"""
    logger.error(f"LibreChatException: {exc.message}", extra={"details": exc.details})
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "message": exc.message,
            "details": exc.details
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    logger.exception("Unhandled exception", exc_info=exc)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": True,
            "message": "Internal server error",
            "details": str(exc) if settings.debug else None
        }
    )


# Health check endpoint
@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "ok",
        "version": app.version
    }


# Root endpoint
@app.get("/", tags=["root"])
async def root():
    """Root endpoint"""
    return {
        "message": "LibreChat API",
        "version": app.version,
        "docs": "/api/docs" if settings.debug else None
    }


# Import and include routers
from app.routes import auth, user

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(user.router, prefix="/api/user", tags=["user"])

# TODO: Add remaining route modules as they are created
# from app.routes import messages, conversations, prompts, agents, etc.
# app.include_router(messages.router, prefix="/api/messages", tags=["messages"])
# app.include_router(conversations.router, prefix="/api/convos", tags=["conversations"])
# etc.


if __name__ == "__main__":
    settings = get_settings()
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
