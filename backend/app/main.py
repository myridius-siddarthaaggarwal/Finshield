from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.db.session import engine, Base, SessionLocal
from app.db.init_db import seed_database
from app.models.user import User

# Import routers
from app.api.v1.auth import router as auth_router
from app.api.v1.cases import router as cases_router
from app.api.v1.ai_assessment import router as ai_router
from app.api.v1.committee import router as committee_router
from app.api.v1.audit import router as audit_router
from app.api.v1.evaluation import router as evaluation_router
from app.api.v1.data_layer import router as data_layer_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure tables exist and seed if database is empty
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        user_count = db.query(User).count()
        if user_count == 0:
            print("[FinShield Startup] Database empty. Running seed_database()...")
            seed_database()
        else:
            print(f"[FinShield Startup] Database ready with {user_count} users.")
    finally:
        db.close()
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description="Enterprise Financial Crime Risk Assessment Workbench Backend API",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all for hackathon flexibility
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API v1 Routers
app.include_router(auth_router, prefix="/api/v1")
app.include_router(cases_router, prefix="/api/v1")
app.include_router(ai_router, prefix="/api/v1")
app.include_router(committee_router, prefix="/api/v1")
app.include_router(audit_router, prefix="/api/v1")
app.include_router(evaluation_router, prefix="/api/v1")
app.include_router(data_layer_router, prefix="/api/v1")

@app.get("/")
def root():
    return {
        "system": settings.PROJECT_NAME,
        "version": settings.PROJECT_VERSION,
        "status": "operational",
        "governed_data_layer": "Active (FATF/FCA/OCC/FinCEN 2026)",
        "docs_url": "/docs"
    }
