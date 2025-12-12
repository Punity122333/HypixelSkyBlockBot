CREATE TABLE IF NOT EXISTS mining_locations (
    location_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    drops TEXT NOT NULL,
    xp_min INTEGER NOT NULL,
    xp_max INTEGER NOT NULL
);

INSERT OR REPLACE INTO mining_locations VALUES
('coal_mine', 'Coal Mine', '["coal", "cobblestone"]', 5, 15),
('gold_mine', 'Gold Mine', '["gold_ore", "cobblestone"]', 10, 25),
('diamond_reserve', 'Diamond Reserve', '["diamond", "gold_ore", "iron_ore"]', 25, 50),
('obsidian_sanctuary', 'Obsidian Sanctuary', '["obsidian", "diamond"]', 40, 80),
('dwarven_mines', 'Dwarven Mines', '["mithril", "titanium", "diamond"]', 50, 100),
('crystal_hollows', 'Crystal Hollows', '["gemstone", "mithril", "diamond"]', 75, 150);

CREATE TABLE IF NOT EXISTS farming_locations (
    location_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    crops TEXT NOT NULL,
    xp_min INTEGER NOT NULL,
    xp_max INTEGER NOT NULL
);

INSERT OR REPLACE INTO farming_locations VALUES
('barn', 'The Barn', '["wheat", "carrot", "potato"]', 5, 20),
('mushroom_desert', 'Mushroom Desert', '["mushroom", "cactus"]', 10, 30),
('garden', 'The Garden', '["wheat", "carrot", "potato", "pumpkin", "melon"]', 15, 40);

CREATE TABLE IF NOT EXISTS combat_locations (
    location_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    mobs TEXT NOT NULL,
    xp_min INTEGER NOT NULL,
    xp_max INTEGER NOT NULL
);

INSERT OR REPLACE INTO combat_locations VALUES
('spiders_den', 'Spider''s Den', '["spider", "cave_spider", "broodfather"]', 10, 30),
('end', 'The End', '["enderman", "zealot", "dragon"]', 25, 60),
('crimson_isle', 'Crimson Isle', '["blaze", "magma_cube", "wither_skeleton"]', 30, 75),
('deep_caverns', 'Deep Caverns', '["zombie", "skeleton", "creeper"]', 5, 20);

CREATE TABLE IF NOT EXISTS fishing_locations (
    location_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    catches TEXT NOT NULL,
    xp_min INTEGER NOT NULL,
    xp_max INTEGER NOT NULL
);

INSERT OR REPLACE INTO fishing_locations VALUES
('pond', 'Pond', '["raw_fish", "lily_pad"]', 5, 15),
('barn_fishing', 'Barn Fishing', '["raw_fish", "sponge"]', 10, 25),
('mushroom_desert_fishing', 'Mushroom Desert Fishing', '["pufferfish", "clownfish"]', 15, 35),
('spider_den_fishing', 'Spider''s Den Fishing', '["raw_fish", "string"]', 20, 45),
('crimson_isle_fishing', 'Crimson Isle Fishing', '["magmafish", "sulfur"]', 30, 70);

CREATE TABLE IF NOT EXISTS foraging_locations (
    location_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    trees TEXT NOT NULL,
    xp_min INTEGER NOT NULL,
    xp_max INTEGER NOT NULL
);

INSERT OR REPLACE INTO foraging_locations VALUES
('park', 'The Park', '["oak", "birch"]', 5, 15),
('floating_islands', 'Floating Islands', '["spruce", "dark_oak"]', 10, 25),
('jungle', 'Jungle', '["jungle", "acacia"]', 15, 35);

CREATE INDEX IF NOT EXISTS idx_mining_locations_id ON mining_locations(location_id);
CREATE INDEX IF NOT EXISTS idx_farming_locations_id ON farming_locations(location_id);
CREATE INDEX IF NOT EXISTS idx_combat_locations_id ON combat_locations(location_id);
CREATE INDEX IF NOT EXISTS idx_fishing_locations_id ON fishing_locations(location_id);
CREATE INDEX IF NOT EXISTS idx_foraging_locations_id ON foraging_locations(location_id);
