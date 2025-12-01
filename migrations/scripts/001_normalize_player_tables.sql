CREATE TABLE player_stats (
    user_id INTEGER PRIMARY KEY,
    health INTEGER DEFAULT 100,
    max_health INTEGER DEFAULT 100,
    mana INTEGER DEFAULT 20,
    max_mana INTEGER DEFAULT 20,
    defense INTEGER DEFAULT 0,
    strength INTEGER DEFAULT 5,
    crit_chance INTEGER DEFAULT 5,
    crit_damage INTEGER DEFAULT 50,
    intelligence INTEGER DEFAULT 0,
    speed INTEGER DEFAULT 100,
    sea_creature_chance INTEGER DEFAULT 5,
    magic_find INTEGER DEFAULT 0,
    pet_luck INTEGER DEFAULT 0,
    ferocity INTEGER DEFAULT 0,
    ability_damage INTEGER DEFAULT 0,
    mining_speed INTEGER DEFAULT 0,
    mining_fortune INTEGER DEFAULT 0,
    farming_fortune INTEGER DEFAULT 0,
    foraging_fortune INTEGER DEFAULT 0,
    fishing_speed INTEGER DEFAULT 0,
    attack_speed INTEGER DEFAULT 0,
    true_defense INTEGER DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES players(user_id) ON DELETE CASCADE
);

INSERT INTO player_stats (
    user_id, health, max_health, mana, max_mana, defense, strength,
    mining_fortune, farming_fortune, foraging_fortune, fishing_speed
)
SELECT 
    user_id, 
    COALESCE(health, 100), 
    COALESCE(max_health, 100), 
    COALESCE(mana, 20), 
    COALESCE(max_mana, 20), 
    COALESCE(defense, 0), 
    COALESCE(strength, 5),
    COALESCE(mining_fortune, 0), 
    COALESCE(farming_fortune, 0), 
    COALESCE(foraging_fortune, 0), 
    COALESCE(fishing_speed, 0)
FROM players;

CREATE TABLE player_economy (
    user_id INTEGER PRIMARY KEY,
    coins INTEGER DEFAULT 100,
    bank INTEGER DEFAULT 0,
    bank_capacity INTEGER DEFAULT 5000,
    total_earned INTEGER DEFAULT 0,
    total_spent INTEGER DEFAULT 0,
    trading_reputation INTEGER DEFAULT 0,
    merchant_level INTEGER DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES players(user_id) ON DELETE CASCADE
);

INSERT INTO player_economy (user_id, coins, bank, bank_capacity, total_earned, total_spent, trading_reputation, merchant_level)
SELECT user_id, coins, bank, bank_capacity, total_earned, total_spent, trading_reputation, merchant_level
FROM players;

CREATE TABLE player_dungeon_stats (
    user_id INTEGER PRIMARY KEY,
    catacombs_level INTEGER DEFAULT 0,
    catacombs_xp INTEGER DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES players(user_id) ON DELETE CASCADE
);

INSERT INTO player_dungeon_stats (user_id, catacombs_level, catacombs_xp)
SELECT user_id, catacombs_level, catacombs_xp
FROM players;

CREATE TABLE player_slayer_progress (
    user_id INTEGER NOT NULL,
    slayer_type TEXT NOT NULL,
    xp INTEGER DEFAULT 0,
    level INTEGER DEFAULT 0,
    total_kills INTEGER DEFAULT 0,
    PRIMARY KEY (user_id, slayer_type),
    FOREIGN KEY (user_id) REFERENCES players(user_id) ON DELETE CASCADE
);

CREATE TABLE players_new (
    user_id INTEGER PRIMARY KEY,
    username TEXT NOT NULL,
    created_at INTEGER NOT NULL
);

INSERT INTO players_new (user_id, username, created_at)
SELECT user_id, username, COALESCE(created_at, strftime('%s', 'now'))
FROM players;

DROP TABLE players;
ALTER TABLE players_new RENAME TO players;

CREATE INDEX idx_players_username ON players(username);
CREATE INDEX idx_player_stats_user ON player_stats(user_id);
CREATE INDEX idx_player_economy_user ON player_economy(user_id);
CREATE INDEX idx_player_dungeon_stats_user ON player_dungeon_stats(user_id);
CREATE INDEX idx_player_slayer_progress ON player_slayer_progress(user_id, slayer_type);
