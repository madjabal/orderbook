import pytest

from doubly_linked_list import OrderBookEntry
from order import create_order
from orderbook import OrderBook


@pytest.fixture()
def bid_primed_order_book():
    orders = [
        create_order("buy", "limit", 10, 99),
        create_order("buy", "limit", 4, 98),
        create_order("buy", "limit", 2, 99),
        create_order("buy", "limit", 20, 97),
        create_order("buy", "limit", 15, 98),
        create_order("buy", "limit", 10, 97),
    ]
    order_book = OrderBook()
    for order in orders:
        order_book.add_order(order)
    return order_book


@pytest.fixture()
def full_primed_order_book(bid_primed_order_book):
    orders = [
        create_order("sell", "limit", 10, 101),
        create_order("sell", "limit", 4, 102),
        create_order("sell", "limit", 2, 101),
        create_order("sell", "limit", 20, 103),
        create_order("sell", "limit", 15, 102),
        create_order("sell", "limit", 10, 103),
    ]
    for order in orders:
        bid_primed_order_book.add_order(order)
    return bid_primed_order_book


@pytest.fixture()
def market_primed_order_book(bid_primed_order_book):
    orders = [
        create_order("buy", "market", 10, None),
        create_order("buy", "market", 4, None),
        create_order("buy", "market", 2, None),
        create_order("buy", "market", 20, None),
        create_order("buy", "market", 15, None),
        create_order("buy", "market", 10, None),
    ]
    for order in orders:
        bid_primed_order_book.add_order(order)
    return bid_primed_order_book


def test_add_limit_order_to_empty_book():
    orderbook = OrderBook()
    limit_order = create_order("buy", "limit", 10, 100)
    messages = orderbook.add_order(limit_order)

    assert messages == []

    assert orderbook.sequence_number == 1

    assert orderbook.bid_queue.queue_price_multiple == -1
    assert list(orderbook.bid_queue.order_id_to_order.keys()) == [1]
    assert list(orderbook.bid_queue.order_id_to_order.values())[
        0
    ].order == OrderBookEntry(order_id=1, quantity=10, price=100)
    assert list(orderbook.bid_queue.price_to_order_list) == [100]
    assert list(orderbook.bid_queue.price_to_order_list.values())[
        0
    ].head.order == OrderBookEntry(order_id=1, quantity=10, price=100)
    assert orderbook.bid_queue.prices == [100]

    assert (
        list(orderbook.bid_queue.order_id_to_order.values())[0].order
        == list(orderbook.bid_queue.price_to_order_list.values())[0].head.order
    )

    assert orderbook.ask_queue.queue_price_multiple == 1
    assert list(orderbook.ask_queue.order_id_to_order.keys()) == []
    assert list(orderbook.ask_queue.order_id_to_order.values()) == []
    assert list(orderbook.ask_queue.price_to_order_list) == []
    assert list(orderbook.ask_queue.price_to_order_list.values()) == []
    assert orderbook.ask_queue.prices == []

    assert list(orderbook.market_bid_queue.order_id_to_order.keys()) == []
    assert list(orderbook.market_bid_queue.order_id_to_order.values()) == []
    assert orderbook.market_bid_queue.orders.length == 0

    assert list(orderbook.market_ask_queue.order_id_to_order.keys()) == []
    assert list(orderbook.market_ask_queue.order_id_to_order.values()) == []
    assert orderbook.market_ask_queue.orders.length == 0


def test_add_market_order_to_empty_book():
    orderbook = OrderBook()
    market_order = create_order("buy", "market", 10, None)
    messages = orderbook.add_order(market_order)

    assert messages == []

    assert orderbook.sequence_number == 1

    assert orderbook.bid_queue.queue_price_multiple == -1
    assert list(orderbook.bid_queue.order_id_to_order.keys()) == []
    assert list(orderbook.bid_queue.order_id_to_order.values()) == []
    assert list(orderbook.bid_queue.price_to_order_list) == []
    assert list(orderbook.bid_queue.price_to_order_list.values()) == []
    assert orderbook.bid_queue.prices == []

    assert orderbook.ask_queue.queue_price_multiple == 1
    assert list(orderbook.ask_queue.order_id_to_order.keys()) == []
    assert list(orderbook.ask_queue.order_id_to_order.values()) == []
    assert list(orderbook.ask_queue.price_to_order_list) == []
    assert list(orderbook.ask_queue.price_to_order_list.values()) == []
    assert orderbook.ask_queue.prices == []

    assert list(orderbook.market_bid_queue.order_id_to_order.keys()) == [1]
    assert list(orderbook.market_bid_queue.order_id_to_order.values())[
        0
    ].order == OrderBookEntry(order_id=1, quantity=10, price=None)
    assert orderbook.market_bid_queue.orders.length == 1

    assert list(orderbook.market_ask_queue.order_id_to_order.keys()) == []
    assert list(orderbook.market_ask_queue.order_id_to_order.values()) == []
    assert orderbook.market_ask_queue.orders.length == 0


