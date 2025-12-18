CREATE TABLE IF NOT EXISTS hotm_tiers (
    tier INTEGER PRIMARY KEY,
    xp_required INTEGER NOT NULL,
    token_reward INTEGER NOT NULL
);

INSERT OR IGNORE INTO hotm_tiers (tier, xp_required, token_reward) VALUES
(1, 0, 2),
(2, 5000, 2),
(3, 15000, 2),
(4, 35000, 2),
(5, 70000, 2),
(6, 150000, 2),
(7, 300000, 2),
(8, 550000, 2),
(9, 1000000, 2),
(10, 1500000, 2);
