import sqlite3
from datetime import datetime, timedelta

DB_NAME = "mags_trading.db"


def calculate_vwap():
    """Calculates the Volume-Weighted Average Price (VWAP) for the last 60 seconds."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # SQLite uses UTC for CURRENT_TIMESTAMP
    one_minute_ago = (datetime.utcnow() - timedelta(minutes=1)).strftime('%Y-%m-%d %H:%M:%S')

    cursor.execute("""
        SELECT price, quantity FROM trades 
        WHERE timestamp >= ?
    """, (one_minute_ago,))

    trades = cursor.fetchall()
    conn.close()

    timestamp = datetime.utcnow().strftime('%H:%M:%S')

    if not trades:
        print(f"[{timestamp} VWAP] No trades in the last minute.")
        return

    total_value = sum(price * qty for price, qty in trades)
    total_volume = sum(qty for _, qty in trades)

    vwap = total_value / total_volume
    print(f"[{timestamp} VWAP] Current VWAP: {vwap:.2f} | Volume: {total_volume}")