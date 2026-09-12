import sqlite3
from datetime import datetime
from risk import analyze_spoofing_risk

DB_NAME = "mags_trading.db"


def generate_tear_sheet():
    print("Gathering session data from database...")
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Calculate session metrics
    cursor.execute("SELECT SUM(quantity), SUM(price * quantity), COUNT(*) FROM trades")
    result = cursor.fetchone()

    total_volume = result[0] or 0
    total_value = result[1] or 0
    trade_count = result[2] or 0
    vwap = (total_value / total_volume) if total_volume > 0 else 0

    conn.close()

    print("Running AI compliance check via Gemini...")
    risk_report = analyze_spoofing_risk()
    risk_text = risk_report.get("analysis", "No risk analysis available.")

    # Format the report
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    report_content = f"""
========================================
MaGs Trading Engine - Session Tear Sheet
========================================
Generated: {timestamp}

--- SESSION METRICS ---
Total Trades Executed : {trade_count}
Total Volume (Shares) : {total_volume}
Total Traded Value    : ${total_value:,.2f}
Session VWAP          : ${vwap:,.2f}

--- AI COMPLIANCE & RISK ASSESSMENT ---
{risk_text}

========================================
End of Report
========================================
"""

    # Write to a text file
    filename = f"session_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(filename, "w") as f:
        f.write(report_content.strip())

    print(f"Success! Session Tear Sheet saved locally as: {filename}")


if __name__ == "__main__":
    generate_tear_sheet()