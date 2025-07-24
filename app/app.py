import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# Import the shared router
from api_router import router as api_router

# Create the main FastAPI app
app = FastAPI()

# --- CORS Configuration ---
# Adjust origins as needed
origins = ["*"] # Example: allow all for simplicity in dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
    allow_credentials=True,
)

# --- Include the Shared API Router ---
# All routes from api_router.py ("/chat", etc.) are now part of this app
app.include_router(api_router)


# --- Frontend Specific Setup ---
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/graphs", StaticFiles(directory="graphs"), name="graphs")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Serves the main HTML page."""
    return templates.TemplateResponse('index.html', {"request": request})


@app.get("/graphs", response_class=JSONResponse)
async def list_graphs():
    """Lists available graph images for the frontend."""
    graphs_dir = os.path.join(os.path.dirname(__file__), "graphs")
    if not os.path.isdir(graphs_dir):
        return []
    # This endpoint is specific to the UI, so it stays here
    return [f for f in os.listdir(graphs_dir) if f.endswith((".png", ".jpg", ".jpeg", ".gif"))]


# Note: The /graphs/{fname} endpoint is now handled by the StaticFiles mount above,
# so a separate endpoint for it is not strictly necessary unless you need custom logic.

if __name__ == '__main__':
    import uvicorn
    # This will run the full application with the frontend
    uvicorn.run(app, host='0.0.0.0', port=5001)