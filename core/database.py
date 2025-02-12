# core/database.py
import sqlite3
from contextlib import contextmanager

DATABASE = 'scans.db'

def init_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS scans
                 (id TEXT PRIMARY KEY, 
                  target TEXT, 
                  tool TEXT, 
                  status TEXT, 
                  results TEXT)''')
    conn.commit()
    conn.close()

@contextmanager
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    try:
        yield conn
    finally:
        conn.close()

# Initialize database on first run
init_db()
