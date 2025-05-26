# core/database.py
import sqlite3
from contextlib import contextmanager

DATABASE = 'scans.db'

def init_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS scans
                 (scan_id INTEGER,
                  task_id TEXT PRIMARY KEY,
                  target TEXT, 
                  tool TEXT, 
                  status TEXT, 
                  results TEXT)''')
    conn.commit()
    conn.close()

def get_db_connection():
    return sqlite3.connect("scans.db")


# Initialize database on first run
init_db()
