import sqlite3
import os
from dotenv import load_dotenv
from google import genai

# Load the secret key from the .env file
load_dotenv()

DB_NAME = "mags_trading.db"

# Initialize the Gemini client securely
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))


def analyze_spoofing_risk():
    """Fetches recent trades and sends them to Gemini to detect market manipulation."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Grab the last 50 trades for pattern analysis
    cursor.execute("""
        SELECT maker_order_id, taker_order_id, price, quantity, timestamp 
        FROM trades 
        ORDER BY timestamp DESC LIMIT 50
    """)
    trades = cursor.fetchall()
    conn.close()

    if not trades:
        return {"status": "no_data", "analysis": "Not enough trade data to analyze risk."}

    # Format the data into an LLM-readable prompt
    trade_log = "\n".join(
        [f"Time: {t[4]} | Maker: {t[0]} | Taker: {t[1]} | Price: {t[2]} | Qty: {t[3]}" for t in trades])

    prompt = f"""
    You are a quantitative risk compliance officer. Analyze the following recent trade executions for a Limit Order Book. 
    Look for signs of market manipulation, such as 'wash trading' (similar maker and taker profiles interacting repeatedly) or suspicious micro-bursts of volume.

    Recent Trades:
    {trade_log}

    Provide a brief, 2-3 sentence risk assessment.
    """

    # Calling the live Gemini model
    response = client.models.generate_content(
        model='gemini-3.6-flash',
        contents=prompt
    )

    return {
        "status": "success",
        "analysis": response.text,
        #"prompt_preview": prompt
    }