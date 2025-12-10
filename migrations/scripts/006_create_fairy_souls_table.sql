-- Migration script to create the correct fairy_souls table
CREATE TABLE IF NOT EXISTS fairy_souls (
    user_id INTEGER,
    location TEXT,
    collected_at INTEGER,
    souls_collected INTEGER,
    PRIMARY KEY (user_id, location)
);

-- Optionally, you can drop the old table if it exists and is incorrect
-- DROP TABLE IF EXISTS fairy_souls;
