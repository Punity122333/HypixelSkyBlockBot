-- Migration: Add comprehensive achievements system
-- This creates the game_achievements table with extensive achievements

CREATE TABLE IF NOT EXISTS game_achievements (
    achievement_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    category TEXT NOT NULL,
    icon TEXT NOT NULL,
    requirement_type TEXT,
    requirement_value INTEGER DEFAULT 0
);

-- First Time Achievements
INSERT OR IGNORE INTO game_achievements (achievement_id, name, description, category, icon, requirement_type, requirement_value) VALUES
('first_mine', 'First Steps', 'Mine your first block', 'First Time', '⛏️', 'action', 1),
('first_farm', 'Farmer', 'Harvest your first crop', 'First Time', '🌾', 'action', 1),
('first_fish', 'Angler', 'Catch your first fish', 'First Time', '🎣', 'action', 1),
('first_forage', 'Lumberjack', 'Chop your first tree', 'First Time', '🪓', 'action', 1),
('first_craft', 'Craftsman', 'Craft your first item', 'First Time', '🔨', 'action', 1),
('first_kill', 'First Blood', 'Defeat your first enemy', 'First Time', '⚔️', 'kills', 1),
('first_auction', 'Auctioneer', 'Create your first auction', 'First Time', '🏛️', 'action', 1),
('first_bazaar', 'Trader', 'Complete your first bazaar transaction', 'First Time', '💰', 'action', 1),
('first_dungeon', 'Dungeon Explorer', 'Complete your first dungeon', 'First Time', '🏰', 'dungeons', 1),
('first_slayer', 'Slayer Novice', 'Complete your first slayer quest', 'First Time', '🗡️', 'slayers', 1),
('first_minion', 'Minion Master', 'Place your first minion', 'First Time', '🤖', 'minions', 1),
('first_enchant', 'Enchanter', 'Enchant your first item', 'First Time', '✨', 'action', 1),
('first_reforge', 'Blacksmith', 'Reforge your first item', 'First Time', '🔧', 'action', 1),
('first_pet', 'Pet Owner', 'Obtain your first pet', 'First Time', '🐕', 'action', 1),

-- Wealth Achievements
('wealth_1k', 'Getting Started', 'Accumulate 1,000 coins', 'Wealth', '💰', 'coins', 1000),
('wealth_10k', 'Coin Collector', 'Accumulate 10,000 coins', 'Wealth', '💵', 'coins', 10000),
('wealth_100k', 'Wealthy', 'Accumulate 100,000 coins', 'Wealth', '💎', 'coins', 100000),
('wealth_1m', 'Millionaire', 'Accumulate 1,000,000 coins', 'Wealth', '💰', 'coins', 1000000),
('wealth_10m', 'Multi-Millionaire', 'Accumulate 10,000,000 coins', 'Wealth', '🏆', 'coins', 10000000),
('wealth_100m', 'Tycoon', 'Accumulate 100,000,000 coins', 'Wealth', '👑', 'coins', 100000000),

-- Combat Achievements
('kills_10', 'Novice Warrior', 'Defeat 10 enemies', 'Combat', '⚔️', 'kills', 10),
('kills_100', 'Experienced Fighter', 'Defeat 100 enemies', 'Combat', '🗡️', 'kills', 100),
('kills_1000', 'Veteran Warrior', 'Defeat 1,000 enemies', 'Combat', '⚔️', 'kills', 1000),
('kills_10000', 'Combat Master', 'Defeat 10,000 enemies', 'Combat', '👹', 'kills', 10000),

-- Mining Skill Achievements
('mining_5', 'Mining Apprentice', 'Reach Mining Level 5', 'Skills', '⛏️', 'skill_level', 5),
('mining_10', 'Mining Adept', 'Reach Mining Level 10', 'Skills', '⛏️', 'skill_level', 10),
('mining_20', 'Mining Expert', 'Reach Mining Level 20', 'Skills', '⛏️', 'skill_level', 20),
('mining_30', 'Mining Master', 'Reach Mining Level 30', 'Skills', '⛏️', 'skill_level', 30),
('mining_40', 'Mining Grandmaster', 'Reach Mining Level 40', 'Skills', '⛏️', 'skill_level', 40),
('mining_50', 'Mining Legend', 'Reach Mining Level 50', 'Skills', '⛏️', 'skill_level', 50),

