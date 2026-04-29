import requests
import time
from datetime import datetime


def fetch_top_flights_calendar(api_key, month_str, top_n=4):
    url = "https://sky-scrapper.p.rapidapi.com/api/v1/flights/getPriceCalendar"
    headers = {
        "x-rapidapi-key": api_key,
        "x-rapidapi-host": "sky-scrapper.p.rapidapi.com"
    }

    year, month = map(int, month_str.split('-'))
    first_day_of_month = f"{year}-{month:02d}-01"

    try:
        res_out = requests.get(url, headers=headers, params={
            "originSkyId": "MAD", "destinationSkyId": "LPA",
            "fromDate": first_day_of_month, "currency": "EUR"
        })
        print(f"DEBUG: Status API: {res_out.status_code}")

        if res_out.status_code != 200:
            print(f"DEBUG: Respuesta error: {res_out.text}")

        print("Esperando 15 segundos para la siguiente consulta...")
        time.sleep(15)

        res_ret = requests.get(url, headers=headers, params={
            "originSkyId": "LPA", "destinationSkyId": "MAD",
            "fromDate": first_day_of_month, "currency": "EUR"
        })

        if res_out.status_code != 200 or res_ret.status_code != 200:
            return []

        data_out = res_out.json().get('data', {}).get('flights', {}).get('days', [])
        data_ret = res_ret.json().get('data', {}).get('flights', {}).get('days', [])

        if not data_out or not data_ret:
            return []

        out_prices = {d['day']: d['price'] for d in data_out if 'price' in d and d['price'] is not None}
        ret_prices = {d['day']: d['price'] for d in data_ret if 'price' in d and d['price'] is not None}

        all_flights = []
        for out_date_str, out_price in out_prices.items():
            if not out_date_str.startswith(month_str): continue
            out_dt = datetime.strptime(out_date_str, "%Y-%m-%d")

            for ret_date_str, ret_price in ret_prices.items():
                if not ret_date_str.startswith(month_str): continue
                ret_dt = datetime.strptime(ret_date_str, "%Y-%m-%d")

                if ret_dt > out_dt:
                    total_price = out_price + ret_price
                    link = f"https://www.skyscanner.es/transport/flights/mad/lpa/{out_date_str[2:4]}{out_date_str[5:7]}{out_date_str[8:10]}/{ret_date_str[2:4]}{ret_date_str[5:7]}{ret_date_str[8:10]}/"
                    all_flights.append(
                        {"price": total_price, "outbound": out_date_str, "return": ret_date_str, "link": link})

        all_flights = sorted(all_flights, key=lambda x: x['price'])
        return all_flights[:top_n]
    except Exception as e:
        print(f"Error: {e}")
        return []


def send_telegram_alert(bot_token, chat_id, best_flight, month_name, avg_price, drop_amount):
    # Texto dinámico según si ha bajado de la media o no
    if drop_amount > 0:
        status_icon = "📉"
        trend_text = f"¡Está {drop_amount:.2f}€ más barato que la media!"
    elif drop_amount < 0:
        status_icon = "📈"
        trend_text = f"Ha subido {abs(drop_amount):.2f}€ respecto a la media."
    else:
        status_icon = "📊"
        trend_text = "Primer análisis del mes."

    message = (
        f"✈️ REPORTE DE VUELOS: {month_name} ✈️\n\n"
        f"{status_icon} {trend_text}\n"
        f"Media histórica: {avg_price:.2f}€\n\n"
        f"🔥 MEJOR OPCIÓN ACTUAL: {best_flight['price']}€ 🔥\n"
        f"🛫 Ida: {best_flight['outbound']}\n"
        f"🛬 Vuelta: {best_flight['return']}\n\n"
        f"🔗 Enlace directo a Skyscanner:\n{best_flight['link']}"
    )
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    requests.post(url, json={"chat_id": chat_id, "text": message})