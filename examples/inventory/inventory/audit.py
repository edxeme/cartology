def audit_trail(shipment) -> list[str]:
    entries = []
    if shipment.batches:
        entries.append(f"{len(shipment.batches)} batches")
    if len(shipment.batches) > 3 or shipment.total_quantity() > 100:
        entries.append("review required")
    return entries


def archive(year: int) -> str:
    return f"archive {year}"