-- Farming Skill Achievements
('farming_5', 'Farming Apprentice', 'Reach Farming Level 5', 'Skills', '🌾', 'skill_level', 5),
('farming_10', 'Farming Adept', 'Reach Farming Level 10', 'Skills', '🌾', 'skill_level', 10),
('farming_20', 'Farming Expert', 'Reach Farming Level 20', 'Skills', '🌾', 'skill_level', 20),
('farming_30', 'Farming Master', 'Reach Farming Level 30', 'Skills', '🌾', 'skill_level', 30),
('farming_40', 'Farming Grandmaster', 'Reach Farming Level 40', 'Skills', '🌾', 'skill_level', 40),
('farming_50', 'Farming Legend', 'Reach Farming Level 50', 'Skills', '🌾', 'skill_level', 50),

-- Combat Skill Achievements
('combat_5', 'Combat Apprentice', 'Reach Combat Level 5', 'Skills', '⚔️', 'skill_level', 5),
('combat_10', 'Combat Adept', 'Reach Combat Level 10', 'Skills', '⚔️', 'skill_level', 10),
('combat_20', 'Combat Expert', 'Reach Combat Level 20', 'Skills', '⚔️', 'skill_level', 20),
('combat_30', 'Combat Master', 'Reach Combat Level 30', 'Skills', '⚔️', 'skill_level', 30),
('combat_40', 'Combat Grandmaster', 'Reach Combat Level 40', 'Skills', '⚔️', 'skill_level', 40),
('combat_50', 'Combat Legend', 'Reach Combat Level 50', 'Skills', '⚔️', 'skill_level', 50),

-- Foraging Skill Achievements
('foraging_5', 'Foraging Apprentice', 'Reach Foraging Level 5', 'Skills', '🪓', 'skill_level', 5),
('foraging_10', 'Foraging Adept', 'Reach Foraging Level 10', 'Skills', '🪓', 'skill_level', 10),
('foraging_20', 'Foraging Expert', 'Reach Foraging Level 20', 'Skills', '🪓', 'skill_level', 20),
('foraging_30', 'Foraging Master', 'Reach Foraging Level 30', 'Skills', '🪓', 'skill_level', 30),
('foraging_40', 'Foraging Grandmaster', 'Reach Foraging Level 40', 'Skills', '🪓', 'skill_level', 40),
('foraging_50', 'Foraging Legend', 'Reach Foraging Level 50', 'Skills', '🪓', 'skill_level', 50),

-- Fishing Skill Achievements
('fishing_5', 'Fishing Apprentice', 'Reach Fishing Level 5', 'Skills', '🎣', 'skill_level', 5),
('fishing_10', 'Fishing Adept', 'Reach Fishing Level 10', 'Skills', '🎣', 'skill_level', 10),
('fishing_20', 'Fishing Expert', 'Reach Fishing Level 20', 'Skills', '🎣', 'skill_level', 20),
('fishing_30', 'Fishing Master', 'Reach Fishing Level 30', 'Skills', '🎣', 'skill_level', 30),
('fishing_40', 'Fishing Grandmaster', 'Reach Fishing Level 40', 'Skills', '🎣', 'skill_level', 40),
('fishing_50', 'Fishing Legend', 'Reach Fishing Level 50', 'Skills', '🎣', 'skill_level', 50),

-- Enchanting Skill Achievements
('enchanting_5', 'Enchanting Apprentice', 'Reach Enchanting Level 5', 'Skills', '✨', 'skill_level', 5),
('enchanting_10', 'Enchanting Adept', 'Reach Enchanting Level 10', 'Skills', '✨', 'skill_level', 10),
('enchanting_20', 'Enchanting Expert', 'Reach Enchanting Level 20', 'Skills', '✨', 'skill_level', 20),
('enchanting_30', 'Enchanting Master', 'Reach Enchanting Level 30', 'Skills', '✨', 'skill_level', 30),
('enchanting_40', 'Enchanting Grandmaster', 'Reach Enchanting Level 40', 'Skills', '✨', 'skill_level', 40),
('enchanting_50', 'Enchanting Legend', 'Reach Enchanting Level 50', 'Skills', '✨', 'skill_level', 50),

