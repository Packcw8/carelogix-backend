from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uuid
import os

from app.database import Base, engine, SessionLocal
from app.models import User, Agency
from app.models.forms import FormSubmission

from app.routers import register, login, protected
from app.routers import docgen
from app.routers.documents import router as document_router
from app.routers import forms

# ✅ Lifespan handler for startup tasks
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create database tables
    Base.metadata.create_all(bind=engine)

    # Preload agencies if they don't exist
    db = SessionLocal()
    agency_names = ["Bright Futures", "New Pathways", "Helping Hands"]
    for name in agency_names:
        if not db.query(Agency).filter_by(name=name).first():
            db.add(Agency(id=str(uuid.uuid4()), name=name))
    db.commit()
    db.close()

    yield  # Startup complete

# ✅ Initialize FastAPI with lifespan
app = FastAPI(lifespan=lifespan)

# ✅ Enable CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # adjust for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Serve generated DOCX files from /generated_docs
app.mount(
    "/generated_docs",
    StaticFiles(directory=os.path.join(os.path.dirname(__file__), "generated_docs")),
    name="generated_docs"
)

# ✅ Register all routers
app.include_router(register.router)
app.include_router(login.router)
app.include_router(protected.router)
app.include_router(docgen.router)
app.include_router(document_router)
app.include_router(forms.router)








