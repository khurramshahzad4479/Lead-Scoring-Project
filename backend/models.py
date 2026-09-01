import os
from dotenv import load_dotenv

load_dotenv()

# Separate parameters - from .env file for better security and flexibility
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "postgres")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")

# Check if all values exist
if not DB_HOST or not DB_USER or not DB_PASS:
    print("❌ ERROR: .env file missing or incomplete!")
    print("Please check .env file has: DB_HOST, DB_USER, DB_PASS")
    DB_HOST = DB_HOST or "localhost"
    DB_USER = DB_USER or "postgres"
    DB_PASS = DB_PASS or "password"

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Boolean, BigInteger
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from datetime import datetime

DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}?sslmode=require&connect_timeout=30"
print(f"🔗 Connecting to: {DB_HOST}...")

engine = create_engine(DATABASE_URL, pool_pre_ping=True, pool_recycle=300)
Base = declarative_base()

class Lead(Base):
    __tablename__ = "leads"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    source = Column(String(50), default="Website")
    budget = Column(Float, default=0.0)
    is_converted = Column(Boolean, default=False)
    location = Column(String(255))
    lead_origin = Column(String(255))
    total_visits = Column(Integer, default=0)
    time_spent = Column(Integer, default=0)
    page_views = Column(Float, default=0.0)
    occupation = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    interactions = relationship("Interaction", back_populates="lead", cascade="all, delete-orphan")

class Interaction(Base):
    __tablename__ = "interactions"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    interaction_type = Column(String(255), nullable=False)
    notes = Column(String)
    lead_id = Column(BigInteger, ForeignKey("leads.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    lead = relationship("Lead", back_populates="interactions")

class User(Base):
    __tablename__ = "users"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    username = Column(String(255), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)