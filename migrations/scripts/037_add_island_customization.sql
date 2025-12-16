CREATE TABLE IF NOT EXISTS player_islands (
    user_id INTEGER PRIMARY KEY,
    island_name TEXT DEFAULT 'My Island',
    island_level INTEGER DEFAULT 1,
    visitors_enabled INTEGER DEFAULT 1,
    theme TEXT DEFAULT 'default',
    upgrade_points INTEGER DEFAULT 0,
    last_modified INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES players(user_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS island_decorations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    decoration_id TEXT NOT NULL,
    position_x INTEGER NOT NULL,
    position_y INTEGER NOT NULL,
    rotation INTEGER DEFAULT 0,
    placed_at INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES players(user_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS island_blocks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    block_type TEXT NOT NULL,
    position_x INTEGER NOT NULL,
    position_y INTEGER NOT NULL,
    position_z INTEGER NOT NULL,
    placed_at INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES players(user_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS game_island_decorations (
    decoration_id TEXT PRIMARY KEY,
    decoration_name TEXT NOT NULL,
    decoration_type TEXT NOT NULL,
    description TEXT,
    cost INTEGER DEFAULT 0,
    required_level INTEGER DEFAULT 1,
    rarity TEXT DEFAULT 'COMMON',
    size_x INTEGER DEFAULT 1,
    size_y INTEGER DEFAULT 1
);

CREATE TABLE IF NOT EXISTS game_island_themes (
    theme_id TEXT PRIMARY KEY,
    theme_name TEXT NOT NULL,
    description TEXT,
    cost INTEGER DEFAULT 0,
    required_level INTEGER DEFAULT 1,
    unlock_requirement TEXT
);

INSERT OR IGNORE INTO game_island_decorations VALUES
('oak_tree', 'Oak Tree', 'nature', 'A classic oak tree', 500, 1, 'COMMON', 2, 2),
('stone_path', 'Stone Path', 'path', 'A decorative stone pathway', 100, 1, 'COMMON', 1, 1),
('flower_bed', 'Flower Bed', 'nature', 'Colorful flower arrangement', 250, 1, 'COMMON', 1, 1),
('fountain', 'Fountain', 'decoration', 'A beautiful water fountain', 5000, 5, 'UNCOMMON', 3, 3),
('lamp_post', 'Lamp Post', 'lighting', 'Illuminates your island', 750, 2, 'COMMON', 1, 2),
('statue', 'Statue', 'decoration', 'An impressive stone statue', 10000, 10, 'RARE', 2, 3),
('garden_bench', 'Garden Bench', 'furniture', 'A relaxing place to sit', 1000, 3, 'COMMON', 2, 1),
('hedge', 'Decorative Hedge', 'nature', 'Trimmed hedge decoration', 500, 2, 'COMMON', 1, 1),
('pond', 'Koi Pond', 'water', 'A peaceful koi pond', 7500, 8, 'UNCOMMON', 4, 4),
('gazebo', 'Gazebo', 'structure', 'A covered outdoor structure', 15000, 12, 'RARE', 5, 5),
('windmill', 'Windmill', 'structure', 'A decorative windmill', 25000, 15, 'EPIC', 6, 8),
('bridge', 'Wooden Bridge', 'structure', 'A decorative bridge', 3000, 5, 'UNCOMMON', 4, 2),
('torch', 'Standing Torch', 'lighting', 'A lit torch for ambiance', 200, 1, 'COMMON', 1, 1),
('flag', 'Banner Flag', 'decoration', 'A colorful flag banner', 1500, 4, 'UNCOMMON', 1, 3),
('well', 'Stone Well', 'decoration', 'A classic stone well', 5000, 6, 'UNCOMMON', 2, 2);

INSERT OR IGNORE INTO game_island_themes VALUES
('default', 'Default Theme', 'The classic SkyBlock island theme', 0, 1, NULL),
('desert', 'Desert Oasis', 'Sandy desert with palm trees', 50000, 10, NULL),
('snow', 'Winter Wonderland', 'Snowy winter landscape', 50000, 10, NULL),
('jungle', 'Tropical Jungle', 'Dense jungle environment', 75000, 15, NULL),
('nether', 'Crimson Wastes', 'Nether-themed island', 100000, 20, 'Visit Crimson Isle'),
('mushroom', 'Mushroom Fields', 'Mystical mushroom biome', 75000, 15, NULL),
('end', 'Void Dimension', 'End-themed dark void', 100000, 20, 'Visit The End'),
('crystal', 'Crystal Cavern', 'Glowing crystal formations', 150000, 25, 'Access Crystal Hollows');

CREATE INDEX IF NOT EXISTS idx_island_decorations_user ON island_decorations(user_id);
CREATE INDEX IF NOT EXISTS idx_island_blocks_user ON island_blocks(user_id);
CREATE INDEX IF NOT EXISTS idx_island_decorations_position ON island_decorations(user_id, position_x, position_y);
