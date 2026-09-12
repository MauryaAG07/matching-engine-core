import sqlite3

DB_NAME = "mags_trading.db"


def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Create a table for executed trades
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            maker_order_id TEXT,
            taker_order_id TEXT,
            price INTEGER,
            quantity INTEGER,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


def log_trades(trades: list[dict]):
    """Logs a batch of trades into the database."""
    if not trades:
        return

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    for trade in trades:
        cursor.execute("""
            INSERT INTO trades (maker_order_id, taker_order_id, price, quantity)
            VALUES (?, ?, ?, ?)
        """, (trade['maker_order_id'], trade['taker_order_id'], trade['price'], trade['quantity']))

    conn.commit()
    conn.close()