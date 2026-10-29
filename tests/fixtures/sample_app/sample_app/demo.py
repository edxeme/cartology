"""Runnable demo used by the trace tests."""

from sample_app import orders, pricing
from sample_app.models import Item, Order


def main() -> float:
    order = Order(
        "A-001",
        items=[Item("SKU-1", "Widget", 10.0), Item("SKU-2", "Gadget", 2.5)],
    )
    return pricing.price_with_tax(orders.grand_total(order))


if __name__ == "__main__":
    main()
