from init_db import init_db
from seed_data import seed_database
from database.migrations import add_location_columns
from database.config import engine
from database.models import Base

def setup_database():
    """Initialize and seed the database"""
    print("Dropping all existing tables...")
    Base.metadata.drop_all(bind=engine)
    
    print("Initializing database tables...")
    init_db()
    
    print("Running database migrations...")
    add_location_columns()
    
    print("Seeding database with sample data...")
    seed_database()
    
    print("Database setup completed successfully!")

if __name__ == "__main__":
    setup_database() 