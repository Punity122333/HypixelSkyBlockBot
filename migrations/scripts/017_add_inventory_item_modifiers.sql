CREATE TABLE IF NOT EXISTS inventory_item_modifiers (
    inventory_item_id INTEGER PRIMARY KEY,
    modifier_data TEXT,
    applied_at INTEGER NOT NULL,
    FOREIGN KEY (inventory_item_id) REFERENCES inventory_items(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_inventory_item_modifiers ON inventory_item_modifiers(inventory_item_id);
