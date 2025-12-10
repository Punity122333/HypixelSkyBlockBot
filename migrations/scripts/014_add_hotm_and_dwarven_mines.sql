CREATE TABLE IF NOT EXISTS player_hotm (
    user_id INTEGER PRIMARY KEY,
    hotm_level INTEGER DEFAULT 1,
    hotm_xp INTEGER DEFAULT 0,
    hotm_tier INTEGER DEFAULT 1,
    token_of_the_mountain INTEGER DEFAULT 0,
    powder_mithril INTEGER DEFAULT 0,
    powder_gemstone INTEGER DEFAULT 0,
    powder_glacite INTEGER DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES players(user_id)
);

CREATE TABLE IF NOT EXISTS player_hotm_perks (
    user_id INTEGER,
    perk_id TEXT,
    perk_level INTEGER DEFAULT 0,
    PRIMARY KEY (user_id, perk_id),
    FOREIGN KEY (user_id) REFERENCES players(user_id)
);

CREATE TABLE IF NOT EXISTS hotm_perks (
    perk_id TEXT PRIMARY KEY,
    perk_name TEXT NOT NULL,
    max_level INTEGER NOT NULL,
    tier INTEGER NOT NULL,
    cost_formula TEXT,
    description TEXT,
    stat_bonuses TEXT,
    unlock_requirements TEXT
);

CREATE TABLE IF NOT EXISTS dwarven_mines_progress (
    user_id INTEGER PRIMARY KEY,
    commissions_completed INTEGER DEFAULT 0,
    reputation INTEGER DEFAULT 0,
    king_yolkar_unlocked INTEGER DEFAULT 0,
    mithril_unlocked INTEGER DEFAULT 1,
    titanium_unlocked INTEGER DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES players(user_id)
);

CREATE TABLE IF NOT EXISTS crystal_hollows_progress (
    user_id INTEGER PRIMARY KEY,
    nucleus_runs INTEGER DEFAULT 0,
    crystals_found INTEGER DEFAULT 0,
    jungle_unlocked INTEGER DEFAULT 0,
    mithril_deposits_unlocked INTEGER DEFAULT 0,
    precursor_unlocked INTEGER DEFAULT 0,
    magma_fields_unlocked INTEGER DEFAULT 0,
    goblin_holdout_unlocked INTEGER DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES players(user_id)
);

CREATE TABLE IF NOT EXISTS player_commissions (
    commission_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    commission_type TEXT,
    requirement INTEGER,
    progress INTEGER DEFAULT 0,
    reward_mithril INTEGER DEFAULT 0,
    reward_coins INTEGER DEFAULT 0,
    completed INTEGER DEFAULT 0,
    expires_at INTEGER,
    FOREIGN KEY (user_id) REFERENCES players(user_id)
);

ALTER TABLE mob_locations ADD COLUMN level INTEGER DEFAULT 1;

CREATE TABLE IF NOT EXISTS mob_level_scaling (
    level INTEGER PRIMARY KEY,
    health_multiplier REAL DEFAULT 1.0,
    damage_multiplier REAL DEFAULT 1.0,
    defense_multiplier REAL DEFAULT 1.0,
    coins_multiplier REAL DEFAULT 1.0,
    xp_multiplier REAL DEFAULT 1.0
);

INSERT INTO mob_level_scaling (level, health_multiplier, damage_multiplier, defense_multiplier, coins_multiplier, xp_multiplier) VALUES
(1, 1.0, 1.0, 1.0, 1.0, 1.0),
(5, 1.5, 1.2, 1.2, 1.3, 1.2),
(10, 2.0, 1.5, 1.5, 1.6, 1.5),
(15, 2.5, 1.8, 1.8, 2.0, 1.8),
(20, 3.0, 2.0, 2.0, 2.5, 2.0),
(25, 3.5, 2.3, 2.3, 3.0, 2.3),
(30, 4.0, 2.6, 2.6, 3.5, 2.6),
(35, 4.5, 3.0, 3.0, 4.0, 3.0),
(40, 5.0, 3.5, 3.5, 4.5, 3.5),
(45, 5.5, 4.0, 4.0, 5.0, 4.0),
(50, 6.0, 4.5, 4.5, 5.5, 4.5),
(60, 7.0, 5.0, 5.0, 6.5, 5.0),
(70, 8.0, 6.0, 6.0, 7.5, 6.0),
(80, 9.0, 7.0, 7.0, 8.5, 7.0),
(90, 10.0, 8.0, 8.0, 10.0, 8.0),
(100, 12.0, 10.0, 10.0, 12.0, 10.0);

