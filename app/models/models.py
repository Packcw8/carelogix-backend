from sqlalchemy import Column, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

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
    pay_tier = Column(String, default="Tier 1")  # 👈 Add this line
    agency = relationship("Agency", back_populates="users")


class Client(Base):
    __tablename__ = "clients"
    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"))
    case_name = Column(String)
    case_number = Column(String)
    client_number = Column(String)

    user = relationship("User", back_populates="clients")
