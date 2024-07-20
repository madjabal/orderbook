import pytest

from order import VALID_SIDES, create_order


@pytest.mark.parametrize("side", VALID_SIDES)
def test_create_market_order(side):
    order = create_order(side, "market", 10, None)

    assert order.order_type == "market"
    assert order.quantity == 10
    assert order.price is None
    assert isinstance(order.quantity, int)


@pytest.mark.parametrize("side", VALID_SIDES)
def test_create_limit_order(side):
    order = create_order(side, "limit", 10, 101)

    assert order.order_type == "limit"
    assert order.quantity == 10
    assert order.price == 101
    assert isinstance(order.quantity, int)


@pytest.mark.parametrize("order_type", ["market", "limit"])
@pytest.mark.parametrize("side", VALID_SIDES)
def test_quantity_assertion(order_type, side):
    expected_quantity_assertion = "Quantity must be int and positive, given type: "
    price = 101 if order_type == "limit" else None
    with pytest.raises(AssertionError, match=expected_quantity_assertion):
        create_order(side, order_type, 10.0, price)
        create_order(side, order_type, -1, price)


@pytest.mark.parametrize("side", VALID_SIDES)
def test_price_assertion(side):
    expected_price_assertion = "Price must be int and positive or None, given type: "
    invalid_prices = [-1, 10.0, "", "limit"]
    for invalid_price in invalid_prices:
        with pytest.raises(AssertionError, match=expected_price_assertion):
            create_order(side, "limit", 1, invalid_price)


@pytest.mark.parametrize("side", VALID_SIDES)
def test_invalid_order_type_assertion(side):
    expected_order_type_assertion = "Unknown order type "
    invalid_order_types = ["Market", "Limit", "MARKET", "LIMIT", "", None, -10]
    for invalid_order_type in invalid_order_types:
        with pytest.raises(AssertionError, match=expected_order_type_assertion):
            create_order(side, invalid_order_type, 10, None)


@pytest.mark.parametrize("side", VALID_SIDES)
def test_market_order_and_price_assertions(side):
    expected_market_order_with_price_assertion = (
        "Must choose one of market order or set price, given "
    )
    with pytest.raises(
        AssertionError, match=expected_market_order_with_price_assertion
    ):
        create_order(side, "market", 10, 10498)
        create_order(side, "limit", 10, None)


@pytest.mark.parametrize("order_type", ["market", "limit"])
def test_invalid_side_assertion(order_type):
    expected_side_assertion = "Unknown side type "
    price = 10498 if order_type == "limit" else None
    invalid_sides = ["Buy", "Sell", "BUY", "SELL", -1, 10.0, None]
    for invalid_side in invalid_sides:
        with pytest.raises(AssertionError, match=expected_side_assertion):
            create_order(invalid_side, order_type, 10, price)
