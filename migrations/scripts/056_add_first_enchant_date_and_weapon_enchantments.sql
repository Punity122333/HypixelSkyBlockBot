ALTER TABLE player_progression ADD COLUMN first_enchant_date INTEGER;

CREATE TABLE IF NOT EXISTS inventory_item_enchantments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    inventory_item_id INTEGER NOT NULL,
    enchantment_id TEXT NOT NULL,
    level INTEGER NOT NULL,
    FOREIGN KEY (inventory_item_id) REFERENCES inventory_items(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_inventory_item_enchantments ON inventory_item_enchantments(inventory_item_id);
