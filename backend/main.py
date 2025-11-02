from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

# Import routers
from routers import auth, projects, calculations

# Import database
from database import connect_to_mongo, close_mongo_connection

# Import settings
from config import settings

# Application lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Starting PoleStar API...")
    await connect_to_mongo()
    yield
    # Shutdown
    print("Shutting down PoleStar API...")
    await close_mongo_connection()

app = FastAPI(
    title="PoleStar API",
    description="Backend API for Steel Transmission Pole Design Software",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
# CORS origins are configured via ALLOWED_ORIGINS environment variable
# Format: comma-separated list (e.g., "http://localhost:8080,https://app.netlify.app")
# Default includes common development ports
cors_origins = settings.get_cors_origins()

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins if "*" not in cors_origins else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Include routers
# Note: Authentication is handled at the endpoint level via get_current_user dependency
app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
app.include_router(projects.router, prefix="/api/projects", tags=["projects"])
app.include_router(calculations.router, prefix="/api/calculations", tags=["calculations"])

@app.get("/")
async def root():
    return {"message": "PoleStar API is running!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/debug/cors")
async def debug_cors():
    """Debug endpoint to check CORS configuration (remove in production)"""
    return {
        "allowed_origins": cors_origins,
        "allowed_origins_raw": settings.allowed_origins,
        "app_url": settings.app_url
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
