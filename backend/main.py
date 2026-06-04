import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from starlette.requests import Request
import jinja2
from backend.database import init_db
from backend.routers.tests import router as tests_router
from backend.routers.auth import router as auth_router
from backend.routers.admin import router as admin_router

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "templates")
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")

jinja_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(TEMPLATES_DIR),
    autoescape=True,
)

def render(name: str, **context):
    template = jinja_env.get_template(name)
    html = template.render(**context)
    return HTMLResponse(html)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

app = FastAPI(title="nipX", lifespan=lifespan)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

app.include_router(auth_router)
app.include_router(tests_router)
app.include_router(admin_router)

@app.get("/")
async def landing(request: Request):
    return render("index.html", request=request)

@app.get("/dashboard")
async def dashboard(request: Request):
    return render("dashboard.html", request=request)

@app.get("/test/{test_id}")
async def test_detail(request: Request, test_id: int):
    return render("test_detail.html", request=request, test_id=test_id)

@app.get("/login")
async def login_page(request: Request):
    return render("login.html", request=request)

@app.get("/signup")
async def signup_page(request: Request):
    return render("signup.html", request=request)

@app.get("/test/{test_id}/report")
async def test_report(request: Request, test_id: int):
    return render("report.html", request=request)
