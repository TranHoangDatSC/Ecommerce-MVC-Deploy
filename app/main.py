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

# 1. Cấu hình đường dẫn tuyệt đối (Để Render không lạc đường)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Templates thường nằm cùng cấp với main.py trong thư mục app
template_path = os.path.join(BASE_DIR, "templates")
# Tìm thư mục templates bằng mọi giá
possible_paths = [
    os.path.join(BASE_DIR, "templates"),           # Trường hợp: app/templates
    os.path.join(os.path.dirname(BASE_DIR), "templates"), # Trường hợp: templates (ở gốc)
    "/opt/render/project/src/app/templates",       # Đường dẫn cứng trên Render 1
    "/opt/render/project/src/templates"            # Đường dẫn cứng trên Render 2
]

template_path = None
for path in possible_paths:
    if os.path.exists(path):
        template_path = path
        break

if not template_path:
    # Nếu vẫn không thấy, ép nó về thư mục hiện tại để tránh crash
    template_path = os.path.join(BASE_DIR, "templates")

templates = Jinja2Templates(directory=template_path)
print(f"--- TEMPLATE PATH BEING USED: {template_path} ---")

# --- 🛠️ DATABASE SETUP ---
def create_tables():
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully.")

def initialize_database():
    create_tables() 
    try:
        db = SessionLocal()
        init_db(db)
    except Exception as e:
        print(f"Lỗi khởi tạo DB: {e}")
    finally:
        if 'db' in locals() and db:
            db.close() 

# --- KHỞI TẠO APP FASTAPI ---
app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

# 2. Cấu hình Static Files (XÓA BỎ MOUNT TEMPLATES)
# CSS, JS hệ thống
static_app_path = os.path.join(BASE_DIR, "static")
if os.path.exists(static_app_path):
    app.mount("/app_static", StaticFiles(directory=static_app_path), name="static_app")

# Ảnh sản phẩm (Nằm ở gốc dự án)
root_static = os.path.join(os.path.dirname(BASE_DIR), "static") 
if os.path.exists(root_static):
    app.mount("/static", StaticFiles(directory=root_static), name="static_root")

# --- 🚀 ROUTES RENDER FRONTEND (ĐÃ SỬA LỖI KEYWORD ARGUMENTS) ---

@app.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse(name="index.html", context={"request": request})

@app.get("/cart")
async def cart_page(request: Request):
    return templates.TemplateResponse(name="cart.html", context={"request": request})

@app.get("/shop")
async def shop_page(request: Request):
    return templates.TemplateResponse(name="shop.html", context={"request": request})

@app.get("/details")
async def details_page(request: Request):
    return templates.TemplateResponse(name="details.html", context={"request": request})

# Router Dashboard Người dùng:
@app.get("/user/seller_dashboard.html")
async def seller_dashboard_page(request: Request):
    return templates.TemplateResponse(name="user/seller_dashboard.html", context={"request": request})

# Router Dashboard Moderator:
@app.get("/moderator/moderator_dashboard.html")
async def moderator_dashboard(request: Request):
    return templates.TemplateResponse(name="moderator/moderator_dashboard.html", context={"request": request})

@app.get("/moderator/moderator_products.html")
async def moderator_product_page(request: Request):
    return templates.TemplateResponse(name="moderator/moderator_products.html", context={"request": request})

@app.get("/moderator/moderator_users.html")
async def moderator_users_page(request: Request):
    return templates.TemplateResponse(name="moderator/moderator_users.html", context={"request": request})

@app.get("/moderator/moderator_profile.html")
async def moderator_profile_page(request: Request):
    return templates.TemplateResponse(name="moderator/moderator_profile.html", context={"request": request})

# Router Dashboard Admin:
@app.get("/admin/dashboard_admin.html")
async def admin_dashboard(request: Request):
    return templates.TemplateResponse(name="admin/dashboard_admin.html", context={"request": request})

@app.get("/admin/admin_moderators.html")
async def admin_moderators_page(request: Request):
    return templates.TemplateResponse(name="admin/admin_moderators.html", context={"request": request})

@app.get("/admin/admin_users.html")
async def admin_users_page(request: Request): 
    return templates.TemplateResponse(name="admin/admin_users.html", context={"request": request})

@app.get("/admin/admin_categories.html")
async def admin_categories_page(request: Request): 
    return templates.TemplateResponse(name="admin/admin_categories.html", context={"request": request})

@app.get("/admin/admin_products.html")
async def admin_products_page(request: Request): 
    return templates.TemplateResponse(name="admin/admin_products.html", context={"request": request})

@app.get("/admin/admin_profile.html")
async def admin_profile_page(request: Request): 
    return templates.TemplateResponse(name="admin/admin_profile.html", context={"request": request})

# --- ROUTER API ---
app.include_router(api_router, prefix=settings.API_V1_STR)
app.include_router(products.router, prefix="/api/products")

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)