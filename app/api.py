from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import the shared router
from api_router import router as api_router

# Create the API-only FastAPI app
app = FastAPI()

# --- CORS Configuration ---
# You can have different CORS settings for your API-only service if needed
origins = ["http://<IP_servWEB>:8080"] # The origin for your other service
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["POST"], # API might only need POST
    allow_headers=["*"],
)

# --- Include the Shared API Router ---
app.include_router(api_router)

if __name__ == '__main__':
    import uvicorn
    # This will run ONLY the API endpoints
    uvicorn.run(app, host='0.0.0.0', port=5001)