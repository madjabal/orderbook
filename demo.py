import random
import time

from order import create_order
from orderbook import OrderBook

QUANTITIES = list(range(1, 100))
DELTAS = range(-3, 30)


def generate_orders(n):
    orders = []
    for i in range(n):
        side = random.choice(["buy", "sell"])
        order_type = random.choice(["limit", "market"])
        price = None
        if order_type == "limit":
            if side == "buy":
                price = 99 - random.choice(DELTAS)
            else:
                price = 101 + random.choice(DELTAS)
        quantity = random.choice(QUANTITIES)
        orders.append(
            create_order(
                side=side, order_type=order_type, quantity=quantity, price=price
            )
        )
    return orders


def main():
    # Only use output with low order numbers (<1000)
    output = False
    order_number = 1_000_000

    random.seed(404)
    orders = generate_orders(order_number)
    order_book = OrderBook()
    start_time = time.time()
    for order in orders:
        trades = order_book.add_order(order)
        if output:
            print("bids", order_book.bid_queue.prices)
            print("asks", order_book.ask_queue.prices)
            print("market_bid_queue", order_book.market_bid_queue.orders.length)
            print("market_ask_queue", order_book.market_ask_queue.orders.length)
            for trade in trades:
                print("Trades")
                print(trade)
            print()
    execution_seconds = time.time() - start_time
    print(
        f"Process {order_number} in {execution_seconds: .3f} seconds, {order_number/execution_seconds: .0f} orders/second"
    )


if __name__ == "__main__":
    main()
