from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import uvicorn, os
from app.core.config import settings
from app.core.database import engine, Base, SessionLocal
from app.initial_data import init_db
from app.api.base import api_router
from app.api.endpoints import products

# 1. TEMPLATES & STATIC PATHS
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
possible_paths = [os.path.join(BASE_DIR, "templates"), "/opt/render/project/src/app/templates"]
template_path = next((p for p in possible_paths if os.path.exists(p)), os.path.join(BASE_DIR, "templates"))
templates = Jinja2Templates(directory=template_path)

app = FastAPI(title=settings.PROJECT_NAME)

# 2. HACK STATIC (Fix giao diện không cần sửa HTML)
static_path = os.path.join(BASE_DIR, "static")
if os.path.exists(static_path):
    for folder in ["css", "js", "lib", "img", "scss"]:
        if os.path.exists(os.path.join(static_path, folder)):
            app.mount(f"/{folder}", StaticFiles(directory=os.path.join(static_path, folder)), name=f"st_{folder}")

root_static = os.path.join(os.path.dirname(BASE_DIR), "static")
if os.path.exists(root_static):
    app.mount("/static", StaticFiles(directory=root_static), name="static_root")

# 3. FRONTEND ROUTES (Sửa lỗi request=request cho Starlette mới)
@app.get("/")
async def read_root(request: Request): return templates.TemplateResponse(request=request, name="index.html")

@app.get("/cart")
async def cart_page(request: Request): return templates.TemplateResponse(request=request, name="cart.html")

@app.get("/shop")
async def shop_page(request: Request): return templates.TemplateResponse(request=request, name="shop.html")

@app.get("/details")
async def details_page(request: Request): return templates.TemplateResponse(request=request, name="details.html")

# --- DASHBOARD MODERATOR ---
@app.get("/moderator/{page}.html")
async def moderator_pages(request: Request, page: str):
    return templates.TemplateResponse(request=request, name=f"moderator/moderator_{page}.html")

# --- DASHBOARD ADMIN ---
@app.get("/admin/{page}.html")
async def admin_pages(request: Request, page: str):
    return templates.TemplateResponse(request=request, name=f"admin/{page}.html")

# --- USER DASHBOARD ---
@app.get("/user/seller_dashboard.html")
async def seller_dashboard(request: Request):
    return templates.TemplateResponse(request=request, name="user/seller_dashboard.html")

# 4. API ROUTERS
app.include_router(api_router, prefix=settings.API_V1_STR)
app.include_router(products.router, prefix="/api/products")

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)