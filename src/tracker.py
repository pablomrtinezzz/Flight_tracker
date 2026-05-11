import os
import sys
import logging
from dotenv import load_dotenv

# Configuración profesional de Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import init_db, save_search_stats, save_top_flights, get_historical_average
from api_tools import fetch_top_flights_calendar, send_telegram_alert

load_dotenv()

API_KEY = os.getenv("RAPIDAPI_KEY", "")
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
DISCOUNT_THRESHOLD = float(os.getenv("DISCOUNT_THRESHOLD", 20.0))

MONTHS = {"Julio 2026": "2026-07", "Agosto 2026": "2026-08"}


def run_tracker() -> None:
    logger.info("🚀 Iniciando el proceso completo de rastreo de vuelos...")

    for name, date_code in MONTHS.items():
        logger.info(f"Analizando métricas para {name}...")
        top_flights = fetch_top_flights_calendar(API_KEY, date_code, top_n=4)

        if not top_flights:
            logger.warning(f"❌ Sin datos extraídos para {name}. Saltando...")
            continue

        # 1. Calculamos métricas para el histórico (Gráficas)
        min_price = top_flights[0]['price']
        batch_avg = sum(f['price'] for f in top_flights) / len(top_flights)
        global_avg = get_historical_average(name)

        # 2. Guardamos TODO en la base de datos de forma segura
        logger.info(f"Guardando datos en la base de datos para {name}...")
        save_search_stats(name, batch_avg, min_price)
        save_top_flights(name, top_flights)

        # 3. Enviamos mensaje de Telegram
        drop = (global_avg - min_price) if global_avg else 0
        logger.info(f"📤 Enviando reporte a Telegram para {name}...")
        send_telegram_alert(BOT_TOKEN, CHAT_ID, top_flights[0], name, (global_avg or batch_avg), drop)

    logger.info("✅ Pipeline de extracción finalizado con éxito.")


if __name__ == "__main__":
    init_db()
    run_tracker()