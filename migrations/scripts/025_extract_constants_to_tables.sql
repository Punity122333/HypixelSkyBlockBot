CREATE TABLE IF NOT EXISTS reforge_rarity_stat_ranges (
    rarity TEXT PRIMARY KEY,
    strength_min INTEGER NOT NULL,
    strength_max INTEGER NOT NULL,
    crit_damage_min INTEGER NOT NULL,
    crit_damage_max INTEGER NOT NULL,
    defense_min INTEGER NOT NULL,
    defense_max INTEGER NOT NULL,
    health_min INTEGER NOT NULL,
    health_max INTEGER NOT NULL
);

INSERT OR REPLACE INTO reforge_rarity_stat_ranges VALUES
('COMMON', 1, 5, 1, 5, 1, 5, 5, 15),
('UNCOMMON', 3, 8, 3, 8, 3, 8, 10, 25),
('RARE', 5, 12, 5, 12, 5, 12, 15, 35),
('EPIC', 8, 18, 8, 18, 8, 18, 25, 50),
('LEGENDARY', 12, 25, 12, 25, 12, 25, 35, 70),
('MYTHIC', 15, 35, 15, 35, 15, 35, 50, 100);

CREATE TABLE IF NOT EXISTS museum_milestone_rewards (
    milestone INTEGER PRIMARY KEY,
    coins INTEGER NOT NULL,
    title TEXT NOT NULL
);

INSERT OR REPLACE INTO museum_milestone_rewards VALUES
(10, 10000, '🎨 Novice Collector'),
(25, 25000, '🏛️ Museum Enthusiast'),
(50, 50000, '💎 Master Curator'),
(100, 100000, '👑 Legendary Collector'),
(200, 250000, '🌟 Museum Tycoon'),
(500, 1000000, '⭐ Grand Archivist');

CREATE TABLE IF NOT EXISTS museum_rarity_points (
    rarity TEXT PRIMARY KEY,
    points INTEGER NOT NULL
);

INSERT OR REPLACE INTO museum_rarity_points VALUES
('COMMON', 1),
('UNCOMMON', 2),
('RARE', 5),
('EPIC', 10),
('LEGENDARY', 25),
('MYTHIC', 50);

CREATE TABLE IF NOT EXISTS dungeon_floors (
    floor INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    min_level INTEGER NOT NULL,
    recommended_level INTEGER NOT NULL
);

INSERT OR REPLACE INTO dungeon_floors VALUES
(1, 'Floor 1', 0, 5),
(2, 'Floor 2', 3, 10),
(3, 'Floor 3', 7, 15),
(4, 'Floor 4', 10, 20),
(5, 'Floor 5', 15, 25),
(6, 'Floor 6', 20, 30),
(7, 'Floor 7', 25, 35);

CREATE TABLE IF NOT EXISTS item_lore_prefixes (
    prefix_id TEXT PRIMARY KEY,
    display_name TEXT NOT NULL,
    color TEXT NOT NULL,
    stats TEXT NOT NULL
);

INSERT OR REPLACE INTO item_lore_prefixes VALUES
('arcane', '⚡ Arcane', 'blue', '{"intelligence": 5, "ability_damage": 3}'),
('blazing', '🔥 Blazing', 'red', '{"strength": 3, "crit_damage": 5}'),
('bloodbound', '🩸 Bloodbound', 'dark_red', '{"health": 20, "ferocity": 2}'),
('frozen', '❄️ Frozen', 'cyan', '{"intelligence": 3, "defense": 5}'),
('gilded', '✨ Gilded', 'gold', '{"magic_find": 2, "pet_luck": 1}'),
('hallowed', '✝️ Hallowed', 'white', '{"defense": 5, "health": 15}'),
('titanic', '⚔️ Titanic', 'purple', '{"strength": 5, "health": 10}'),
('swift', '💨 Swift', 'green', '{"speed": 10, "attack_speed": 5}'),
('vampiric', '🧛 Vampiric', 'dark_red', '{"health": 25, "strength": 2}'),
('wise', '🧙 Wise', 'purple', '{"intelligence": 10, "mana": 50}'),
('lucky', '🍀 Lucky', 'green', '{"magic_find": 5, "pet_luck": 3}'),
('powerful', '💪 Powerful', 'red', '{"strength": 7, "crit_damage": 10}'),
('fortified', '🛡️ Fortified', 'gray', '{"defense": 10, "true_defense": 3}'),
('prosperous', '💰 Prosperous', 'gold', '{"mining_fortune": 10, "farming_fortune": 10}');

