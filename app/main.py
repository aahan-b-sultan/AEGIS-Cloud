from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from app.core.config import settings
from app.models.user import User
from app.api.endpoints import radar, auth
from app.models.scan import ScanLog

# --- DATABASE IMPORTS ---
from app.db.session import engine, SessionLocal
from app.models.scan import Base
from app.core.security import get_password_hash

# CREATE TABLES ON STARTUP
Base.metadata.create_all(bind=engine)

# --- AUTO-ADMIN CREATION ---
def init_admin():
    db = SessionLocal()
    try:
        # Check if admin already exists
        admin = db.query(User).filter(User.username == "admin").first()
        if not admin:
            print("👤 Creating Default Admin User...")
            new_admin = User(
                username="admin",
                hashed_password=get_password_hash("admin123"), # Default password
                is_superuser=True
            )
            db.add(new_admin)
            db.commit()
            print("✅ Default Admin created (Username: admin | Password: admin123)")
        else:
            print("✅ Admin user already exists.")
    except Exception as e:
        print(f"❌ Error creating admin: {e}")
    finally:
        db.close()

# Run the function immediately after tables are created
init_admin()
# ------------------------

import zipfile
import os

# --- EXTRACT DATA LAKE ZIP ---
DATA_LAKE_ZIP = "data_lake.zip"
DATA_LAKE_DIR = "data_lake"

if os.path.exists(DATA_LAKE_ZIP) and not os.path.exists(DATA_LAKE_DIR):
    print("Extracting Data Lake...")
    with zipfile.ZipFile(DATA_LAKE_ZIP, 'r') as zip_ref:
        zip_ref.extractall(".")
    print("Extraction complete.")
# -----------------------------

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="2.0.0"
)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
app.include_router(radar.router, prefix="/api/v1/radar", tags=["Radar Control"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])

# Removed duplicate radar.router inclusion

# 1. NEW ROOT ROUTE (Landing Page)
@app.get("/", response_class=HTMLResponse)
async def landing_page(request: Request):
    return templates.TemplateResponse(request=request, name="welcome.html")

# 2. LOGIN ROUTE (Already exists, ensure it's there)
@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse(request=request, name="login.html")

# 3. CHANGED DASHBOARD ROUTE (Now at /dashboard)
@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

if __name__ == "__main__":
    import uvicorn
    # Make sure this is set to 7860 to match your local testing with the Dockerfile
    uvicorn.run("app.main:app", host="127.0.0.1", port=7860, reload=True)