-- Alchemy Skill Achievements
('alchemy_5', 'Alchemy Apprentice', 'Reach Alchemy Level 5', 'Skills', '⚗️', 'skill_level', 5),
('alchemy_10', 'Alchemy Adept', 'Reach Alchemy Level 10', 'Skills', '⚗️', 'skill_level', 10),
('alchemy_20', 'Alchemy Expert', 'Reach Alchemy Level 20', 'Skills', '⚗️', 'skill_level', 20),
('alchemy_30', 'Alchemy Master', 'Reach Alchemy Level 30', 'Skills', '⚗️', 'skill_level', 30),
('alchemy_40', 'Alchemy Grandmaster', 'Reach Alchemy Level 40', 'Skills', '⚗️', 'skill_level', 40),
('alchemy_50', 'Alchemy Legend', 'Reach Alchemy Level 50', 'Skills', '⚗️', 'skill_level', 50),

-- Taming Skill Achievements
('taming_5', 'Taming Apprentice', 'Reach Taming Level 5', 'Skills', '🐕', 'skill_level', 5),
('taming_10', 'Taming Adept', 'Reach Taming Level 10', 'Skills', '🐕', 'skill_level', 10),
('taming_20', 'Taming Expert', 'Reach Taming Level 20', 'Skills', '🐕', 'skill_level', 20),
('taming_30', 'Taming Master', 'Reach Taming Level 30', 'Skills', '🐕', 'skill_level', 30),
('taming_40', 'Taming Grandmaster', 'Reach Taming Level 40', 'Skills', '🐕', 'skill_level', 40),
('taming_50', 'Taming Legend', 'Reach Taming Level 50', 'Skills', '🐕', 'skill_level', 50),

-- General Skill Achievements
('skill_level_10', 'Skilled', 'Reach level 10 in any skill', 'Skills', '📚', 'skill_level', 10),
('skill_level_25', 'Highly Skilled', 'Reach level 25 in any skill', 'Skills', '📖', 'skill_level', 25),
('skill_level_50', 'Master of Skills', 'Reach level 50 in any skill', 'Skills', '⭐', 'skill_level', 50),

-- Dungeon Achievements
('dungeon_10', 'Dungeon Runner', 'Complete 10 dungeons', 'Dungeons', '🏰', 'dungeons', 10),
('dungeon_50', 'Dungeon Veteran', 'Complete 50 dungeons', 'Dungeons', '🏰', 'dungeons', 50),
('dungeon_100', 'Dungeon Expert', 'Complete 100 dungeons', 'Dungeons', '🏰', 'dungeons', 100),
('dungeon_500', 'Dungeon Master', 'Complete 500 dungeons', 'Dungeons', '🏰', 'dungeons', 500),

-- Slayer Achievements
('slayer_10', 'Slayer Apprentice', 'Complete 10 slayer quests', 'Slayer', '🗡️', 'slayers', 10),
('slayer_50', 'Slayer Adept', 'Complete 50 slayer quests', 'Slayer', '🗡️', 'slayers', 50),
('slayer_100', 'Slayer Expert', 'Complete 100 slayer quests', 'Slayer', '🗡️', 'slayers', 100),
('slayer_500', 'Slayer Master', 'Complete 500 slayer quests', 'Slayer', '🗡️', 'slayers', 500),

-- Minion Achievements
('minions_5', 'Minion Collector', 'Place 5 unique minions', 'Minions', '🤖', 'minions', 5),
('minions_10', 'Minion Army', 'Place 10 unique minions', 'Minions', '🤖', 'minions', 10),
('minions_25', 'Minion Commander', 'Place 25 unique minions', 'Minions', '🤖', 'minions', 25),
('minion_slots_max', 'Minion Overlord', 'Unlock all minion slots', 'Minions', '🤖', 'minion_slots', 25),

