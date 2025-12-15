ALTER TABLE player_economy ADD COLUMN auction_wins INTEGER DEFAULT 0;
ALTER TABLE player_economy ADD COLUMN bazaar_orders_completed INTEGER DEFAULT 0;
ALTER TABLE player_economy ADD COLUMN bazaar_profit INTEGER DEFAULT 0;
ALTER TABLE player_economy ADD COLUMN quests_completed INTEGER DEFAULT 0;
ALTER TABLE player_economy ADD COLUMN museum_donations INTEGER DEFAULT 0;

ALTER TABLE player_stats ADD COLUMN boss_kills INTEGER DEFAULT 0;
ALTER TABLE player_stats ADD COLUMN total_crafts INTEGER DEFAULT 0;
ALTER TABLE player_stats ADD COLUMN total_enchants INTEGER DEFAULT 0;
ALTER TABLE player_stats ADD COLUMN total_reforges INTEGER DEFAULT 0;
ALTER TABLE player_stats ADD COLUMN pets_owned INTEGER DEFAULT 0;
ALTER TABLE player_stats ADD COLUMN islands_visited INTEGER DEFAULT 0;

ALTER TABLE player_dungeon_stats ADD COLUMN parties_joined INTEGER DEFAULT 0;
ALTER TABLE player_dungeon_stats ADD COLUMN parties_hosted INTEGER DEFAULT 0;

CREATE TABLE IF NOT EXISTS player_tracking (
    user_id INTEGER PRIMARY KEY,
    login_streak INTEGER DEFAULT 0,
    last_login_date TEXT,
    total_logins INTEGER DEFAULT 0,
    prestige_level INTEGER DEFAULT 0,
    collections_tier_5 INTEGER DEFAULT 0,
    collections_maxed INTEGER DEFAULT 0,
    minion_slots INTEGER DEFAULT 5,
    FOREIGN KEY (user_id) REFERENCES players(user_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_player_tracking_user ON player_tracking(user_id);
