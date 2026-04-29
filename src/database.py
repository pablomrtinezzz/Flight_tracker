import sqlite3
import os
from datetime import datetime

# Esto busca la carpeta 'data' subiendo un nivel desde 'src'
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
os.makedirs(DATA_DIR, exist_ok=True)
DB_NAME = os.path.join(DATA_DIR, "flights.db")

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # Tabla para las gráficas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS historical_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME,
            target_month TEXT,
            avg_price REAL,
            min_price REAL
        )
    ''')
    # Tabla para el Top 4 actual
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS current_top_flights (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            target_month TEXT,
            rank INTEGER,
            price REAL,
            outbound_date TEXT,
            return_date TEXT,
            link TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_search_stats(month, avg_price, min_price):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute('INSERT INTO historical_stats (timestamp, target_month, avg_price, min_price) VALUES (?, ?, ?, ?)',
                   (timestamp, month, avg_price, min_price))
    conn.commit()
    conn.close()

def save_top_flights(month, flights):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM current_top_flights WHERE target_month = ?', (month,))
    for rank, flight in enumerate(flights, start=1):
        cursor.execute('''
            INSERT INTO current_top_flights (target_month, rank, price, outbound_date, return_date, link)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (month, rank, flight['price'], flight['outbound'], flight['return'], flight['link']))
    conn.commit()
    conn.close()

def get_historical_average(month):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT AVG(avg_price) FROM historical_stats WHERE target_month = ?', (month,))
    result = cursor.fetchone()[0]
    conn.close()
    return result if result else None

def get_all_stats():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT timestamp, target_month, avg_price, min_price FROM historical_stats ORDER BY timestamp DESC')
    data = cursor.fetchall()
    conn.close()
    return data

def get_current_top_flights(month):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT rank, price, outbound_date, return_date, link FROM current_top_flights WHERE target_month = ? ORDER BY rank ASC', (month,))
    data = cursor.fetchall()
    conn.close()
    return data