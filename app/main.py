from fastapi.responses import HTMLResponse
import uvicorn
import os
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.core.database import engine, Base
from app.models import sqlmodels 
from app.initial_data import init_db
from app.core.database import SessionLocal 
from app.api.base import api_router
from app.api.endpoints import auth, products, categories

# 1. TÌM ĐƯỜNG DẪN TEMPLATES (FIX LỖI MÙ ĐƯỜNG DẪN TRÊN RENDER)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
possible_paths = [
    os.path.join(BASE_DIR, "templates"),
    os.path.join(os.path.dirname(BASE_DIR), "templates"),
    "/opt/render/project/src/app/templates",
    "/opt/render/project/src/templates"
]

template_path = next((path for path in possible_paths if os.path.exists(path)), os.path.join(BASE_DIR, "templates"))
templates = Jinja2Templates(directory=template_path)
print(f"--- TEMPLATE PATH ACTIVE: {template_path} ---")

# --- DATABASE SETUP ---
def create_tables():
    Base.metadata.create_all(bind=engine)

def initialize_database():
    create_tables() 
    try:
        db = SessionLocal()
        init_db(db)
    except Exception as e:
        print(f"DB Error: {e}")
    finally:
        if 'db' in locals() and db: db.close() 

# --- KHỞI TẠO APP ---
app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

# 2. CẤU HÌNH STATIC FILES (CHỈ MOUNT FILE TĨNH, KHÔNG MOUNT TEMPLATES)
static_app_path = os.path.join(BASE_DIR, "static")
if os.path.exists(static_app_path):
    app.mount("/app_static", StaticFiles(directory=static_app_path), name="static_app")

root_static = os.path.join(os.path.dirname(BASE_DIR), "static") 
if os.path.exists(root_static):
    app.mount("/static", StaticFiles(directory=root_static), name="static_root")

# --- 🚀 ROUTES FRONTEND (FIX TRIỆT ĐỂ LỖI TYPEERROR/MISSING ARGUMENT) ---

@app.get("/")
async def read_root(request: Request):
    # BẮT BUỘC: request phải là tham số đầu tiên, không nằm trong context dict
    return templates.TemplateResponse(request=request, name="index.html")

@app.get("/cart")
async def cart_page(request: Request):
    return templates.TemplateResponse(request=request, name="cart.html")

@app.get("/shop")
async def shop_page(request: Request):
    return templates.TemplateResponse(request=request, name="shop.html")

@app.get("/details")
async def details_page(request: Request):
    return templates.TemplateResponse(request=request, name="details.html")

# --- USER DASHBOARD ---
@app.get("/user/seller_dashboard.html")
async def seller_dashboard_page(request: Request):
    return templates.TemplateResponse(request=request, name="user/seller_dashboard.html")

# --- MODERATOR DASHBOARD ---
@app.get("/moderator/moderator_dashboard.html")
async def moderator_dashboard(request: Request):
    return templates.TemplateResponse(request=request, name="moderator/moderator_dashboard.html")

@app.get("/moderator/moderator_products.html")
async def moderator_product_page(request: Request):
    return templates.TemplateResponse(request=request, name="moderator/moderator_products.html")

@app.get("/moderator/moderator_users.html")
async def moderator_users_page(request: Request):
    return templates.TemplateResponse(request=request, name="moderator/moderator_users.html")

@app.get("/moderator/moderator_profile.html")
async def moderator_profile_page(request: Request):
    return templates.TemplateResponse(request=request, name="moderator/moderator_profile.html")

# --- ADMIN DASHBOARD ---
@app.get("/admin/dashboard_admin.html")
async def admin_dashboard(request: Request):
    return templates.TemplateResponse(request=request, name="admin/dashboard_admin.html")

@app.get("/admin/admin_moderators.html")
async def admin_moderators_page(request: Request):
    return templates.TemplateResponse(request=request, name="admin/admin_moderators.html")

@app.get("/admin/admin_users.html")
async def admin_users_page(request: Request): 
    return templates.TemplateResponse(request=request, name="admin/admin_users.html")

@app.get("/admin/admin_categories.html")
async def admin_categories_page(request: Request): 
    return templates.TemplateResponse(request=request, name="admin/admin_categories.html")

@app.get("/admin/admin_products.html")
async def admin_products_page(request: Request): 
    return templates.TemplateResponse(request=request, name="admin/admin_products.html")

@app.get("/admin/admin_profile.html")
async def admin_profile_page(request: Request): 
    return templates.TemplateResponse(request=request, name="admin/admin_profile.html")

# --- ROUTER API ---
app.include_router(api_router, prefix=settings.API_V1_STR)
app.include_router(products.router, prefix="/api/products")

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)