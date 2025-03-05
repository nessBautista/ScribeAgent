from allocation.domain.model import OrderLine

def test_orderline_instantiation():
    order = OrderLine(
        orderid="123",
        sku="ABC",
        qty=5
    )
    assert order.orderid == "123"

def test_orderline_hashability():
    order1 = OrderLine(orderid="123", sku="ABC", qty=5)
    order2 = OrderLine(orderid="123", sku="ABC", qty=5)
    order3 = OrderLine(orderid="124", sku="ABC", qty=5)
    assert order1 == order2
    assert order1 != order3
    orders_set = {order1, order2}
    # Since order1 and order2 are equal, the set should contain only one unique element
    assert len(orders_set) == 1
