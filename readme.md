# 🛫 Flight Tracker: Automated Pricing Intelligence

[![Python](https://img.shields.io/badge/Python-3.10-blue.svg)](https://www.python.org/)
[![Automation](https://img.shields.io/badge/CI%2FCD-GitHub%20Actions-2088FF.svg)]()
[![Frontend](https://img.shields.io/badge/Dashboard-Streamlit-FF4B4B.svg)](https://streamlit.io/)

> **Value Proposition**: A fully autonomous data engineering pipeline that tracks flight prices, calculates historical averages to detect real discounts, stores data in a persistent SQLite database, and alerts stakeholders via Telegram.

---

## 🏗️ System Architecture & Workflow

This project leverages a zero-cost serverless architecture:
1. **Cronjob Orchestration**: GitHub Actions triggers the extraction script every week automatically.
2. **Data Ingestion Layer**: Connects to the Sky-Scrapper API to fetch raw pricing data for targeted routes (e.g., MAD ⇄ LPA).
3. **Data Processing**: Computes total round-trip pricing and compares the lowest available price against the historical moving average to evaluate true discount value.
4. **Persistence (The Hack)**: The SQLite database (`flights.db`) is committed back to the repository by the GitHub Action Bot, ensuring persistent tracking without requiring external DB hosting.
5. **Alerting System**: Real-time push notifications are sent via the Telegram Bot API.

---

## 📊 Analytics Dashboard

A Streamlit frontend translates the SQL data into actionable insights:
* **KPI Tracking**: Compares the absolute minimum price with the historical average.
* **Trend Visualization**: Multi-line charts displaying price variance over time.
* **Actionable Tables**: Renders the "Top 4" active flights with direct booking links.

**Run the Dashboard locally:**
streamlit run app.py
⚙️ Environment Configuration
To run or deploy this pipeline, you need the following API keys securely stored in your .env file (or GitHub Repository Secrets for production):

```bash
RAPIDAPI_KEY=your_sky_scrapper_key
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_chat_id
DISCOUNT_THRESHOLD=20.0
```

## 🚀 Local Execution & Testing

To test the pipeline on your local machine, the project is divided into two executable components:

### 1. Run the Data Extraction Engine
This script manually triggers the ETL process. It will fetch the latest prices from the RapidAPI endpoint, calculate the historical variations, save the results into the local SQLite database (`data/flights.db`), and dispatch a Telegram alert.

```bash
python src/tracker.py
```

Note: Ensure your .env file is properly configured with your API credentials before running this command.

2. Launch the Analytics Dashboard
Once the database is populated, you can visualize the historical trends and the current top 4 flights using the Streamlit frontend.

Bash
streamlit run app.py
The dashboard will automatically open in your default web browser at http://localhost:8501.
# 🛠️ Code Standards
**Reliability:** Implemented Context Managers (with statements) to prevent database locks and corruption during unhandled exceptions.

**Traceability:** Swapped standard output for Python's native logging library for precise error tracking.

**Predictability:** Enforced strong typing (typing.Dict, typing.List) across all extraction functions.

**© Developed by Pablo Martínez Suárez**