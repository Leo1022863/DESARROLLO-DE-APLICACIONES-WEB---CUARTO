import sqlite3
from sqlite3 import Error
from pathlib import Path
db_path = Path(__file__).parent / "data"/ 'ProyectoCEB.db'

def get_db_connection():
    db_path.parent.mkdir(parents=True, exist_ok=True)  # Ensure the directory exists
    conn = sqlite3.connect(db_path)
    return conn

def imit_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            descripcion TEXT,
            precio REAL NOT NULL,
            cantidad INTEGER NOT NULL
        )
    ''')
    conn.commit()
    conn.close()