from sqlalchemy import create_engine, Column, Float
from sqlalchemy.sql import text
from database.config import SQLALCHEMY_DATABASE_URL

def add_location_columns():
    """Add latitude and longitude columns to water_quality_measurements table"""
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    
    with engine.connect() as connection:
        # Check if columns exist
        result = connection.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'water_quality_measurements' 
            AND column_name IN ('latitude', 'longitude')
        """))
        existing_columns = [row[0] for row in result]
        
        # Add latitude column if it doesn't exist
        if 'latitude' not in existing_columns:
            connection.execute(text("""
                ALTER TABLE water_quality_measurements 
                ADD COLUMN latitude FLOAT
            """))
            print("Added latitude column")
        
        # Add longitude column if it doesn't exist
        if 'longitude' not in existing_columns:
            connection.execute(text("""
                ALTER TABLE water_quality_measurements 
                ADD COLUMN longitude FLOAT
            """))
            print("Added longitude column")
        
        connection.commit()
        print("Migration completed successfully")

if __name__ == "__main__":
    add_location_columns() 