def test_add_market_order_to_shallow_book():
    orderbook = OrderBook()
    limit_order = create_order("sell", "limit", 10, 100)
    market_order = create_order("buy", "market", 10, None)
    messages = []
    messages.extend(orderbook.add_order(limit_order))
    messages.extend(orderbook.add_order(market_order))

    assert messages == [{"bid": None, "ask": None, "trade_price": 100}]

    assert orderbook.sequence_number == 2

    assert orderbook.bid_queue.queue_price_multiple == -1
    assert list(orderbook.bid_queue.order_id_to_order.keys()) == []
    assert list(orderbook.bid_queue.order_id_to_order.values()) == []
    assert list(orderbook.bid_queue.price_to_order_list) == []
    assert list(orderbook.bid_queue.price_to_order_list.values()) == []
    assert orderbook.bid_queue.prices == []

    assert orderbook.ask_queue.queue_price_multiple == 1
    assert list(orderbook.ask_queue.order_id_to_order.keys()) == []
    assert list(orderbook.ask_queue.order_id_to_order.values()) == []
    assert list(orderbook.ask_queue.price_to_order_list) == []
    assert list(orderbook.ask_queue.price_to_order_list.values()) == []
    assert orderbook.ask_queue.prices == []

    assert list(orderbook.market_bid_queue.order_id_to_order.keys()) == []
    assert list(orderbook.market_bid_queue.order_id_to_order.values()) == []
    assert orderbook.market_bid_queue.orders.length == 0

    assert list(orderbook.market_ask_queue.order_id_to_order.keys()) == []
    assert list(orderbook.market_ask_queue.order_id_to_order.values()) == []
    assert orderbook.market_ask_queue.orders.length == 0


def test_cancel_order_in_limit_order_queue(full_primed_order_book):
    order_id_for_cancel = 1
    cancelled_order_price = full_primed_order_book.bid_queue.order_id_to_order[
        order_id_for_cancel
    ].order.price
    full_primed_order_book.cancel_order(order_id_for_cancel)

    assert order_id_for_cancel not in full_primed_order_book.bid_queue.order_id_to_order
    assert order_id_for_cancel not in full_primed_order_book.ask_queue.order_id_to_order

    assert (
        order_id_for_cancel
        not in full_primed_order_book.market_bid_queue.order_id_to_order
    )
    assert (
        order_id_for_cancel
        not in full_primed_order_book.market_ask_queue.order_id_to_order
    )

    assert (
        full_primed_order_book.bid_queue.price_to_order_list[
            cancelled_order_price
        ].head.order.order_id
        != order_id_for_cancel
    )


def test_cancel_order_in_market_queue(market_primed_order_book):
    order_id_for_cancel = 7
    market_primed_order_book.cancel_order(order_id_for_cancel)

    assert (
        order_id_for_cancel not in market_primed_order_book.bid_queue.order_id_to_order
    )
    assert (
        order_id_for_cancel not in market_primed_order_book.ask_queue.order_id_to_order
    )

    assert (
        order_id_for_cancel
        not in market_primed_order_book.market_bid_queue.order_id_to_order
    )
    assert (
        order_id_for_cancel
        not in market_primed_order_book.market_ask_queue.order_id_to_order
    )

    assert (
        market_primed_order_book.market_bid_queue.orders.head.order.order_id
        != order_id_for_cancel
    )


def test_add_limit_small_cross(full_primed_order_book):
    limit_order_cross = create_order("buy", "limit", 11, 101)
    messages = []
    messages.extend(full_primed_order_book.add_order(limit_order_cross))

    assert messages == [
        {"bid": 99, "ask": 101, "trade_price": 101},
        {"bid": 99, "ask": 101, "trade_price": 101},
    ]

    assert full_primed_order_book.sequence_number == 13

    assert full_primed_order_book.bid_queue.queue_price_multiple == -1
    assert list(full_primed_order_book.bid_queue.order_id_to_order.keys()) == [
        1,
        2,
        3,
        4,
        5,
        6,
    ]
    assert [
        node.order.order_id
        for node in full_primed_order_book.bid_queue.order_id_to_order.values()
    ] == [1, 2, 3, 4, 5, 6]
    assert list(full_primed_order_book.bid_queue.order_id_to_order.values())[
        0
    ].order == OrderBookEntry(order_id=1, quantity=10, price=99)
    assert list(full_primed_order_book.bid_queue.price_to_order_list) == [99, 98, 97]
    assert [
        dll.head.order.order_id
        for dll in full_primed_order_book.bid_queue.price_to_order_list.values()
    ] == [1, 2, 4]
    assert list(full_primed_order_book.bid_queue.price_to_order_list.values())[
        0
    ].head.order == OrderBookEntry(order_id=1, quantity=10, price=99)
    assert full_primed_order_book.bid_queue.prices == [99, 98, 97]

    assert full_primed_order_book.ask_queue.queue_price_multiple == 1
    assert list(full_primed_order_book.ask_queue.order_id_to_order.keys()) == [
        8,
        9,
        10,
        11,
        12,
    ]
    assert [
        node.order.order_id
        for node in full_primed_order_book.ask_queue.order_id_to_order.values()
    ] == [8, 9, 10, 11, 12]
    assert list(full_primed_order_book.ask_queue.order_id_to_order.values())[
        0
    ].order == OrderBookEntry(order_id=8, quantity=4, price=102)
    assert list(full_primed_order_book.ask_queue.price_to_order_list) == [101, 102, 103]
    assert [
        dll.head.order.order_id
        for dll in full_primed_order_book.ask_queue.price_to_order_list.values()
    ] == [9, 8, 10]
    assert list(full_primed_order_book.ask_queue.price_to_order_list.values())[
        0
    ].head.order == OrderBookEntry(order_id=9, quantity=1, price=101)
    assert full_primed_order_book.ask_queue.prices == [101, 102, 103]


