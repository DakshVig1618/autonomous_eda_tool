import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.api.endpoints import process, upload

# Resolve path locations for backend and separated frontend directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.abspath(os.path.join(BASE_DIR, "../../frontend"))

app = FastAPI(
    title="Autonomous Data Preprocessing Engine",
    version="1.0.0",
    docs_url="/docs",
)

# Configure static assets and Jinja2 template directories
static_dir = os.path.join(FRONTEND_DIR, "static")
templates_dir = os.path.join(FRONTEND_DIR, "templates")

app.mount("/static", StaticFiles(directory=static_dir), name="static")
templates = Jinja2Templates(directory=templates_dir)

# Middleware configuration for cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API endpoint routes
app.include_router(upload.router, prefix="/api/upload", tags=["Upload & Profiling"])
app.include_router(process.router, prefix="/api/process", tags=["AI Execution Sandbox"])


@app.get("/", tags=["Web UI"])
async def render_home(request: Request):
    """
    Renders the primary file upload page.
    """
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/dashboard", tags=["Web UI"])
async def render_dashboard(request: Request):
    """
    Renders the interactive data profiling and configuration dashboard.
    """
    return templates.TemplateResponse("dashboard.html", {"request": request})

# Register API Routers
app.include_router(upload.router, prefix="/api/upload", tags=["Upload & Profiling"])
app.include_router(process.router, prefix="/api/process", tags=["AI Execution Sandbox"])

@app.get("/", tags=["Web UI"])
async def render_home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/dashboard", tags=["Web UI"])
async def render_dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})