CREATE TABLE IF NOT EXISTS combat_location_unlocks (
    location_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    min_level INTEGER NOT NULL,
    min_coins INTEGER NOT NULL,
    difficulty INTEGER NOT NULL
);

INSERT OR IGNORE INTO combat_location_unlocks (location_id, name, min_level, min_coins, difficulty) VALUES
('hub', 'Hub', 0, 0, 1),
('spiders_den', 'Spider''s Den', 3, 5000, 2),
('crimson_isle', 'Crimson Isle', 8, 50000, 3),
('end', 'The End', 12, 150000, 4),
('nether', 'Nether', 15, 500000, 5),
('deep_caverns', 'Deep Caverns', 5, 15000, 2);

CREATE TABLE IF NOT EXISTS slayer_unlocks (
    slayer_type TEXT NOT NULL,
    min_combat_level INTEGER NOT NULL,
    min_coins INTEGER NOT NULL,
    tier INTEGER NOT NULL,
    cost INTEGER NOT NULL,
    min_level INTEGER NOT NULL,
    xp_reward INTEGER NOT NULL,
    PRIMARY KEY (slayer_type, tier)
);

INSERT OR IGNORE INTO slayer_unlocks (slayer_type, min_combat_level, min_coins, tier, cost, min_level, xp_reward) VALUES
('revenant', 5, 2000, 1, 2000, 5, 5),
('revenant', 5, 2000, 2, 7500, 10, 25),
('revenant', 5, 2000, 3, 20000, 15, 100),
('revenant', 5, 2000, 4, 50000, 20, 500),
('revenant', 5, 2000, 5, 100000, 25, 1500),
('tarantula', 5, 2000, 1, 2000, 5, 5),
('tarantula', 5, 2000, 2, 7500, 10, 25),
('tarantula', 5, 2000, 3, 20000, 15, 100),
('tarantula', 5, 2000, 4, 50000, 20, 500),
('tarantula', 5, 2000, 5, 100000, 25, 1000),
('sven', 10, 2000, 1, 2000, 10, 10),
('sven', 10, 2000, 2, 7500, 15, 30),
('sven', 10, 2000, 3, 20000, 20, 120),
('sven', 10, 2000, 4, 50000, 25, 600),
('sven', 10, 2000, 5, 100000, 30, 1800),
('voidgloom', 15, 2000, 1, 2000, 15, 10),
('voidgloom', 15, 2000, 2, 10000, 20, 50),
('voidgloom', 15, 2000, 3, 30000, 25, 200),
('voidgloom', 15, 2000, 4, 75000, 30, 1000),
('voidgloom', 15, 2000, 5, 150000, 35, 2500),
('inferno', 20, 2000, 1, 2000, 20, 10),
('inferno', 20, 2000, 2, 10000, 25, 50),
('inferno', 20, 2000, 3, 30000, 30, 250),
('inferno', 20, 2000, 4, 75000, 35, 1200),
('inferno', 20, 2000, 5, 150000, 40, 3000);

CREATE TABLE IF NOT EXISTS dungeon_unlocks (
    floor_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    min_level INTEGER NOT NULL,
    min_coins INTEGER NOT NULL
);

INSERT OR IGNORE INTO dungeon_unlocks (floor_id, name, min_level, min_coins) VALUES
('entrance', 'Entrance', 0, 0),
('floor1', 'Floor 1', 3, 5000),
('floor2', 'Floor 2', 5, 15000),
('floor3', 'Floor 3', 7, 30000),
('floor4', 'Floor 4', 9, 60000),
('floor5', 'Floor 5', 11, 120000),
('floor6', 'Floor 6', 13, 250000),
('floor7', 'Floor 7', 15, 500000),
('m1', 'Master Mode 1', 18, 1000000),
('m2', 'Master Mode 2', 20, 1500000),
('m3', 'Master Mode 3', 22, 2500000),
('m4', 'Master Mode 4', 24, 4000000),
('m5', 'Master Mode 5', 26, 6000000),
('m6', 'Master Mode 6', 28, 9000000),
('m7', 'Master Mode 7', 30, 15000000);
