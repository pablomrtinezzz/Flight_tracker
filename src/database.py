import sqlite3
import os
from datetime import datetime
from typing import List, Tuple, Optional

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
os.makedirs(DATA_DIR, exist_ok=True)
DB_NAME = os.path.join(DATA_DIR, "flights.db")

def init_db() -> None:
    # Usar 'with' asegura que la conexión se cierra y hace commit automáticamente
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS historical_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME,
                target_month TEXT,
                avg_price REAL,
                min_price REAL
            )
        ''')
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

def save_search_stats(month: str, avg_price: float, min_price: float) -> None:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO historical_stats (timestamp, target_month, avg_price, min_price) VALUES (?, ?, ?, ?)',
                       (timestamp, month, avg_price, min_price))

def save_top_flights(month: str, flights: List[dict]) -> None:
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM current_top_flights WHERE target_month = ?', (month,))
        for rank, flight in enumerate(flights, start=1):
            cursor.execute('''
                INSERT INTO current_top_flights (target_month, rank, price, outbound_date, return_date, link)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (month, rank, flight['price'], flight['outbound'], flight['return'], flight['link']))

def get_historical_average(month: str) -> Optional[float]:
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT AVG(avg_price) FROM historical_stats WHERE target_month = ?', (month,))
        result = cursor.fetchone()[0]
    return result if result else None

def get_all_stats() -> List[Tuple]:
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT timestamp, target_month, avg_price, min_price FROM historical_stats ORDER BY timestamp DESC')
        data = cursor.fetchall()
    return data

def get_current_top_flights(month: str) -> List[Tuple]:
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT rank, price, outbound_date, return_date, link FROM current_top_flights WHERE target_month = ? ORDER BY rank ASC', (month,))
        data = cursor.fetchall()
    return data