CREATE TABLE IF NOT EXISTS player_equipment (
    user_id INTEGER PRIMARY KEY,
    helmet_slot INTEGER,
    chestplate_slot INTEGER,
    leggings_slot INTEGER,
    boots_slot INTEGER,
    weapon_slot INTEGER,
    tool_slot INTEGER,
    FOREIGN KEY (user_id) REFERENCES players(user_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS armor_stats (
    item_id TEXT PRIMARY KEY,
    defense INTEGER DEFAULT 0,
    health INTEGER DEFAULT 0,
    strength INTEGER DEFAULT 0,
    crit_chance REAL DEFAULT 0,
    crit_damage REAL DEFAULT 0,
    intelligence INTEGER DEFAULT 0,
    speed INTEGER DEFAULT 0,
    magic_find INTEGER DEFAULT 0,
    pet_luck INTEGER DEFAULT 0,
    true_defense INTEGER DEFAULT 0,
    FOREIGN KEY (item_id) REFERENCES game_items(item_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS tool_stats (
    item_id TEXT PRIMARY KEY,
    tool_type TEXT NOT NULL,
    damage INTEGER DEFAULT 0,
    breaking_power INTEGER DEFAULT 0,
    mining_speed INTEGER DEFAULT 0,
    mining_fortune INTEGER DEFAULT 0,
    farming_fortune INTEGER DEFAULT 0,
    foraging_fortune INTEGER DEFAULT 0,
    fishing_speed INTEGER DEFAULT 0,
    sea_creature_chance REAL DEFAULT 0,
    crop_yield_multiplier REAL DEFAULT 1.0,
    wood_yield_multiplier REAL DEFAULT 1.0,
    ore_yield_multiplier REAL DEFAULT 1.0,
    durability INTEGER DEFAULT 100,
    FOREIGN KEY (item_id) REFERENCES game_items(item_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS weapon_stats (
    item_id TEXT PRIMARY KEY,
    damage INTEGER DEFAULT 0,
    strength INTEGER DEFAULT 0,
    crit_chance REAL DEFAULT 0,
    crit_damage REAL DEFAULT 0,
    attack_speed INTEGER DEFAULT 0,
    ability_damage INTEGER DEFAULT 0,
    ferocity INTEGER DEFAULT 0,
    bonus_attack_speed REAL DEFAULT 0,
    FOREIGN KEY (item_id) REFERENCES game_items(item_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_player_equipment_user ON player_equipment(user_id);
CREATE INDEX IF NOT EXISTS idx_armor_stats_item ON armor_stats(item_id);
CREATE INDEX IF NOT EXISTS idx_tool_stats_item ON tool_stats(item_id);
CREATE INDEX IF NOT EXISTS idx_tool_stats_type ON tool_stats(tool_type);
CREATE INDEX IF NOT EXISTS idx_weapon_stats_item ON weapon_stats(item_id);

ALTER TABLE inventory_items ADD COLUMN enchantments TEXT DEFAULT '{}';
ALTER TABLE inventory_items ADD COLUMN reforge TEXT;
