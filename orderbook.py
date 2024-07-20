import bisect
import logging
from typing import Dict, List, Literal

from doubly_linked_list import DoublyLinkedList, Node, OrderBookEntry
from order import Order

logger = logging.getLogger(__name__)


QUEUE_PRICE_TYPE_TO_MULTIPLE = {"ask": 1, "bid": -1}


def get_queue_price_multiple(queue_type: Literal["bid", "ask"]):
    return QUEUE_PRICE_TYPE_TO_MULTIPLE.get(queue_type)


class OrderQueue:
    def __init__(self, queue_type: Literal["bid", "ask"]):
        self.queue_price_multiple: int = get_queue_price_multiple(queue_type)
        self.order_id_to_order: Dict[int, Node] = dict()
        self.price_to_order_list: Dict[int, DoublyLinkedList] = dict()
        self.prices: List[int] = []

    def add_order(self, order: OrderBookEntry):
        order_node = Node(order)
        self.order_id_to_order[order.order_id] = order_node
        if order.price in self.price_to_order_list:
            self.price_to_order_list[order.price].add_to_tail(order_node)
        else:
            bisect.insort(
                self.prices, order.price, key=lambda x: self.queue_price_multiple * x
            )
            self.price_to_order_list[order.price] = DoublyLinkedList().add_to_tail(
                order_node
            )

    def cancel_order(self, order_id: int):
        order_node = self.order_id_to_order[order_id]
        order = order_node.order
        self.price_to_order_list[order.price].remove(order_node)
        del self.order_id_to_order[order_id]
        # If there are no orders with that price we remove it
        if self.price_to_order_list[order.price].length == 0:
            i = (
                bisect.bisect(
                    self.prices,
                    order.price * self.queue_price_multiple,
                    key=lambda x: self.queue_price_multiple * x,
                )
                - 1
            )
            del self.prices[i]
            del self.price_to_order_list[order.price]

    def get_best_price(self) -> int:
        best_price = None
        if len(self.prices) > 0:
            best_price = self.prices[0]
        return best_price

    def _match_single(self, order: OrderBookEntry):
        matched_order = self.price_to_order_list[self.prices[0]].head.order
        trade_price = matched_order.price
        if matched_order.quantity <= order.quantity:
            order.quantity -= matched_order.quantity
            self.cancel_order(matched_order.order_id)
        else:
            matched_order.quantity -= order.quantity
            order.quantity = 0
        return trade_price, self.get_best_price()

    def execute_market_order(self, order: OrderBookEntry) -> list:
        trades_and_queue_best = []
        while order.quantity > 0 and self.prices:
            trades_and_queue_best.append(self._match_single(order))
        return trades_and_queue_best

    def execute_crossed_limit_order(self, order: OrderBookEntry) -> list:
        trades_and_queue_best = []
        while (
            self.get_best_price() is not None
            and (
                self.get_best_price() * self.queue_price_multiple * -1
                >= order.price * self.queue_price_multiple * -1
            )
            and (order.quantity > 0 and len(self.prices) > 0)
        ):
            trades_and_queue_best.append(self._match_single(order))
        return trades_and_queue_best


class MarketOrderQueue:
    def __init__(self):
        self.order_id_to_order: Dict[int, Node] = dict()
        self.orders = DoublyLinkedList()

    def add_order(self, order: OrderBookEntry):
        node = Node(order)
        self.order_id_to_order[order.order_id] = node
        self.orders.add_to_tail(node)

    def cancel_order(self, order_id: int):
        order_node = self.order_id_to_order[order_id]
        self.orders.remove(order_node)
        del self.order_id_to_order[order_id]


