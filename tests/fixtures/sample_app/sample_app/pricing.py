from sample_app import orders
from sample_app.config import TAX_RATE


def price_with_tax(amount: float) -> float:
    return amount * (1 + TAX_RATE)


def discount_for(order_size: int) -> float:
    if order_size > 100:
        return 0.2
    elif order_size > 50:
        return 0.1
    elif order_size > 10 and order_size < 20:
        return 0.05
    return 0.0


def total_for(order) -> float:
    return orders.grand_total(order)
