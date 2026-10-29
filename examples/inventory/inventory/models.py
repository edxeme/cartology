from dataclasses import dataclass


@dataclass
class Batch:
    code: str
    quantity: int


@dataclass
class Shipment:
    batches: list[Batch]

    def total_quantity(self) -> int:
        return sum(batch.quantity for batch in self.batches)
