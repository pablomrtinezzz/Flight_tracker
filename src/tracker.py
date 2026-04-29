import os
import sys
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import init_db, save_search_stats, save_top_flights, get_historical_average
from api_tools import fetch_top_flights_calendar, send_telegram_alert

load_dotenv()

API_KEY = os.getenv("RAPIDAPI_KEY")
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
# Mantenemos el threshold por si quieres usarlo en el futuro, pero ahora mandará siempre
DISCOUNT_THRESHOLD = float(os.getenv("DISCOUNT_THRESHOLD", 20.0))

MONTHS = {"Julio 2026": "2026-07", "Agosto 2026": "2026-08"}


def run_tracker():
    print("🚀 Iniciando rastreo total...")
    for name, date_code in MONTHS.items():
        print(f"Analizando {name}...")
        top_flights = fetch_top_flights_calendar(API_KEY, date_code, top_n=4)

        if not top_flights:
            print(f"❌ Sin datos para {name}")
            continue

        # 1. Calculamos métricas para el histórico (Gráficas)
        min_price = top_flights[0]['price']
        batch_avg = sum(f['price'] for f in top_flights) / len(top_flights)
        global_avg = get_historical_average(name)

        # 2. Guardamos TODO en la base de datos
        save_search_stats(name, batch_avg, min_price)  # Para la gráfica
        save_top_flights(name, top_flights)  # Los 4 mejores actuales

        # 3. Enviamos mensaje de Telegram SIEMPRE
        # Calculamos la diferencia con la media solo para informar en el mensaje
        drop = (global_avg - min_price) if global_avg else 0

        print(f"📤 Enviando reporte de {name} a Telegram...")
        send_telegram_alert(BOT_TOKEN, CHAT_ID, top_flights[0], name, (global_avg or batch_avg), drop)


if __name__ == "__main__":
    init_db()
    run_tracker()