from engine import Order, OrderBook, Side


def run_simulation():
    book = OrderBook()

    print("--- Submitting Resting Orders (Makers) ---")
    # Two sellers at the exact same price. sell_1 gets time priority.
    book.add_resting_order(Order("sell_1", Side.SELL, 15000, 10))  # $150.00, Qty: 10
    book.add_resting_order(Order("sell_2", Side.SELL, 15000, 5))  # $150.00, Qty: 5
    # A seller at a higher, worse price
    book.add_resting_order(Order("sell_3", Side.SELL, 15050, 20))  # $150.50, Qty: 20

    print(f"Current Best Ask (Lowest Seller): {book.best_ask}")

    print("\n--- Submitting Aggressive Order (Taker) ---")
    # A buyer willing to pay up to $150.00 for 12 shares
    aggressive_buy = Order("buy_1", Side.BUY, 15000, 12)
    print(f"Incoming: BUY 12 @ 15000")

    trades = book.match_order(aggressive_buy)

    print("\n--- Execution Results ---")
    for trade in trades:
        print(f"Trade: {trade['quantity']} shares @ {trade['price']} | "
              f"Maker: {trade['maker_order_id']} <-> Taker: {trade['taker_order_id']}")

    print("\n--- Order Book State After Execution ---")
    print(f"Remaining qty for aggressive buy_1: {aggressive_buy.quantity}")

    # Check what is left at the $150.00 price level
    if 15000 in book.asks and book.asks[15000]:
        remaining_sell_2 = book.asks[15000][0]
        print(f"Next in queue at 15000: {remaining_sell_2.order_id} with qty {remaining_sell_2.quantity}")

    print(f"New Best Ask: {book.best_ask}")


if __name__ == "__main__":
    run_simulation()