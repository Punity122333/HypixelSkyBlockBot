-- Migration to fix fairy_souls table schema
-- Step 1: Rename old table
ALTER TABLE fairy_souls RENAME TO fairy_souls_old;

-- Step 2: Create new table
CREATE TABLE fairy_souls (
    user_id INTEGER,
    location TEXT,
    collected_at INTEGER,
    souls_collected INTEGER,
    PRIMARY KEY (user_id, location)
);

-- Step 3: Copy data if columns exist
INSERT INTO fairy_souls (user_id, location, collected_at, souls_collected)
SELECT user_id, location, collected_at, souls_collected FROM fairy_souls_old
WHERE user_id IS NOT NULL AND location IS NOT NULL;

-- Step 4: Drop old table
DROP TABLE fairy_souls_old;