INSERT INTO hotm_perks (perk_id, perk_name, max_level, tier, cost_formula, description, stat_bonuses, unlock_requirements) VALUES
('mining_speed', 'Mining Speed', 50, 1, 'level', 'Grants +20 Mining Speed per level', '{"mining_speed": 20}', '{}'),
('mining_fortune', 'Mining Fortune', 50, 1, 'level', 'Grants +5 Mining Fortune per level', '{"mining_fortune": 5}', '{}'),
('titanium_insanium', 'Titanium Insanium', 20, 2, 'level * 2', 'Increases Titanium drop chance', '{"titanium_chance": 2}', '{"hotm_tier": 2}'),
('efficient_miner', 'Efficient Miner', 100, 1, 'level', 'Reduces mining speed by 1% per level', '{"mining_speed_percent": 1}', '{}'),
('orbiter', 'Orbiter', 80, 3, 'level * 3', 'Increases Fallen Star spawn rate', '{"orb_chance": 0.5}', '{"hotm_tier": 3}'),
('seasoned_mineman', 'Seasoned Mineman', 100, 2, 'level * 2', 'Grants +5 Mining Wisdom per level', '{"mining_wisdom": 5}', '{"hotm_tier": 2}'),
('powder_buff', 'Powder Buff', 50, 2, 'level * 2', 'Increases powder gained by 1% per level', '{"powder_percent": 1}', '{"hotm_tier": 2}'),
('mining_speed_boost', 'Mining Speed Boost', 1, 4, '50', 'Grants Mining Speed Boost ability', '{"ability": "mining_speed_boost"}', '{"hotm_tier": 4}'),
('vein_seeker', 'Vein Seeker', 1, 5, '100', 'Shows ores through walls', '{"ability": "vein_seeker"}', '{"hotm_tier": 5}'),
('maniac_miner', 'Maniac Miner', 1, 6, '100', 'Break 5 blocks at once', '{"ability": "maniac_miner"}', '{"hotm_tier": 6}'),
('daily_powder', 'Daily Powder', 100, 2, 'level', 'Grants daily powder', '{"daily_powder": 500}', '{"hotm_tier": 2}'),
('precision_mining', 'Precision Mining', 1, 7, '150', 'Mine single blocks precisely', '{"ability": "precision_mining"}', '{"hotm_tier": 7}'),
('mining_fortune_2', 'Luck of the Cave', 50, 3, 'level * 3', 'Grants +4 Mining Fortune per level', '{"mining_fortune": 4}', '{"hotm_tier": 3}'),
('crystallized', 'Crystallized', 30, 4, 'level * 5', 'Increases Gemstone drops', '{"gemstone_fortune": 10}', '{"hotm_tier": 4}'),
('professional', 'Professional', 140, 1, 'level', 'Grants +50 Mining Speed per level', '{"mining_speed": 50}', '{}'),
('lonesome_miner', 'Lonesome Miner', 45, 5, 'level * 5', 'Grants stats when alone', '{"strength": 5, "defense": 5}', '{"hotm_tier": 5}'),
('great_explorer', 'Great Explorer', 20, 4, 'level * 4', 'Grants +20 Speed in caves', '{"speed": 20}', '{"hotm_tier": 4}'),
('fortunate', 'Fortunate', 20, 4, 'level * 5', 'Grants +20 Mining Fortune per level', '{"mining_fortune": 20}', '{"hotm_tier": 4}'),
('gemstone_infusion', 'Gemstone Infusion', 1, 7, '200', 'Gemstones grant extra stats', '{"ability": "gemstone_infusion"}', '{"hotm_tier": 7}'),
('mining_madness', 'Mining Madness', 1, 7, '200', 'Toggle: 50% speed, 33% fortune', '{"ability": "mining_madness"}', '{"hotm_tier": 7}');

UPDATE mob_locations SET level = 1 WHERE mob_id IN ('zombie', 'skeleton', 'spider');
UPDATE mob_locations SET level = 5 WHERE mob_id IN ('cave_spider', 'creeper');
UPDATE mob_locations SET level = 10 WHERE mob_id IN ('enderman', 'blaze');
UPDATE mob_locations SET level = 15 WHERE mob_id IN ('zombie_pigman', 'wither_skeleton');
UPDATE mob_locations SET level = 20 WHERE mob_id IN ('magma_cube', 'ghast');
UPDATE mob_locations SET level = 25 WHERE mob_id IN ('zealot');
UPDATE mob_locations SET level = 30 WHERE mob_id IN ('broodfather', 'tarantula');
UPDATE mob_locations SET level = 50 WHERE mob_id IN ('ender_dragon', 'wither');
UPDATE mob_locations SET level = 35 WHERE mob_id IN ('revenant', 'sven');
UPDATE mob_locations SET level = 45 WHERE mob_id IN ('voidgloom');
UPDATE mob_locations SET level = 60 WHERE mob_id IN ('inferno');
