from sample_app import pricing
from sample_app.models import Order


def grand_total(order: Order) -> float:
    return pricing.price_with_tax(order.subtotal())
