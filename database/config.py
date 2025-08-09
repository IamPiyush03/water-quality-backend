from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
from urllib.parse import quote_plus

# Load environment variables
load_dotenv()

# Get database configuration from environment variables
# For Render deployment, use DATABASE_URL if available, otherwise use individual components
DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    # Render provides DATABASE_URL in format: postgresql://user:password@host:port/database
    SQLALCHEMY_DATABASE_URL = DATABASE_URL
else:
    # Fallback to individual environment variables for local development
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "Marsmission@11")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5433")
    DB_NAME = os.getenv("DB_NAME", "water_quality")
    
    # Create database URL with encoded password
    SQLALCHEMY_DATABASE_URL = f"postgresql://{DB_USER}:{quote_plus(DB_PASSWORD)}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Create engine
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 