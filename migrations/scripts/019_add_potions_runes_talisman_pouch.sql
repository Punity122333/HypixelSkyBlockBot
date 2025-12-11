CREATE TABLE IF NOT EXISTS active_potions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    potion_id TEXT NOT NULL,
    level INTEGER DEFAULT 1,
    duration INTEGER NOT NULL,
    applied_at INTEGER NOT NULL,
    expires_at INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES players(user_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS player_talisman_pouch (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    talisman_id TEXT NOT NULL,
    slot INTEGER NOT NULL,
    equipped INTEGER DEFAULT 1,
    FOREIGN KEY (user_id) REFERENCES players(user_id) ON DELETE CASCADE,
    UNIQUE(user_id, slot),
    UNIQUE(user_id, talisman_id)
);

CREATE INDEX IF NOT EXISTS idx_active_potions_user ON active_potions(user_id);
CREATE INDEX IF NOT EXISTS idx_active_potions_expires ON active_potions(expires_at);
CREATE INDEX IF NOT EXISTS idx_talisman_pouch_user ON player_talisman_pouch(user_id);
