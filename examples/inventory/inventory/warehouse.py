from inventory import storage
from inventory.models import Batch


def put_away(batch: Batch) -> str:
    return f"stored {batch.code}"


def transfer(batch: Batch, destination: str) -> str:
    return storage.pick(batch)