def test_add_limit_large_cross(full_primed_order_book):
    limit_order_cross = create_order("sell", "limit", 1000, 90)

    messages = []
    messages.extend(full_primed_order_book.add_order(limit_order_cross))

    assert messages == [
        {"bid": 99, "ask": 90, "trade_price": 99},
        {"bid": 98, "ask": 90, "trade_price": 99},
        {"bid": 98, "ask": 90, "trade_price": 98},
        {"bid": 97, "ask": 90, "trade_price": 98},
        {"bid": 97, "ask": 90, "trade_price": 97},
        {"bid": None, "ask": 90, "trade_price": 97},
    ]

    assert full_primed_order_book.sequence_number == 14

    assert full_primed_order_book.bid_queue.queue_price_multiple == -1
    assert list(full_primed_order_book.bid_queue.order_id_to_order.keys()) == []
    assert [
        node.order.order_id
        for node in full_primed_order_book.bid_queue.order_id_to_order.values()
    ] == []
    assert list(full_primed_order_book.bid_queue.price_to_order_list) == []
    assert [
        dll.head.order.order_id
        for dll in full_primed_order_book.bid_queue.price_to_order_list.values()
    ] == []
    assert full_primed_order_book.bid_queue.prices == []

    assert full_primed_order_book.ask_queue.queue_price_multiple == 1
    assert list(full_primed_order_book.ask_queue.order_id_to_order.keys()) == [
        7,
        8,
        9,
        10,
        11,
        12,
        14,
    ]
    assert [
        node.order.order_id
        for node in full_primed_order_book.ask_queue.order_id_to_order.values()
    ] == [7, 8, 9, 10, 11, 12, 14]
    assert list(full_primed_order_book.ask_queue.price_to_order_list) == [
        101,
        102,
        103,
        90,
    ]
    assert [
        dll.head.order.order_id
        for dll in full_primed_order_book.ask_queue.price_to_order_list.values()
    ] == [7, 8, 10, 14]
    assert full_primed_order_book.ask_queue.prices == [90, 101, 102, 103]


def test_flush_market_orders(market_primed_order_book):
    limit_order = create_order("sell", "limit", 10, 100)

    messages = []
    messages.extend(market_primed_order_book.add_order(limit_order))

    assert messages == [{"bid": 99, "ask": None, "trade_price": 100}]

    assert market_primed_order_book.sequence_number == 13

    assert market_primed_order_book.bid_queue.queue_price_multiple == -1
    assert list(market_primed_order_book.bid_queue.order_id_to_order.keys()) == [
        1,
        2,
        3,
        4,
        5,
        6,
    ]
    assert len(list(market_primed_order_book.bid_queue.order_id_to_order.values())) == 6
    assert list(market_primed_order_book.bid_queue.price_to_order_list) == [99, 98, 97]
    assert (
        len(list(market_primed_order_book.bid_queue.price_to_order_list.values())) == 3
    )
    assert market_primed_order_book.bid_queue.prices == [99, 98, 97]

    assert market_primed_order_book.ask_queue.queue_price_multiple == 1
    assert list(market_primed_order_book.ask_queue.order_id_to_order.keys()) == []
    assert list(market_primed_order_book.ask_queue.order_id_to_order.values()) == []
    assert list(market_primed_order_book.ask_queue.price_to_order_list) == []
    assert list(market_primed_order_book.ask_queue.price_to_order_list.values()) == []
    assert market_primed_order_book.ask_queue.prices == []

    assert list(market_primed_order_book.market_bid_queue.order_id_to_order.keys()) == [
        8,
        9,
        10,
        11,
        12,
    ]
    assert (
        len(list(market_primed_order_book.market_bid_queue.order_id_to_order.values()))
        == 5
    )
    assert market_primed_order_book.market_bid_queue.orders.length == 5

    assert (
        list(market_primed_order_book.market_ask_queue.order_id_to_order.keys()) == []
    )
    assert (
        list(market_primed_order_book.market_ask_queue.order_id_to_order.values()) == []
    )
    assert market_primed_order_book.market_ask_queue.orders.length == 0
