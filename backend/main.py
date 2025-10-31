from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

# Import routers
from routers import auth, projects, calculations

# Import database
from database import connect_to_mongo, close_mongo_connection

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
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite default
        "http://localhost:3000",   # React default
        "http://localhost:8080",   # Alternative port
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8080",
        "http://192.168.0.7:8080",
        "http://192.168.0.2:8080/",
    ],
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
