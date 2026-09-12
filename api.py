from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from engine import Order, OrderBook, Side
import uuid

app = FastAPI(title="VIAMAG Trading Engine")
book = OrderBook()


# Pydantic model for incoming JSON requests
class OrderRequest(BaseModel):
    side: str
    price: int
    quantity: int


@app.post("/order")
async def place_order(order_req: OrderRequest):
    if order_req.side.upper() not in ["BUY", "SELL"]:
        raise HTTPException(status_code=400, detail="Side must be BUY or SELL")

    # Generate a unique order ID
    order_id = f"{order_req.side.lower()}_{uuid.uuid4().hex[:8]}"
    side_enum = Side.BUY if order_req.side.upper() == "BUY" else Side.SELL

    order = Order(order_id=order_id, side=side_enum, price=order_req.price, quantity=order_req.quantity)

    # Execute against the order book
    trades = book.match_order(order)

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