class OrderBook:
    def __init__(self):
        self.sequence_number: int = 0

        self.bid_queue = OrderQueue("bid")
        self.ask_queue = OrderQueue("ask")

        # These Queues hold market orders that were not able to execute
        self.market_bid_queue = MarketOrderQueue()
        self.market_ask_queue = MarketOrderQueue()

    def _increment_sequence_number(self):
        self.sequence_number += 1
        return self.sequence_number

    def _create_order_and_get_new_sequence_number(self, order: Order):
        order_id = self._increment_sequence_number()
        order_book_entry = OrderBookEntry(order_id, order.quantity, order.price)
        return order_book_entry

    def add_order(self, order: Order):
        messages_for_external_feed = []
        if order.order_type == "limit":
            messages_for_external_feed = self._process_limit_order(order)
        elif order.order_type == "market":
            messages_for_external_feed = self._process_market_order(order)
        else:
            logger.info(
                f"Failed to process order, unrecognized type: {order.order_type}"
            )
        messages_for_external_feed.extend(self._attempt_to_flush_market_order_queues())
        return messages_for_external_feed

    def _flush_single_market_order_from_queue(self):
        side = None
        messages_for_external_feed = []
        if (
            self.market_ask_queue.orders.length > 0
            and self.market_bid_queue.orders.length > 0
        ):
            if (
                self.market_ask_queue.orders.head.order.order_id
                < self.market_bid_queue.orders.head.order.order_id
            ) and len(self.bid_queue.prices) > 0:
                side = "sell"
            elif len(self.ask_queue.prices) > 0:
                side = "buy"
        elif self.market_ask_queue.orders.length > 0 and len(self.bid_queue.prices) > 0:
            side = "sell"
        elif self.market_bid_queue.orders.length > 0 and len(self.ask_queue.prices) > 0:
            side = "buy"

        if side is not None:
            if side == "buy":
                order_book_entry = self.market_bid_queue.orders.head.order
                queue = self.ask_queue
                market_order_queue = self.market_bid_queue
            else:
                order_book_entry = self.market_ask_queue.orders.head.order
                queue = self.bid_queue
                market_order_queue = self.market_ask_queue

            trades_and_best = queue.execute_market_order(order_book_entry)
            if order_book_entry.quantity == 0:
                market_order_queue.cancel_order(order_book_entry.order_id)

            messages_for_external_feed = self._convert_trades_and_best_to_messages(
                trades_and_best, side
            )
        return messages_for_external_feed, side

    def _attempt_to_flush_market_order_queues(self):
        messages_for_external_feed = []
        side = "start"
        while side is not None:
            messages_for_external_feed_from_execute, side = (
                self._flush_single_market_order_from_queue()
            )
            messages_for_external_feed.extend(messages_for_external_feed_from_execute)
        return messages_for_external_feed

    def _convert_trades_and_best_to_messages(
        self, trades_and_best: list, side: str
    ) -> list:
        trades = []
        bids = []
        asks = []
        if side == "buy":
            best = asks
            opposite_best = self.bid_queue.get_best_price()
            bids = [opposite_best] * len(trades_and_best)
        else:
            best = bids
            opposite_best = self.ask_queue.get_best_price()
            asks = [opposite_best] * len(trades_and_best)
        for trade, best_price in trades_and_best:
            trades.append(trade)
            best.append(best_price)
        return [
            {"bid": bid, "ask": ask, "trade_price": trade_price}
            for bid, ask, trade_price in zip(bids, asks, trades)
        ]

    @staticmethod
    def _output_external_messages(messages: list):
        for message in messages:
            print(message)

    def _process_limit_order(self, order: Order):
        crossed_order = False
        messages_for_external_feed = []
        if order.side == "buy":
            queue = self.bid_queue
            best_price_opposite_price = self.ask_queue.get_best_price()
            if (
                best_price_opposite_price is not None
                and order.price >= best_price_opposite_price
            ):
                queue = self.ask_queue
                crossed_order = True
        elif order.side == "sell":
            queue = self.ask_queue
            best_price_opposite_price = self.bid_queue.get_best_price()
            if (
                best_price_opposite_price is not None
                and order.price <= best_price_opposite_price
            ):
                queue = self.bid_queue
                crossed_order = True
        else:
            logger.info(f"Failed to process order, unrecognized side: {order.side}")
            return messages_for_external_feed
        if crossed_order:
            trades_and_best = self._process_crossed_limit_order(order, queue)
            messages_for_external_feed = self._convert_trades_and_best_to_messages(
                trades_and_best, order.side
            )
        else:
            order_book_entry = self._create_order_and_get_new_sequence_number(order)
            queue.add_order(order_book_entry)
        return messages_for_external_feed

    def _process_crossed_limit_order(self, order: Order, queue: OrderQueue):
        order_book_entry = self._create_order_and_get_new_sequence_number(order)
        trades_and_best = queue.execute_crossed_limit_order(order_book_entry)
        if order_book_entry.quantity > 0:
            self._process_limit_order(
                Order(
                    order.side, order.order_type, order_book_entry.quantity, order.price
                )
            )
        return trades_and_best

    def _process_market_order(self, order: Order):
        messages_for_external_feed = []
        if order.side == "buy":
            queue = self.ask_queue
        elif order.side == "sell":
            queue = self.bid_queue
        else:
            logger.info(f"Failed to process order, unrecognized side: {order.side}")
            return messages_for_external_feed
        order_book_entry = self._create_order_and_get_new_sequence_number(order)
        trades_and_best = queue.execute_market_order(order_book_entry)
        if order_book_entry.quantity > 0:
            if order.side == "buy":
                self.market_bid_queue.add_order(order_book_entry)
            else:
                self.market_ask_queue.add_order(order_book_entry)
        messages_for_external_feed = self._convert_trades_and_best_to_messages(
            trades_and_best, order.side
        )
        return messages_for_external_feed

    def cancel_order(self, order_id: int):
        if order_id in self.bid_queue.order_id_to_order:
            self.bid_queue.cancel_order(order_id)
        elif order_id in self.ask_queue.order_id_to_order:
            self.ask_queue.cancel_order(order_id)
        elif order_id in self.market_bid_queue.order_id_to_order:
            self.market_bid_queue.cancel_order(order_id)
        elif order_id in self.market_ask_queue.order_id_to_order:
            self.market_ask_queue.cancel_order(order_id)
        else:
            logger.info(f"Order ID not recognized: {order_id}")
