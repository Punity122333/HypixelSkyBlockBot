CREATE TABLE IF NOT EXISTS inventory_item_reforged_stats (
    inventory_item_id INTEGER PRIMARY KEY,
    reforged_stats TEXT NOT NULL,
    reforged_at INTEGER NOT NULL,
    FOREIGN KEY (inventory_item_id) REFERENCES inventory_items(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS boss_rotation_kills (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    boss_id TEXT NOT NULL,
    damage_dealt INTEGER NOT NULL,
    time_taken INTEGER NOT NULL,
    killed_at INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES players(user_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_boss_rotation_user ON boss_rotation_kills(user_id, boss_id);
CREATE INDEX IF NOT EXISTS idx_boss_rotation_boss ON boss_rotation_kills(boss_id);

CREATE TABLE IF NOT EXISTS museum_donations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    item_id TEXT NOT NULL,
    rarity TEXT NOT NULL,
    points INTEGER NOT NULL,
    donated_at INTEGER NOT NULL,
    UNIQUE(user_id, item_id),
    FOREIGN KEY (user_id) REFERENCES players(user_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS museum_milestones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    milestone INTEGER NOT NULL,
    claimed_at INTEGER NOT NULL,
    UNIQUE(user_id, milestone),
    FOREIGN KEY (user_id) REFERENCES players(user_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_museum_user ON museum_donations(user_id);
CREATE INDEX IF NOT EXISTS idx_museum_points ON museum_donations(points DESC);
CREATE INDEX IF NOT EXISTS idx_museum_milestones ON museum_milestones(user_id);
