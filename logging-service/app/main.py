from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import log_router
from app.core.config import settings
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Logging Service",
    description="Microservice for handling analytics and logging operations",
    version="1.0.0"
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
    return {"message": "Logging Service is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "logging-service"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
