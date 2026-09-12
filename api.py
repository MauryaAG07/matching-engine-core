from risk import analyze_spoofing_risk
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from contextlib import asynccontextmanager
from apscheduler.schedulers.background import BackgroundScheduler
from engine import Order, OrderBook, Side
from database import init_db, log_trades
from analytics import calculate_vwap
import uuid

# Initializing database on startup
init_db()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Boot up the background cron job
    scheduler = BackgroundScheduler()
    scheduler.add_job(calculate_vwap, 'interval', seconds=60)
    scheduler.start()

    yield  # The API runs while suspended here

    # Clean shutdown
    scheduler.shutdown()

app = FastAPI(title="MaGs Trading Engine", lifespan=lifespan)
book = OrderBook()

class OrderRequest(BaseModel):
    side: str
    price: int
    quantity: int

@app.post("/order")
async def place_order(order_req: OrderRequest, background_tasks: BackgroundTasks):
    if order_req.side.upper() not in ["BUY", "SELL"]:
        raise HTTPException(status_code=400, detail="Side must be BUY or SELL")

    order_id = f"{order_req.side.lower()}_{uuid.uuid4().hex[:8]}"
    side_enum = Side.BUY if order_req.side.upper() == "BUY" else Side.SELL

    order = Order(order_id=order_id, side=side_enum, price=order_req.price, quantity=order_req.quantity)

    # Execute against the order book in memory
    trades = book.match_order(order)

    # Send the DB write to a background worker
    if trades:
        background_tasks.add_task(log_trades, trades)

    return {
        "status": "accepted",
        "order_id": order_id,
        "remaining_quantity": order.quantity,
        "trades": trades
    }


@app.get("/book")
async def get_book():
    return {
        "best_bid": book.best_bid,
        "best_ask": book.best_ask
    }
@app.get("/risk")
async def get_risk_analysis():
    """Generates an LLM-powered market manipulation report."""
    return analyze_spoofing_risk()