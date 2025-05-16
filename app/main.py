from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
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
from app.routers import clients
from app.routers import referrals
from app.routers import infield_notes
from app.routers import gpt_clean
from app.routers import summaries





@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    agency_names = ["Bright Futures", "New Pathways", "Helping Hands", "Uplifting Families"]
    for name in agency_names:
        if not db.query(Agency).filter_by(name=name).first():
            db.add(Agency(id=str(uuid.uuid4()), name=name))
    db.commit()
    db.close()
    yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # for local dev
        "https://carelogix-frontend.vercel.app",  # ✅ your deployed frontend
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(register.router)
app.include_router(login.router)
app.include_router(protected.router)
app.include_router(docgen.router)
app.include_router(document_router)
app.include_router(forms.router)
app.include_router(admin.router)
app.include_router(invoice_router)
app.include_router(clients.router)
app.include_router(referrals.router)
app.include_router(infield_notes.router)
app.include_router(gpt_clean.router)
app.include_router(summaries.router)


# ✅ Health check endpoint for both GET and HEAD
@app.api_route("/", methods=["GET", "HEAD"])
def read_root(request: Request):
    return JSONResponse(content={"status": "ok"})

print("🚀 FastAPI server is running and ready.")









