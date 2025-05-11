from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uuid
import os

from app.database import Base, engine, SessionLocal
from app.models import User, Agency
from app.routers import register, login, protected, docgen, forms
from app.routers.documents import router as document_router
from app.routers import admin
from app.routers.invoice import router as invoice_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    agency_names = ["Bright Futures", "New Pathways", "Helping Hands"]
    for name in agency_names:
        if not db.query(Agency).filter_by(name=name).first():
            db.add(Agency(id=str(uuid.uuid4()), name=name))
    db.commit()
    db.close()
    yield

app = FastAPI(lifespan=lifespan)

# ✅ FIXED CORS CONFIG
origins = [
    "https://carelogix-frontend.vercel.app",  # ✅ your frontend domain
    "http://localhost:3000",                  # optional for local dev
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Include all routers
app.include_router(register.router)
app.include_router(login.router)
app.include_router(protected.router)
app.include_router(docgen.router)
app.include_router(document_router)
app.include_router(forms.router)
app.include_router(admin.router)
app.include_router(invoice_router)

print("🚀 FastAPI server is running and ready.")