-- Trading Achievements
('auction_10', 'Auction Regular', 'Create 10 auctions', 'Trading', '🏛️', 'auctions', 10),
('auction_100', 'Auction Expert', 'Create 100 auctions', 'Trading', '🏛️', 'auctions', 100),
('auction_1000', 'Auction Master', 'Create 1,000 auctions', 'Trading', '🏛️', 'auctions', 1000),
('bazaar_profit_100k', 'Bazaar Flipper', 'Make 100K profit from bazaar', 'Trading', '💹', 'profit', 100000),
('bazaar_profit_1m', 'Flip Master', 'Make 1M profit from bazaar', 'Trading', '💹', 'profit', 1000000),
('bazaar_profit_10m', 'Flip God', 'Make 10M profit from bazaar', 'Trading', '💹', 'profit', 10000000),

-- Collection Achievements
('collection_tier_5', 'Collector', 'Reach tier 5 in any collection', 'Collections', '📚', 'collection_tier', 5),
('collection_tier_10', 'Master Collector', 'Max out any collection', 'Collections', '📚', 'collection_tier', 10),
('collections_10', 'Collection Hunter', 'Reach tier 5 in 10 collections', 'Collections', '📚', 'collections', 10),

-- HOTM Achievements
('hotm_tier_3', 'Mountain Climber', 'Reach HOTM Tier 3', 'Mining', '⛰️', 'hotm_tier', 3),
('hotm_tier_5', 'Mountain Explorer', 'Reach HOTM Tier 5', 'Mining', '⛰️', 'hotm_tier', 5),
('hotm_tier_7', 'Mountain Master', 'Reach HOTM Tier 7', 'Mining', '⛰️', 'hotm_tier', 7),
('hotm_tier_10', 'Peak of Mountain', 'Reach HOTM Tier 10', 'Mining', '⛰️', 'hotm_tier', 10),

-- Pet Achievements
('pet_rare', 'Rare Pet Owner', 'Obtain a rare pet', 'Pets', '🐾', 'pet_rarity', 3),
('pet_epic', 'Epic Pet Owner', 'Obtain an epic pet', 'Pets', '🐾', 'pet_rarity', 4),
('pet_legendary', 'Legendary Pet Owner', 'Obtain a legendary pet', 'Pets', '🐉', 'pet_rarity', 5),
('pet_level_50', 'Pet Trainer', 'Level a pet to 50', 'Pets', '🐕', 'pet_level', 50),
('pet_level_100', 'Pet Master', 'Level a pet to 100', 'Pets', '🐕', 'pet_level', 100),

-- Fairy Soul Achievements
('fairy_soul_10', 'Soul Seeker', 'Collect 10 fairy souls', 'Exploration', '✨', 'fairy_souls', 10),
('fairy_soul_50', 'Soul Collector', 'Collect 50 fairy souls', 'Exploration', '✨', 'fairy_souls', 50),
('fairy_soul_100', 'Soul Hunter', 'Collect 100 fairy souls', 'Exploration', '✨', 'fairy_souls', 100),
('fairy_soul_all', 'Soul Master', 'Collect all fairy souls', 'Exploration', '✨', 'fairy_souls', 200),

-- Special Achievements
('bank_1m', 'Banker', 'Store 1M coins in bank', 'Special', '🏦', 'bank_balance', 1000000),
('coop_create', 'Co-op Founder', 'Create a co-op', 'Special', '🤝', 'action', 1),
('party_host_10', 'Party Host', 'Host 10 dungeon parties', 'Special', '👥', 'parties', 10),
('boss_kill_10', 'Boss Hunter', 'Defeat 10 world bosses', 'Special', '👹', 'boss_kills', 10),
('museum_donate_10', 'Museum Donor', 'Donate 10 items to museum', 'Special', '🏛️', 'museum_donations', 10),
('museum_donate_100', 'Museum Benefactor', 'Donate 100 items to museum', 'Special', '🏛️', 'museum_donations', 100),

-- Cursed Achievements
('death_first', 'Mortality', 'Die for the first time', 'Cursed', '💀', 'deaths', 1),
('death_100', 'Frequent Flyer', 'Die 100 times', 'Cursed', '💀', 'deaths', 100),
('death_1000', 'Death Enthusiast', 'Die 1,000 times', 'Cursed', '💀', 'deaths', 1000),
('broke', 'Broke', 'Have exactly 0 coins', 'Cursed', '🥺', 'coins', 0),
('scammed', 'Got Scammed', 'Lose 100k+ in a bad trade', 'Cursed', '😭', 'action', 1);
