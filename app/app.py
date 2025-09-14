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
origins = ["*"]  # Configure appropriately for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
    allow_credentials=True,
)

# Include the Shared API Router
app.include_router(api_router)

# Frontend Setup
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
app.mount("/graphs", StaticFiles(directory=GRAPHS_DIR), name="graphs")
templates = Jinja2Templates(directory=TEMPLATES_DIR)

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Serves the main HTML page."""
    return templates.TemplateResponse('index.html', {"request": request})


@app.get("/health")
async def health_check():
    """Health check endpoint for service readiness verification."""
    return {"status": "healthy", "service": "chatbot"}


@app.get("/graphs", response_class=JSONResponse)
async def list_graphs():
    """Lists available graph images for the frontend."""
    if not os.path.isdir(GRAPHS_DIR):
        return []
    return [f for f in os.listdir(GRAPHS_DIR) if f.endswith((".png", ".jpg", ".jpeg", ".gif"))]


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=5001)