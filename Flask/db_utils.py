import psycopg2
from flask import current_app

def get_db_connection():
    """Establishes a new database connection."""
    conn = psycopg2.connect(current_app.config['POSTGRES_URL'])
    # Consider setting autocommit based on your transaction needs.
    # For many web apps, explicit commit/rollback per transaction is safer.
    # conn.autocommit = True 
    return conn