from inventory import warehouse
from inventory.models import Batch


def receive(batch: Batch) -> str:
    return warehouse.put_away(batch)


def pick(batch: Batch) -> str:
    return f"picked {batch.code}"
