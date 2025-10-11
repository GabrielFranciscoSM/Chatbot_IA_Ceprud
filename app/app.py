import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# Import the routers
from routes import router as api_router
from lti.routes import router as lti_router


APP_ROOT = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(APP_ROOT, "web", "static")
TEMPLATES_DIR = os.path.join(APP_ROOT, "web", "templates")
GRAPHS_DIR = os.path.join(APP_ROOT, "analytics", "graphs")

# Create the main FastAPI app
app = FastAPI()

# CORS Configuration
origins = [
    "http://localhost:3000",  # React frontend in development (Vite dev server)
    "http://localhost:8090",  # Frontend served via nginx (production - actual port)
    "http://127.0.0.1:3000",  # Alternative localhost address for dev
    "http://127.0.0.1:8090",  # Alternative localhost address for production
    "http://0.0.0.0:3000",    # Frontend container host binding (dev)
    "http://0.0.0.0:8090",    # Frontend nginx host binding (production)
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    allow_credentials=True,
    expose_headers=["X-RateLimit-Limit", "X-RateLimit-Remaining", "X-RateLimit-Reset"],
)

# Include the Shared API Router
app.include_router(api_router)
app.include_router(lti_router)

@app.get("/", response_class=JSONResponse)
async def root():
    """API root endpoint - frontend is served separately."""
    return {
        "message": "Chatbot UGR API",
        "version": "2.0",
        "frontend_url": "http://localhost:3000",
        "docs": "/docs"
    }


@app.get("/graphs-list", response_class=JSONResponse)
async def list_graphs():
    """Lists available graph images for the frontend."""
    if not os.path.isdir(GRAPHS_DIR):
        return []
    return [f for f in os.listdir(GRAPHS_DIR) if f.endswith((".png", ".jpg", ".jpeg", ".gif"))]


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8080)