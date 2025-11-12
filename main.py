from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
import logging
import time
from collections import defaultdict
from typing import Dict
from config import settings
from database import connect_to_mongo, close_mongo_connection, get_database

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import routers
from routers import auth, calculations

# Rate limiting storage (in production, use Redis or similar)
rate_limit_store: Dict[str, list] = defaultdict(list)

def setup_rate_limiting_middleware(app: FastAPI):
    """Simple in-memory rate limiting middleware."""
    @app.middleware("http")
    async def rate_limit_middleware(request: Request, call_next):
        # Skip rate limiting for health checks
        if request.url.path in ["/health", "/"]:
            return await call_next(request)
        
        # Get client IP
        client_ip = request.client.host if request.client else "unknown"
        
        # Clean old entries (older than 1 minute)
        current_time = time.time()
        rate_limit_store[client_ip] = [
            timestamp for timestamp in rate_limit_store[client_ip]
            if current_time - timestamp < 60
        ]
        
        # Check rate limit
        if len(rate_limit_store[client_ip]) >= settings.rate_limit_per_minute:
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={"detail": "Rate limit exceeded. Please try again later."}
            )
        
        # Add current request timestamp
        rate_limit_store[client_ip].append(current_time)
        
        return await call_next(request)

def setup_security_headers_middleware(app: FastAPI):
    """Add security headers to all responses."""
    @app.middleware("http")
    async def security_headers_middleware(request: Request, call_next):
        response = await call_next(request)
        
        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # HSTS - only in production with HTTPS
        if settings.is_production and settings.app_url.startswith("https"):
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        return response

# Application lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting PoleStar API...")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Debug mode: {settings.debug}")
    
    await connect_to_mongo()
    
    # Validate production settings
    if settings.is_production:
        warnings = settings.validate_production_settings()
        for warning in warnings:
            logger.warning(warning)
    
    yield
    
    # Shutdown
    logger.info("Shutting down PoleStar API...")
    await close_mongo_connection()

app = FastAPI(
    title="PoleStar API",
    description="Backend API for Steel Transmission Pole Design Software",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs" if not settings.is_production else None,  # Disable docs in production
    redoc_url="/redoc" if not settings.is_production else None,  # Disable redoc in production
    max_request_size=settings.max_request_size,  # Limit request body size
)

# Setup middleware
setup_rate_limiting_middleware(app)
setup_security_headers_middleware(app)

# CORS middleware - uses environment variable
cors_origins = settings.get_cors_origins()
logger.info(f"CORS origins: {cors_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,  # Cache preflight requests for 1 hour
)

# Global exception handler for validation errors
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors with cleaner messages."""
    logger.warning(f"Validation error on {request.url.path}: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": "Validation error", "errors": exc.errors()}
    )

# Include routers
# Note: Authentication is handled at the endpoint level via get_current_user dependency
app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
app.include_router(calculations.router, prefix="/api/calculations", tags=["calculations"])

@app.get("/")
async def root():
    return {"message": "PoleStar API is running!"}

@app.get("/health")
async def health_check():
    """Comprehensive health check endpoint."""
    health_status = {
        "status": "healthy",
        "version": "1.0.0",
        "environment": settings.environment,
        "checks": {}
    }
    
    # Check MongoDB connection
    try:
        db = get_database()
        await db.client.admin.command('ping')
        health_status["checks"]["database"] = "healthy"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        health_status["checks"]["database"] = "unhealthy"
        health_status["status"] = "degraded"
    
    # Check email configuration
    if settings.email_user and settings.email_password:
        health_status["checks"]["email"] = "configured"
        health_status["checks"]["email_host"] = settings.email_host
        health_status["checks"]["email_port"] = settings.email_port
        health_status["checks"]["email_user"] = settings.email_user
        # Don't expose password
    else:
        health_status["checks"]["email"] = "not_configured"
        if settings.is_production:
            health_status["status"] = "degraded"
    
    return health_status


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
