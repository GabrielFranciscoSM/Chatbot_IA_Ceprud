import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# Import the shared router
from api_router import router as api_router


APP_ROOT = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(APP_ROOT, "web", "static")
TEMPLATES_DIR = os.path.join(APP_ROOT, "web", "templates")
GRAPHS_DIR = os.path.join(APP_ROOT, "analytics", "graphs")

# Create the main FastAPI app
app = FastAPI()

# CORS Configuration
origins = [
    "http://localhost:3000",  # React frontend in development
    "http://frontend:80",     # Frontend service in Docker
    "http://localhost:80",    # Frontend served via nginx
    "*"  # Allow all for development - configure appropriately for production
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    allow_credentials=True,
)

# Include the Shared API Router
app.include_router(api_router)

# Static files for legacy support and analytics
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
app.mount("/graphs", StaticFiles(directory=GRAPHS_DIR), name="graphs")
templates = Jinja2Templates(directory=TEMPLATES_DIR)

@app.get("/", response_class=JSONResponse)
async def root():
    """API root endpoint - frontend is served separately."""
    return {
        "message": "Chatbot UGR API",
        "version": "2.0",
        "frontend_url": "http://localhost:3000",
        "docs": "/docs"
    }

@app.get("/legacy", response_class=HTMLResponse)
async def legacy_frontend(request: Request):
    """Serves the legacy HTML page for backwards compatibility."""
    return templates.TemplateResponse('index.html', {"request": request})


@app.get("/health")
async def health_check():
    """Health check endpoint for service readiness verification."""
    return {"status": "healthy", "service": "chatbot"}


@app.get("/graphs-list", response_class=JSONResponse)
async def list_graphs():
    """Lists available graph images for the frontend."""
    if not os.path.isdir(GRAPHS_DIR):
        return []
    return [f for f in os.listdir(GRAPHS_DIR) if f.endswith((".png", ".jpg", ".jpeg", ".gif"))]


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8080)