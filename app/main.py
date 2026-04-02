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
from fastapi import APIRouter
from app.api.endpoints import auth, products, categories

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

# --- 🛠️ HÀM TẠO BẢNG DATABASE (ĐƯỢC KÍCH HOẠT LẠI) ---
def create_tables():
    """Tạo tất cả các bảng dựa trên Base.metadata."""
    # Đảm bảo các models đã được import (như dòng 6) trước khi gọi Base.metadata.create_all
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully or already exist.")

# --- 🛠️ HÀM KHỞI TẠO DỮ LIỆU BAN ĐẦU (ĐƯỢC KÍCH HOẠT LẠI) ---
def initialize_database():
    """Tạo bảng và chèn dữ liệu khởi tạo."""
    create_tables() 
    try:
        db = SessionLocal()
        init_db(db)
        print("Initial data inserted successfully.")
    except Exception as e:
        # Lỗi này thường xảy ra nếu init_db được chạy nhiều lần.
        print(f"Lỗi khi khởi tạo DB/Dữ liệu ban đầu (có thể do dữ liệu đã tồn tại): {e}")
    finally:
        if 'db' in locals() and db:
            db.close() 

# Khởi tạo Database ngay khi module main.py được loade
# initialize_database()

# --- KHỞI TẠO APP FASTAPI ---
app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

# Cấu hình Static và Templates
# 1. Tài nguyên hệ thống (CSS, JS, Lib) - nằm trong app/static
if os.path.exists(os.path.join(BASE_DIR, "static")):
    app.mount("/app_static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static_app")

# 2. Dữ liệu người dùng/Ảnh sản phẩm - nằm ở root static
# Giữ cái này là /static để các đường dẫn ảnh trong DB không bị hỏng
root_static = os.path.join(os.path.dirname(BASE_DIR), "static") 
if os.path.exists(root_static):
    app.mount("/static", StaticFiles(directory=root_static), name="static_root")

app.mount("/templates", StaticFiles(directory="app/templates"), name="templates")
@app.get("/")
def read_root(request: Request):
    """Render trang index.html."""
    return templates.TemplateResponse("index.html", {"request": request})
app.mount("/templates", StaticFiles(directory="app/templates"), name="templates")

@app.get("/cart") # Đổi đường dẫn
def cart_page(request: Request):
    return templates.TemplateResponse("cart.html", {"request": request})

@app.get("/shop") # Đổi đường dẫn
def shop_page(request: Request):
    return templates.TemplateResponse("shop.html", {"request": request})

@app.get("/details") # Đổi đường dẫn
def details_page(request: Request):
    return templates.TemplateResponse("details.html", {"request": request})

# Router Dashboard Người dùng Quản lý:
@app.get("/user/seller_dashboard.html", response_class=HTMLResponse)
async def seller_dashboard_page(request: Request):
    return templates.TemplateResponse("user/seller_dashboard.html", {"request": request})

# Router Dashboard Moderator:
@app.get("/moderator/moderator_dashboard.html", response_class=HTMLResponse)
async def moderator_dashboard(request: Request):
    """Phục vụ tệp HTML cho trang kiểm duyệt viên."""
    return templates.TemplateResponse("moderator/moderator_dashboard.html", {"request": request})
@app.get("/moderator/moderator_products.html", response_class=HTMLResponse)
async def moderator_product_page(request: Request):
    return templates.TemplateResponse("moderator/moderator_products.html", {"request": request})
@app.get("/moderator/moderator_users.html", response_class=HTMLResponse)
async def moderator_users_page(request: Request):
    return templates.TemplateResponse("moderator/moderator_users.html", {"request": request})
@app.get("/moderator/moderator_profile.html", response_class=HTMLResponse)
async def moderator_users_page(request: Request):
    return templates.TemplateResponse("moderator/moderator_profile.html", {"request": request})

# Router Dashboard Admin:
@app.get("/admin/dashboard_admin.html", response_class=HTMLResponse)
async def admin_dashboard(request: Request):
    """Phục vụ tệp HTML cho trang quản trị."""
    return templates.TemplateResponse("admin/dashboard_admin.html", {"request": request})

# Router Admin Quản lý các tài khoản:
@app.get("/admin/admin_moderators.html", response_class=HTMLResponse)
async def admin_moderators_page(request: Request):
    return templates.TemplateResponse("admin/admin_moderators.html", {"request": request})
@app.get("/admin/admin_users.html", response_class=HTMLResponse)
async def admin_users_page(request: Request): 
    return templates.TemplateResponse("admin/admin_users.html", {"request": request})
@app.get("/admin/admin_categories.html", response_class=HTMLResponse)
async def admin_users_page(request: Request): 
    return templates.TemplateResponse("admin/admin_categories.html", {"request": request})
@app.get("/admin/admin_products.html", response_class=HTMLResponse)
async def admin_users_page(request: Request): 
    return templates.TemplateResponse("admin/admin_products.html", {"request": request})
@app.get("/admin/admin_profile.html", response_class=HTMLResponse)
async def admin_users_page(request: Request): 
    return templates.TemplateResponse("admin/admin_profile.html", {"request": request})

# ROUTE CHÍNH
app.include_router(api_router, prefix=settings.API_V1_STR)
app.include_router(products.router, prefix="/api/products")

if __name__ == "__main__":
    # Đảm bảo uvicorn chạy đúng file app
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)