import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Database connection parameters
DB_USER = 'postgres'
DB_PASSWORD = 'ronin01'
DB_HOST = 'localhost'
DB_PORT = '5432'
DB_NAME = 'water_quality'

# Connect to PostgreSQL server
conn = psycopg2.connect(
    user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT
)

# Set isolation level to autocommit
conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

# Create a cursor
cur = conn.cursor()

# Create the database
cur.execute(f'CREATE DATABASE {DB_NAME}')

# Close the cursor and connection
cur.close()
conn.close()

print(f"Database '{DB_NAME}' created successfully!") 