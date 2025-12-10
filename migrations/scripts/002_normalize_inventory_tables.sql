CREATE TABLE inventory_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    item_id TEXT NOT NULL,
    amount INTEGER DEFAULT 1,
    slot INTEGER NOT NULL,
    equipped BOOLEAN DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES players(user_id) ON DELETE CASCADE,
    UNIQUE(user_id, slot)
);

INSERT INTO inventory_items (user_id, item_id, amount, slot)
SELECT user_id, item_id, 1 as amount, slot
FROM inventories;

CREATE TABLE inventory_item_metadata (
    inventory_item_id INTEGER PRIMARY KEY,
    reforge TEXT,
    enchantments TEXT,
    hot_potato_books INTEGER DEFAULT 0,
    stars INTEGER DEFAULT 0,
    runes TEXT,
    custom_name TEXT,
    FOREIGN KEY (inventory_item_id) REFERENCES inventory_items(id) ON DELETE CASCADE
);

CREATE TABLE enderchest_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    item_id TEXT NOT NULL,
    amount INTEGER DEFAULT 1,
    slot INTEGER NOT NULL,
    metadata TEXT,
    FOREIGN KEY (user_id) REFERENCES players(user_id) ON DELETE CASCADE,
    UNIQUE(user_id, slot)
);

INSERT INTO enderchest_items (user_id, item_id, amount, slot, metadata)
SELECT user_id, item_id, 1 as amount, slot, item_data
FROM enderchest;

CREATE TABLE armor_slots (
    user_id INTEGER NOT NULL,
    slot TEXT NOT NULL,
    item_id TEXT NOT NULL,
    metadata TEXT,
    PRIMARY KEY (user_id, slot),
    FOREIGN KEY (user_id) REFERENCES players(user_id) ON DELETE CASCADE
);

INSERT INTO armor_slots (user_id, slot, item_id, metadata)
SELECT user_id, slot, item_id, item_data
FROM armor;

CREATE TABLE wardrobe_slots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    slot INTEGER NOT NULL,
    item_id TEXT NOT NULL,
    metadata TEXT,
    FOREIGN KEY (user_id) REFERENCES players(user_id) ON DELETE CASCADE,
    UNIQUE(user_id, slot)
);

INSERT INTO wardrobe_slots (user_id, slot, item_id, metadata)
SELECT user_id, slot, item_id, item_data
FROM wardrobe;

CREATE TABLE accessory_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    item_id TEXT NOT NULL,
    slot INTEGER NOT NULL,
    enrichment TEXT,
    FOREIGN KEY (user_id) REFERENCES players(user_id) ON DELETE CASCADE,
    UNIQUE(user_id, slot)
);

INSERT INTO accessory_items (user_id, item_id, slot)
SELECT user_id, item_id, slot
FROM accessory_bag;

DROP TABLE inventories;
DROP TABLE enderchest;
DROP TABLE armor;
DROP TABLE wardrobe;
DROP TABLE accessory_bag;

CREATE INDEX idx_inventory_items_user ON inventory_items(user_id);
CREATE INDEX idx_inventory_items_item ON inventory_items(item_id);
CREATE INDEX idx_enderchest_items_user ON enderchest_items(user_id);
CREATE INDEX idx_armor_slots_user ON armor_slots(user_id);
CREATE INDEX idx_wardrobe_slots_user ON wardrobe_slots(user_id);
CREATE INDEX idx_accessory_items_user ON accessory_items(user_id);
