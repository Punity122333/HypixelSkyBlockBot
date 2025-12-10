def normalize_item_id(item_id: str) -> str:
    return item_id.strip().lower().replace(" ", "_")