CREATE TABLE IF NOT EXISTS item_lore_suffixes (
    suffix_id TEXT PRIMARY KEY,
    display_name TEXT NOT NULL,
    stats TEXT NOT NULL
);

INSERT OR REPLACE INTO item_lore_suffixes VALUES
('the_end', 'of the End', '{"health": 10, "defense": 5}'),
('the_nether', 'of the Nether', '{"strength": 5, "ferocity": 2}'),
('dragons', 'of Dragons', '{"health": 20, "strength": 10}'),
('the_depths', 'of the Depths', '{"fishing_speed": 10, "sea_creature_chance": 5}'),
('mining', 'of Mining', '{"mining_speed": 10, "mining_fortune": 15}'),
('farming', 'of Farming', '{"farming_fortune": 15, "speed": 5}'),
('combat', 'of Combat', '{"crit_chance": 5, "crit_damage": 15}'),
('wealth', 'of Wealth', '{"magic_find": 3}');

CREATE TABLE IF NOT EXISTS coop_permissions (
    role TEXT PRIMARY KEY,
    permissions TEXT NOT NULL
);

INSERT OR REPLACE INTO coop_permissions VALUES
('owner', '["manage_members", "manage_permissions", "use_bank", "manage_minions", "manage_island", "invite_members", "kick_members"]'),
('admin', '["use_bank", "manage_minions", "manage_island", "invite_members"]'),
('member', '["use_bank", "manage_minions"]'),
('guest', '[]');

CREATE TABLE IF NOT EXISTS boss_rotation_data (
    boss_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    emoji TEXT NOT NULL,
    health INTEGER NOT NULL,
    damage INTEGER NOT NULL,
    defense INTEGER NOT NULL,
    rewards_coins INTEGER NOT NULL,
    rewards_xp INTEGER NOT NULL,
    rotation_order INTEGER NOT NULL
);

INSERT OR REPLACE INTO boss_rotation_data VALUES
('crypt_ghoul_king', 'Crypt Ghoul King', '🧟', 500000, 1500, 200, 50000, 5000, 0),
('spider_queen', 'Spider Queen', '🕷️', 750000, 2000, 300, 75000, 7500, 1),
('blaze_lord', 'Blaze Lord', '🔥', 1000000, 2500, 400, 100000, 10000, 2),
('ender_warden', 'Ender Warden', '👾', 1250000, 3000, 500, 125000, 12500, 3);

CREATE TABLE IF NOT EXISTS item_stat_mutations (
    stat TEXT PRIMARY KEY,
    min_value INTEGER NOT NULL,
    max_value INTEGER NOT NULL,
    weight INTEGER NOT NULL
);

INSERT OR REPLACE INTO item_stat_mutations VALUES
('strength', 1, 10, 10),
('crit_damage', 2, 20, 8),
('health', 5, 50, 10),
('defense', 2, 15, 9),
('intelligence', 2, 25, 7),
('mining_fortune', 3, 20, 6),
('farming_fortune', 3, 20, 6),
('foraging_fortune', 3, 20, 6),
('magic_find', 1, 5, 3),
('pet_luck', 1, 3, 2),
('speed', 5, 15, 5),
('attack_speed', 2, 10, 4),
('ferocity', 1, 5, 4);

CREATE INDEX IF NOT EXISTS idx_boss_rotation_order ON boss_rotation_data(rotation_order);
