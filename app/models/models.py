from sqlalchemy import Column, String, Boolean, ForeignKey, Integer, Float, Date, DateTime, JSON
from sqlalchemy.orm import relationship
from app.database import Base
import uuid
from datetime import datetime


class Agency(Base):
    __tablename__ = "agencies"
    id = Column(String, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    users = relationship("User", back_populates="agency")


class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    full_name = Column(String)
    agency_id = Column(String, ForeignKey("agencies.id"))
    is_admin = Column(Boolean, default=False)
    pay_tier = Column(String, default="Tier 1")

    agency = relationship("Agency", back_populates="users")
    clients = relationship("Client", back_populates="user", cascade="all, delete")
    referrals = relationship("Referral", back_populates="user", cascade="all, delete")
    invoices = relationship("Invoice", back_populates="user", cascade="all, delete")  # ✅ Add this line
 # ✅ REQUIRED


from sqlalchemy import Column, Integer, String

class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)
    case_name = Column(String, nullable=False)
    case_number = Column(String, nullable=False)
    client_number = Column(String, nullable=True)

    # Allow nullable fields
    case_worker = Column(String, nullable=True)
    worker_email = Column(String, nullable=True)
    address = Column(String, nullable=True)
    phone_number = Column(String, nullable=True)
    participants = Column(String, nullable=True)




class Referral(Base):
    __tablename__ = "referrals"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    filename = Column(String, nullable=False)
    s3_key = Column(String, nullable=False)
    note = Column(String, nullable=True)

    user = relationship("User", back_populates="referrals")

class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    start_date = Column(Date)
    end_date = Column(Date)
    total = Column(Float)
    data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="invoices")
