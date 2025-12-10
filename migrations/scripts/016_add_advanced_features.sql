CREATE TABLE IF NOT EXISTS item_modifiers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    inventory_item_id INTEGER NOT NULL,
    modifier_type TEXT NOT NULL,
    modifier_name TEXT NOT NULL,
    stat_bonuses TEXT,
    created_at INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES players(user_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS market_price_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_id TEXT NOT NULL,
    price REAL NOT NULL,
    volume INTEGER DEFAULT 0,
    timestamp INTEGER NOT NULL,
    source TEXT DEFAULT 'bazaar'
);

CREATE TABLE IF NOT EXISTS player_networth_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    networth REAL NOT NULL,
    timestamp INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES players(user_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS player_badges (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    badge_id TEXT NOT NULL,
    unlocked_at INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES players(user_id) ON DELETE CASCADE,
    UNIQUE(user_id, badge_id)
);

CREATE TABLE IF NOT EXISTS game_badges (
    badge_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    category TEXT DEFAULT 'Other'
);

INSERT OR IGNORE INTO game_badges (badge_id, name, description, category) VALUES
('first_death', '💀 First Blood', 'Died for the first time', 'Deaths'),
('death_100', '💀💀 Death Enthusiast', 'Died 100 times', 'Deaths'),
('death_1000', '💀💀💀 Immortal Spirit', 'Died 1000 times', 'Deaths'),
('networth_1k', '💰 Starting Strong', '1K Networth', 'Wealth'),
('networth_10k', '💎 Getting Rich', '10K Networth', 'Wealth'),
('networth_100k', '💵 Wealthy', '100K Networth', 'Wealth'),
('networth_1m', '📈 1M Networth Club', 'Reached 1 million coins networth', 'Wealth'),
('networth_10m', '🏆 Multi-Millionaire', '10M Networth', 'Wealth'),
('broke', '🥺 Broke', 'Had exactly 0 coins', 'Cursed'),
('first_minion', '🤖 Minion Master', 'Placed first minion', 'Minions'),
('minion_10', '🤖🤖 Minion Army', 'Placed 10 minions', 'Minions'),
('first_auction', '🔨 Auctioneer', 'Created first auction', 'Trading'),
('auction_100', '💼 Business Tycoon', 'Created 100 auctions', 'Trading'),
('bazaar_flip', '📊 Bazaar Flipper', 'Made first bazaar profit', 'Trading'),
('bazaar_1m_profit', '💹 Flip Master', 'Made 1M profit from bazaar', 'Trading'),
('merchant_level_10', '🏪 Master Merchant', 'Reached merchant level 10', 'Trading'),
('skill_50', '⭐ Skilled', 'Reached level 50 in any skill', 'Skills'),
('all_skills_25', '🌟 Jack of All Trades', 'All skills level 25+', 'Skills'),
('first_fairy_soul', '✨ Soul Collector', 'Found first fairy soul', 'Exploration'),
('fairy_souls_50', '✨✨ Soul Hunter', 'Collected 50 fairy souls', 'Exploration'),
('dungeon_1', '⚔️ Dungeon Explorer', 'Completed first dungeon', 'Combat'),
('dungeon_100', '⚔️⚔️ Dungeon Veteran', 'Completed 100 dungeons', 'Combat'),
('slayer_1000', '🗡️ Slayer', 'Killed 1000 slayer bosses', 'Combat'),
('tax_payer', '💸 Tax Payer (Once)', 'Paid taxes at least once', 'Cursed'),
('gambler', '🎲 Gambler', 'Lost 100k+ in a single day', 'Cursed'),
('hoarder', '📦 Hoarder', 'Inventory completely full', 'Cursed'),
('speed_demon', '💨 Speed Demon', 'Reached 500 speed', 'Stats'),
('tank', '🛡️ Tank', 'Reached 1000 defense', 'Stats'),
('glass_cannon', '⚡ Glass Cannon', '500+ strength but <100 defense', 'Stats'),
('wizard', '🧙 Archmage', 'Reached 1000 intelligence', 'Stats'),
('crit_master', '💥 Crit Master', '100% crit chance', 'Stats'),
('pet_legendary', '🐉 Legendary Pet Owner', 'Owned a legendary pet', 'Other'),
('collection_max', '📚 Master Collector', 'Maxed out a collection', 'Other'),
('island_upgrade_10', '🏝️ Island Builder', 'Upgraded island 10 times', 'Other'),
('early_bird', '🌅 Early Bird', 'Claimed daily reward 30 days in a row', 'Other'),
('party_finder_host', '👥 Party Leader', 'Hosted 50 dungeon parties', 'Other'),
('coop_founder', '🤝 Cooperative', 'Founded a co-op', 'Other'),
('compactor_user', '🗜️ Efficiency Expert', 'Used a super compactor', 'Other');

CREATE TABLE IF NOT EXISTS dungeon_parties (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    party_leader INTEGER NOT NULL,
    dungeon_floor INTEGER NOT NULL,
    class_requirements TEXT,
    min_catacombs_level INTEGER DEFAULT 0,
    description TEXT,
    created_at INTEGER NOT NULL,
    status TEXT DEFAULT 'open',
    FOREIGN KEY (party_leader) REFERENCES players(user_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS dungeon_party_members (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    party_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    dungeon_class TEXT NOT NULL,
    joined_at INTEGER NOT NULL,
    FOREIGN KEY (party_id) REFERENCES dungeon_parties(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES players(user_id) ON DELETE CASCADE,
    UNIQUE(party_id, user_id)
);

CREATE TABLE IF NOT EXISTS coops (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    coop_name TEXT NOT NULL,
    created_at INTEGER NOT NULL,
    shared_bank INTEGER DEFAULT 0,
    bank_capacity INTEGER DEFAULT 10000
);

CREATE TABLE IF NOT EXISTS coop_members (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    coop_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    role TEXT DEFAULT 'member',
    permissions TEXT,
    joined_at INTEGER NOT NULL,
    FOREIGN KEY (coop_id) REFERENCES coops(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES players(user_id) ON DELETE CASCADE,
    UNIQUE(coop_id, user_id)
);

CREATE TABLE IF NOT EXISTS minion_upgrades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    minion_id INTEGER NOT NULL,
    upgrade_type TEXT NOT NULL,
    upgrade_value TEXT,
    applied_at INTEGER NOT NULL,
    FOREIGN KEY (minion_id) REFERENCES user_minions(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS game_compactors (
    compactor_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    tier INTEGER NOT NULL,
    multiplier INTEGER NOT NULL,
    description TEXT
);

INSERT OR IGNORE INTO game_compactors (compactor_id, name, tier, multiplier, description) VALUES
('super_compactor_3000', 'Super Compactor 3000', 1, 160, 'Compacts items into enchanted forms automatically'),
('compactor_4000', 'Compactor 4000', 2, 640, 'Compacts items into enchanted blocks'),
('compactor_5000', 'Compactor 5000', 3, 25600, 'Compacts items into enchanted hyper-forms');

CREATE TABLE IF NOT EXISTS game_minion_fuels (
    fuel_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    speed_boost REAL NOT NULL,
    duration INTEGER NOT NULL,
    description TEXT
);

INSERT OR IGNORE INTO game_minion_fuels (fuel_id, name, speed_boost, duration, description) VALUES
('foul_flesh', 'Foul Flesh', 0.9, 43200, '-10% time between actions'),
('catalyst', 'Catalyst', 0.99, 10800, '-1% time between actions'),
('hamster_wheel', 'Hamster Wheel', 0.75, 28800, '-25% time between actions'),
('magma_bucket', 'Magma Bucket', 0.75, 172800, '-25% time between actions'),
('plasma_bucket', 'Plasma Bucket', 0.65, 259200, '-35% time between actions'),
('solar_panel', 'Solar Panel', 0.75, 432000, '-25% time between actions'),
('enchanted_lava_bucket', 'Enchanted Lava Bucket', 0.75, 86400, '-25% time between actions');

CREATE TABLE IF NOT EXISTS game_minion_skins (
    skin_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    minion_type TEXT NOT NULL,
    rarity TEXT DEFAULT 'common',
    description TEXT
);

INSERT OR IGNORE INTO game_minion_skins (skin_id, name, minion_type, rarity, description) VALUES
('farming_islands_wheat', 'Farming Islands Wheat Minion', 'wheat', 'epic', 'A festive wheat minion skin'),
('spooky_cobblestone', 'Spooky Cobblestone Minion', 'cobblestone', 'rare', 'A spooky halloween skin'),
('winter_snow', 'Winter Snow Minion', 'snow', 'epic', 'A frosty winter skin');

CREATE INDEX idx_item_modifiers_user ON item_modifiers(user_id);
CREATE INDEX idx_market_price_history_item ON market_price_history(item_id, timestamp);
CREATE INDEX idx_player_networth_user ON player_networth_history(user_id, timestamp);
CREATE INDEX idx_player_badges_user ON player_badges(user_id);
CREATE INDEX idx_dungeon_parties_leader ON dungeon_parties(party_leader, status);
CREATE INDEX idx_dungeon_party_members_party ON dungeon_party_members(party_id);
CREATE INDEX idx_coop_members_user ON coop_members(user_id);
CREATE INDEX idx_coop_members_coop ON coop_members(coop_id);
CREATE INDEX idx_minion_upgrades_minion ON minion_upgrades(minion_id);
