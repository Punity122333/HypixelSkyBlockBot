-- Remove duplicate columns from players table that are now in player_economy and player_stats
-- These columns were moved during normalization but never removed from the original table

-- SQLite doesn't support DROP COLUMN directly, so we need to recreate the table
-- Create a new players table with only the columns we want
CREATE TABLE players_new (
    user_id INTEGER PRIMARY KEY,
    username TEXT NOT NULL,
    created_at INTEGER NOT NULL,
    achievements TEXT DEFAULT '{}'
);

-- Copy data from old table to new table
INSERT INTO players_new (user_id, username, created_at, achievements)
SELECT user_id, username, created_at, COALESCE(achievements, '{}')
FROM players;

-- Drop old table
DROP TABLE players;

-- Rename new table to original name
ALTER TABLE players_new RENAME TO players;

-- Recreate any indexes that might have existed
CREATE INDEX IF NOT EXISTS idx_players_username ON players(username);
