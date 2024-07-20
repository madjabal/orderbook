import dataclasses
from typing import Literal, Optional

VALID_ORDER_TYPES = {"limit", "market"}
VALID_SIDES = {"buy", "sell"}


@dataclasses.dataclass()
class Order:
    side: Literal["buy", "sell"]
    order_type: Literal["limit", "market"]
    quantity: int
    price: Optional[int]


def create_order(
    side: Literal["buy", "sell"],
    order_type: Literal["limit", "market"],
    quantity: int,
    price: Optional[int],
) -> Order:
    assert side in VALID_SIDES, f"Unknown side type {side}"
    assert order_type in VALID_ORDER_TYPES, f"Unknown order type {order_type}"
    assert (order_type == "market" and price is None) or (
        order_type == "limit" and price is not None
    ), f"Must choose one of market order or set price, given {order_type}, {price}"
    assert (
        isinstance(price, int) and price > 0
    ) or price is None, f"Price must be int and positive or None, given type: {type(price)} with value: {price}"
    assert quantity > 0 and isinstance(
        quantity, int
    ), f"Quantity must be int and positive, given type: {type(quantity)} with value: {quantity}"
    return Order(side=side, order_type=order_type, quantity=quantity, price=price)
