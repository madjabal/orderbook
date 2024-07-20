import dataclasses
from typing import Optional


@dataclasses.dataclass()
class OrderBookEntry:
    order_id: int
    quantity: int
    price: Optional[int]


class Node:
    def __init__(self, order: OrderBookEntry):
        self.order = order
        self.next = None
        self.prev = None


class DoublyLinkedList:
    def __init__(self):
        self.head = None
        self.tail = None
        self.length = 0

    def add_to_tail(self, new_node: Node):
        if new_node.order.order_id == 5:
            x = 0
        if self.length == 0:
            self.head = new_node
            self.tail = new_node
        else:
            self.tail.next = new_node
            new_node.prev = self.tail
            self.tail = new_node
        self.length += 1
        return self

    def remove(self, node: Node):
        self.length -= 1
        if node == self.head:
            if node == self.tail:
                self.head = None
                self.tail = None
            else:
                self.head = node.next
                node.next.prev = None
        elif node == self.tail:
            self.tail = node.prev
            node.prev.next = None
        else:
            if node.prev is None:
                x = 0
            node.prev.next = node.next
            node.next.prev = node.prev
