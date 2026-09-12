from dataclasses import dataclass
from collections import defaultdict, deque
from enum import Enum
from typing import Dict, Optional


class Side(Enum):
    BUY = "BUY"
    SELL = "SELL"


@dataclass
class Order:
    order_id: str
    side: Side
    price: int  # represented in ticks/cents to avoid float drift
    quantity: int


class OrderBook:
    def __init__(self):
        # Maps price levels to a queue of resting orders (O(1) lookups)
        self.bids: Dict[int, deque] = defaultdict(deque)
        self.asks: Dict[int, deque] = defaultdict(deque)

        # Track the top of the book for O(1) cross detection
        self.best_bid: Optional[int] = None
        self.best_ask: Optional[int] = None

    def add_resting_order(self, order: Order):
        """Adds an order to the book without attempting to match it yet."""
        if order.side == Side.BUY:
            self.bids[order.price].append(order)
            if self.best_bid is None or order.price > self.best_bid:
                self.best_bid = order.price
        else:
            self.asks[order.price].append(order)
            if self.best_ask is None or order.price < self.best_ask:
                self.best_ask = order.price

    def match_order(self, incoming_order: Order) -> list[dict]:
        """Matches an incoming order against the resting order book."""
        trades = []

        if incoming_order.side == Side.BUY:
            # While the incoming buy price is >= the best ask, we have a cross
            while self.best_ask is not None and incoming_order.price >= self.best_ask and incoming_order.quantity > 0:
                best_ask_queue = self.asks[self.best_ask]

                while best_ask_queue and incoming_order.quantity > 0:
                    resting_order = best_ask_queue[0]

                    # Calculate execution quantity
                    traded_quantity = min(incoming_order.quantity, resting_order.quantity)

                    # Record the trade
                    trades.append({
                        "maker_order_id": resting_order.order_id,
                        "taker_order_id": incoming_order.order_id,
                        "price": resting_order.price,
                        "quantity": traded_quantity
                    })

                    # Decrement quantities
                    incoming_order.quantity -= traded_quantity
                    resting_order.quantity -= traded_quantity

                    # Remove the resting order if it's fully filled (O(1) popleft)
                    if resting_order.quantity == 0:
                        best_ask_queue.popleft()

                # If the queue at this price level is empty, delete it and find the next best ask
                if not best_ask_queue:
                    del self.asks[self.best_ask]
                    self.best_ask = min(self.asks.keys()) if self.asks else None

        else:  # SIDE.SELL
            # While the incoming sell price is <= the best bid, we have a cross
            while self.best_bid is not None and incoming_order.price <= self.best_bid and incoming_order.quantity > 0:
                best_bid_queue = self.bids[self.best_bid]

                while best_bid_queue and incoming_order.quantity > 0:
                    resting_order = best_bid_queue[0]

                    traded_quantity = min(incoming_order.quantity, resting_order.quantity)

                    trades.append({
                        "maker_order_id": resting_order.order_id,
                        "taker_order_id": incoming_order.order_id,
                        "price": resting_order.price,
                        "quantity": traded_quantity
                    })

                    incoming_order.quantity -= traded_quantity
                    resting_order.quantity -= traded_quantity

                    if resting_order.quantity == 0:
                        best_bid_queue.popleft()

                if not best_bid_queue:
                    del self.bids[self.best_bid]
                    self.best_bid = max(self.bids.keys()) if self.bids else None

        # If the incoming order still has quantity left, add it to the book
        if incoming_order.quantity > 0:
            self.add_resting_order(incoming_order)

        return trades