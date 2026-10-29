from dataclasses import dataclass, field


@dataclass
class Item:
    sku: str
    name: str
    unit_price: float


@dataclass
class Order:
    reference: str
    items: list[Item] = field(default_factory=list)

    def subtotal(self) -> float:
        return sum(item.unit_price for item in self.items)
