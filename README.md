# Matching Core Engine

A low-latency limit order book (LOB) and matching engine featuring O(1) execution, strict price-time priority, and automated AI compliance checks. Built for the final capstone of my FlyRank AI Internship.

## Architecture & Features

* **Core Engine:** O(1) limit order matching with strict price-time priority.
* **API Layer:** FastAPI for low-latency HTTP order ingestion and book retrieval.
* **Data Persistence:** Asynchronous SQLite database for trade logging.
* **Background Workers:** Isolated cron scheduler for non-blocking real-time VWAP calculations.
* **Risk & Compliance:** Live API integration with Google's gemini-3.6-flash for quantitative spoofing and wash-trading detection.
* **Reporting:** Automated session tear sheet generation summarizing trade volume, VWAP, and AI risk assessments.

## Quick Start Guide

**1. Install Dependencies**
```bash
pip install fastapi uvicorn google-genai python-dotenv
```

**2. Environment Setup**
Create a `.env` file in the root directory and add your Google Gemini API key:
```env
GEMINI_API_KEY=your_api_key_here
```

**3. Run the Engine**
```bash
uvicorn api:app --reload
```
*Access the Swagger UI at `http://127.0.0.1:8000/docs` to place limit orders and run live AI risk reports.*

**4. Generate Session Report**
```bash
python generate_report.py
```
*Run this at the end of a trading session to generate a `.txt` tear sheet.*

## Author

Maurya Govindu
