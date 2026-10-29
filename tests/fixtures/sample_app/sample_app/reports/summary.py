from ..config import CURRENCY
from ..models import Order


def render(order: Order) -> str:
    lines = [f"Order {order.reference}"]
    for item in order.items:
        lines.append(f"  {item.sku}  {item.name}  {item.unit_price:.2f}")
    lines.append(f"Subtotal {order.subtotal():.2f} {CURRENCY}")
    return "\n".join(lines)
