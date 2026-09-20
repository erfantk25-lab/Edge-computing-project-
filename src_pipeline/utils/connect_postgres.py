import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
DB_HOST = os.getenv("DB_HOST", "localhost") 
DB_PORT = os.getenv("DB_PORT", "5432")
DB_SSLMODE = os.getenv("DB_SSLMODE", "prefer") # 'require' for Azure, 'prefer' allows local non-SSL

DB_CONFIG = {
    "dbname": POSTGRES_DB,
    "user": POSTGRES_USER,
    "password": POSTGRES_PASSWORD,
    "host": DB_HOST,
    "port": DB_PORT,
    "sslmode": DB_SSLMODE,
}

def query_db(sql: str, parameters: tuple | None = None):
    """ Executes a SQL query and returns the result rows, or None. """
    
    conn = psycopg2.connect(**DB_CONFIG) 
    try:
        with conn:  # commits changes if block succeeds, rolls back if an exception is raised
            with conn.cursor() as cur:
                cur.execute(sql, parameters) # parameters passed separately -> protects against SQL injection
                return cur.fetchall() if cur.description else None
    except psycopg2.Error as e:
        print(f"Database error: {e}")
        raise
    finally:
        conn.close()