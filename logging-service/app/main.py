from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.routers import log_router
from app.core.config import settings
from app.core.database import MongoDB
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle"""
    # Startup: Connect to MongoDB
    try:
        await MongoDB.connect()
        logger.info("Logging service started successfully")
    except Exception as e:
        logger.error(f"Failed to start logging service: {e}")
        raise
    
    yield
    
    # Shutdown: Close MongoDB connection
    await MongoDB.close()
    logger.info("Logging service shut down")


app = FastAPI(
    title="Logging Service",
    description="Microservice for handling analytics and logging operations",
    version="2.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(log_router.router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "Logging Service is running", "version": "2.0.0", "storage": "MongoDB"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "logging-service", "version": "2.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
