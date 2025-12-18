CREATE TABLE IF NOT EXISTS dwarven_commission_types (
    commission_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    mithril_powder_reward INTEGER NOT NULL,
    coins_reward INTEGER NOT NULL,
    amount_min INTEGER NOT NULL,
    amount_max INTEGER NOT NULL
);

INSERT OR IGNORE INTO dwarven_commission_types (commission_id, name, description, mithril_powder_reward, coins_reward, amount_min, amount_max) VALUES
('mithril_mining', 'Mithril Miner', 'Mine {amount} Mithril', 500, 2000, 100, 250),
('titanium_mining', 'Titanium Collector', 'Mine {amount} Titanium', 800, 3500, 50, 100),
('goblin_slayer', 'Goblin Slayer', 'Kill {amount} Goblins', 400, 1500, 30, 60),
('hard_stone_mining', 'Hard Stone Miner', 'Mine {amount} Hard Stone', 300, 1000, 200, 400),
('treasure_hunter', 'Treasure Hunter', 'Find {amount} Treasures', 600, 2500, 5, 15),
('lapis_mining', 'Lapis Collector', 'Mine {amount} Lapis', 350, 1200, 150, 300),
('redstone_mining', 'Redstone Collector', 'Mine {amount} Redstone', 350, 1200, 150, 300);
