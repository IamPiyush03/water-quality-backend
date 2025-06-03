from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.models import Base
from database.config import DATABASE_URL

def init_db():
    # Create database engine
    engine = create_engine(DATABASE_URL)
    
    # Create all tables
    Base.metadata.create_all(engine)
    
    # Create session factory
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    return SessionLocal()

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully!") 