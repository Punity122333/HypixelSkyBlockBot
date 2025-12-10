CREATE TABLE player_achievements (
    user_id INTEGER NOT NULL,
    achievement_id TEXT NOT NULL,
    unlocked_at INTEGER NOT NULL,
    PRIMARY KEY (user_id, achievement_id),
    FOREIGN KEY (user_id) REFERENCES players(user_id) ON DELETE CASCADE
);

CREATE TABLE player_unlocked_locations (
    user_id INTEGER NOT NULL,
    location_id TEXT NOT NULL,
    unlocked_at INTEGER NOT NULL,
    PRIMARY KEY (user_id, location_id),
    FOREIGN KEY (user_id) REFERENCES players(user_id) ON DELETE CASCADE
);

CREATE TABLE player_progression_new (
    user_id INTEGER PRIMARY KEY,
    tutorial_completed BOOLEAN DEFAULT 0,
    first_mine_date INTEGER,
    first_farm_date INTEGER,
    first_auction_date INTEGER,
    first_trade_date INTEGER,
    FOREIGN KEY (user_id) REFERENCES players(user_id) ON DELETE CASCADE
);

INSERT INTO player_progression_new (user_id, tutorial_completed, first_mine_date, first_farm_date, first_auction_date, first_trade_date)
SELECT user_id, tutorial_completed, first_mine_date, first_farm_date, first_auction_date, first_trade_date
FROM player_progression;

DROP TABLE player_progression;
ALTER TABLE player_progression_new RENAME TO player_progression;

CREATE INDEX idx_player_achievements ON player_achievements(user_id);
CREATE INDEX idx_player_locations ON player_unlocked_locations(user_id);
