-- Migration: Expanded Achievement System
-- Adds many more achievements across all categories

-- Additional Wealth Achievements
INSERT OR IGNORE INTO game_achievements (achievement_id, name, description, category, icon, requirement_type, requirement_value) VALUES
('wealth_500k', 'Half Millionaire', 'Accumulate 500,000 coins', 'Wealth', '💰', 'coins', 500000),
('wealth_5m', 'Five Million Club', 'Accumulate 5,000,000 coins', 'Wealth', '💎', 'coins', 5000000),
('wealth_50m', 'Coin Hoarder', 'Accumulate 50,000,000 coins', 'Wealth', '👑', 'coins', 50000000),
('wealth_500m', 'Ultra Rich', 'Accumulate 500,000,000 coins', 'Wealth', '⭐', 'coins', 500000000),
('wealth_1b', 'Billionaire', 'Accumulate 1,000,000,000 coins', 'Wealth', '💠', 'coins', 1000000000),

-- Additional Combat Achievements
('kills_50', 'Combat Initiate', 'Defeat 50 enemies', 'Combat', '⚔️', 'kills', 50),
('kills_500', 'Battle Master', 'Defeat 500 enemies', 'Combat', '⚔️', 'kills', 500),
('kills_5000', 'Slaughter Machine', 'Defeat 5,000 enemies', 'Combat', '👹', 'kills', 5000),
('kills_50000', 'Legendary Warrior', 'Defeat 50,000 enemies', 'Combat', '⚔️', 'kills', 50000),
('kills_100000', 'Death Incarnate', 'Defeat 100,000 enemies', 'Combat', '💀', 'kills', 100000),

-- Boss Achievements
('boss_kills_1', 'Boss Slayer', 'Defeat your first boss', 'Combat', '👹', 'boss_kills', 1),
('boss_kills_5', 'Boss Hunter', 'Defeat 5 bosses', 'Combat', '👹', 'boss_kills', 5),
('boss_kills_25', 'Boss Destroyer', 'Defeat 25 bosses', 'Combat', '👹', 'boss_kills', 25),
('boss_kills_50', 'Boss Terminator', 'Defeat 50 bosses', 'Combat', '💀', 'boss_kills', 50),
('boss_kills_100', 'Boss Annihilator', 'Defeat 100 bosses', 'Combat', '⚔️', 'boss_kills', 100),

-- Carpentry Skill Achievements
('carpentry_5', 'Carpentry Apprentice', 'Reach Carpentry Level 5', 'Skills', '🪚', 'skill_level', 5),
('carpentry_10', 'Carpentry Adept', 'Reach Carpentry Level 10', 'Skills', '🪚', 'skill_level', 10),
('carpentry_20', 'Carpentry Expert', 'Reach Carpentry Level 20', 'Skills', '🪚', 'skill_level', 20),
('carpentry_30', 'Carpentry Master', 'Reach Carpentry Level 30', 'Skills', '🪚', 'skill_level', 30),
('carpentry_40', 'Carpentry Grandmaster', 'Reach Carpentry Level 40', 'Skills', '🪚', 'skill_level', 40),
('carpentry_50', 'Carpentry Legend', 'Reach Carpentry Level 50', 'Skills', '🪚', 'skill_level', 50),

-- Runecrafting Skill Achievements
('runecrafting_5', 'Runecrafting Apprentice', 'Reach Runecrafting Level 5', 'Skills', '🔮', 'skill_level', 5),
('runecrafting_10', 'Runecrafting Adept', 'Reach Runecrafting Level 10', 'Skills', '🔮', 'skill_level', 10),
('runecrafting_20', 'Runecrafting Expert', 'Reach Runecrafting Level 20', 'Skills', '🔮', 'skill_level', 20),
('runecrafting_30', 'Runecrafting Master', 'Reach Runecrafting Level 30', 'Skills', '🔮', 'skill_level', 30),
('runecrafting_40', 'Runecrafting Grandmaster', 'Reach Runecrafting Level 40', 'Skills', '🔮', 'skill_level', 40),
('runecrafting_50', 'Runecrafting Legend', 'Reach Runecrafting Level 50', 'Skills', '🔮', 'skill_level', 50),

-- Social Skill Achievements
('social_5', 'Social Butterfly', 'Reach Social Level 5', 'Skills', '👥', 'skill_level', 5),
('social_10', 'Popular', 'Reach Social Level 10', 'Skills', '👥', 'skill_level', 10),
('social_20', 'Well Connected', 'Reach Social Level 20', 'Skills', '👥', 'skill_level', 20),
('social_30', 'Social Master', 'Reach Social Level 30', 'Skills', '👥', 'skill_level', 30),
('social_40', 'Social Grandmaster', 'Reach Social Level 40', 'Skills', '👥', 'skill_level', 40),
('social_50', 'Social Legend', 'Reach Social Level 50', 'Skills', '👥', 'skill_level', 50),

-- Multi-Skill Achievements
('all_skills_10', 'Jack of All Trades', 'Reach level 10 in all skills', 'Skills', '📚', 'skill_average', 10),
('all_skills_25', 'Master of All', 'Reach level 25 in all skills', 'Skills', '📖', 'skill_average', 25),
('all_skills_50', 'Legendary Crafter', 'Reach level 50 in all skills', 'Skills', '⭐', 'skill_average', 50),
('skill_level_30', 'Highly Trained', 'Reach level 30 in any skill', 'Skills', '📗', 'skill_level', 30),
('skill_level_40', 'Expert', 'Reach level 40 in any skill', 'Skills', '📕', 'skill_level', 40),

-- More Dungeon Achievements
('dungeon_5', 'Dungeon Beginner', 'Complete 5 dungeons', 'Dungeons', '🏰', 'dungeons', 5),
('dungeon_25', 'Dungeon Explorer', 'Complete 25 dungeons', 'Dungeons', '🏰', 'dungeons', 25),
('dungeon_250', 'Dungeon Specialist', 'Complete 250 dungeons', 'Dungeons', '🏰', 'dungeons', 250),
('dungeon_1000', 'Dungeon Legend', 'Complete 1,000 dungeons', 'Dungeons', '🏰', 'dungeons', 1000),
('dungeon_s_rank', 'Perfect Run', 'Get S rank in a dungeon', 'Dungeons', '⭐', 'action', 1),
('dungeon_no_death', 'Flawless Victory', 'Complete a dungeon without dying', 'Dungeons', '💚', 'action', 1),

-- More Slayer Achievements
('slayer_5', 'Slayer Beginner', 'Complete 5 slayer quests', 'Slayer', '🗡️', 'slayers', 5),
('slayer_25', 'Slayer Veteran', 'Complete 25 slayer quests', 'Slayer', '🗡️', 'slayers', 25),
('slayer_250', 'Slayer Champion', 'Complete 250 slayer quests', 'Slayer', '🗡️', 'slayers', 250),
('slayer_1000', 'Slayer Legend', 'Complete 1,000 slayer quests', 'Slayer', '🗡️', 'slayers', 1000),
('slayer_tier_5', 'Slayer Boss', 'Complete a Tier 5 slayer', 'Slayer', '💀', 'slayer_tier', 5),

-- More Minion Achievements
('minion_tier_11', 'Minion Maxed', 'Upgrade a minion to tier 11', 'Minions', '🤖', 'minion_tier', 11),
('minions_15', 'Minion Manager', 'Place 15 unique minions', 'Minions', '🤖', 'minions', 15),
('minions_20', 'Minion Lord', 'Place 20 unique minions', 'Minions', '🤖', 'minions', 20),
('minion_slots_20', 'Slot Master', 'Unlock 20 minion slots', 'Minions', '🤖', 'minion_slots', 20),

-- Trading/Economy Achievements
('auction_5', 'Auction Starter', 'Create 5 auctions', 'Trading', '🏛️', 'auctions', 5),
('auction_50', 'Auction Trader', 'Create 50 auctions', 'Trading', '🏛️', 'auctions', 50),
('auction_500', 'Auction Merchant', 'Create 500 auctions', 'Trading', '🏛️', 'auctions', 500),
('auction_win_10', 'Winning Bidder', 'Win 10 auctions', 'Trading', '💰', 'auction_wins', 10),
('auction_win_50', 'Auction King', 'Win 50 auctions', 'Trading', '👑', 'auction_wins', 50),
('bazaar_orders_100', 'Bazaar Trader', 'Complete 100 bazaar orders', 'Trading', '💹', 'bazaar_orders', 100),
('bazaar_orders_1000', 'Bazaar Tycoon', 'Complete 1,000 bazaar orders', 'Trading', '💹', 'bazaar_orders', 1000),
('bazaar_profit_50k', 'Profit Seeker', 'Make 50K profit from bazaar', 'Trading', '💹', 'profit', 50000),
('bazaar_profit_500k', 'Profit Hunter', 'Make 500K profit from bazaar', 'Trading', '💹', 'profit', 500000),
('bazaar_profit_5m', 'Profit Master', 'Make 5M profit from bazaar', 'Trading', '💹', 'profit', 5000000),
('bazaar_profit_50m', 'Profit Legend', 'Make 50M profit from bazaar', 'Trading', '💹', 'profit', 50000000),

-- More Collection Achievements
('collections_5', 'Collection Starter', 'Reach tier 5 in 5 collections', 'Collections', '📚', 'collections', 5),
('collections_25', 'Collection Enthusiast', 'Reach tier 5 in 25 collections', 'Collections', '📚', 'collections', 25),
('collections_50', 'Collection Master', 'Reach tier 5 in 50 collections', 'Collections', '📚', 'collections', 50),
('collection_max_10', 'Maxed Collector', 'Max out 10 collections', 'Collections', '⭐', 'collections_maxed', 10),

-- Crafting Achievements
('craft_10', 'Novice Crafter', 'Craft 10 items', 'Crafting', '🔨', 'crafts', 10),
('craft_100', 'Experienced Crafter', 'Craft 100 items', 'Crafting', '🔨', 'crafts', 100),
('craft_1000', 'Master Crafter', 'Craft 1,000 items', 'Crafting', '🔨', 'crafts', 1000),
('craft_legendary', 'Legendary Smith', 'Craft a legendary item', 'Crafting', '✨', 'action', 1),

-- Enchanting Achievements  
('enchant_10', 'Enchant Beginner', 'Enchant 10 items', 'Enchanting', '✨', 'enchants', 10),
('enchant_100', 'Enchant Master', 'Enchant 100 items', 'Enchanting', '✨', 'enchants', 100),
('enchant_max', 'Ultimate Enchanter', 'Apply a max level enchantment', 'Enchanting', '⭐', 'action', 1),

-- Reforging Achievements
('reforge_10', 'Reforge Novice', 'Reforge 10 items', 'Reforging', '🔧', 'reforges', 10),
('reforge_100', 'Reforge Expert', 'Reforge 100 items', 'Reforging', '🔧', 'reforges', 100),
('reforge_legendary', 'Perfect Reforge', 'Apply a legendary reforge', 'Reforging', '✨', 'action', 1),

-- More HOTM Achievements
('hotm_tier_2', 'Mountain Beginner', 'Reach HOTM Tier 2', 'Mining', '⛰️', 'hotm_tier', 2),
('hotm_tier_4', 'Mountain Adventurer', 'Reach HOTM Tier 4', 'Mining', '⛰️', 'hotm_tier', 4),
('hotm_tier_6', 'Mountain Expert', 'Reach HOTM Tier 6', 'Mining', '⛰️', 'hotm_tier', 6),
('hotm_tier_8', 'Mountain Champion', 'Reach HOTM Tier 8', 'Mining', '⛰️', 'hotm_tier', 8),
('hotm_tier_9', 'Mountain Hero', 'Reach HOTM Tier 9', 'Mining', '⛰️', 'hotm_tier', 9),
('mithril_powder_10k', 'Powder Collector', 'Collect 10,000 Mithril Powder', 'Mining', '💎', 'mithril_powder', 10000),
('mithril_powder_100k', 'Powder Master', 'Collect 100,000 Mithril Powder', 'Mining', '💎', 'mithril_powder', 100000),

-- More Pet Achievements
('pet_common', 'Pet Collector', 'Obtain a common pet', 'Pets', '🐾', 'pet_rarity', 1),
('pet_uncommon', 'Uncommon Pet Owner', 'Obtain an uncommon pet', 'Pets', '🐾', 'pet_rarity', 2),
('pet_level_25', 'Pet Enthusiast', 'Level a pet to 25', 'Pets', '🐕', 'pet_level', 25),
('pet_level_75', 'Pet Expert', 'Level a pet to 75', 'Pets', '🐕', 'pet_level', 75),
('pets_5', 'Pet Collector', 'Own 5 different pets', 'Pets', '🐾', 'pets_owned', 5),
('pets_10', 'Pet Hoarder', 'Own 10 different pets', 'Pets', '🐾', 'pets_owned', 10),
('pets_25', 'Pet Master', 'Own 25 different pets', 'Pets', '🐾', 'pets_owned', 25),

-- More Fairy Soul Achievements
('fairy_soul_5', 'Soul Finder', 'Collect 5 fairy souls', 'Exploration', '✨', 'fairy_souls', 5),
('fairy_soul_25', 'Soul Gatherer', 'Collect 25 fairy souls', 'Exploration', '✨', 'fairy_souls', 25),
('fairy_soul_75', 'Soul Expert', 'Collect 75 fairy souls', 'Exploration', '✨', 'fairy_souls', 75),
('fairy_soul_150', 'Soul Champion', 'Collect 150 fairy souls', 'Exploration', '✨', 'fairy_souls', 150),

-- Location Achievements
('hub_explorer', 'Hub Explorer', 'Unlock all Hub locations', 'Exploration', '🗺️', 'action', 1),
('island_hopper', 'Island Hopper', 'Visit 5 different islands', 'Exploration', '🏝️', 'islands_visited', 5),
('world_traveler', 'World Traveler', 'Visit all available islands', 'Exploration', '🌍', 'action', 1),

-- Special/Milestone Achievements
('bank_100k', 'Savings Account', 'Store 100K coins in bank', 'Special', '🏦', 'bank_balance', 100000),
('bank_10m', 'Vault Master', 'Store 10M coins in bank', 'Special', '🏦', 'bank_balance', 10000000),
('bank_100m', 'Bank Tycoon', 'Store 100M coins in bank', 'Special', '🏦', 'bank_balance', 100000000),
('coop_member', 'Co-op Member', 'Join a co-op', 'Special', '🤝', 'action', 1),
('party_join_10', 'Party Animal', 'Join 10 parties', 'Special', '👥', 'parties_joined', 10),
('party_host_5', 'Party Starter', 'Host 5 parties', 'Special', '👥', 'parties', 5),
('party_host_25', 'Party Master', 'Host 25 parties', 'Special', '👥', 'parties', 25),
('boss_kill_5', 'Boss Challenger', 'Defeat 5 world bosses', 'Special', '👹', 'boss_kills', 5),
('boss_kill_25', 'Boss Slayer', 'Defeat 25 world bosses', 'Special', '👹', 'boss_kills', 25),
('boss_kill_50', 'Boss Destroyer', 'Defeat 50 world bosses', 'Special', '👹', 'boss_kills', 50),
('museum_donate_5', 'Museum Contributor', 'Donate 5 items to museum', 'Special', '🏛️', 'museum_donations', 5),
('museum_donate_50', 'Museum Patron', 'Donate 50 items to museum', 'Special', '🏛️', 'museum_donations', 50),
('museum_donate_250', 'Museum Curator', 'Donate 250 items to museum', 'Special', '🏛️', 'museum_donations', 250),
('quest_10', 'Quest Taker', 'Complete 10 quests', 'Special', '📜', 'quests_completed', 10),
('quest_50', 'Quest Master', 'Complete 50 quests', 'Special', '📜', 'quests_completed', 50),
('quest_100', 'Quest Legend', 'Complete 100 quests', 'Special', '📜', 'quests_completed', 100),
('daily_login_7', 'Week Streak', 'Login for 7 days in a row', 'Special', '📅', 'login_streak', 7),
('daily_login_30', 'Month Streak', 'Login for 30 days in a row', 'Special', '📅', 'login_streak', 30),
('daily_login_100', 'Dedicated Player', 'Login for 100 days in a row', 'Special', '📅', 'login_streak', 100),

-- More Cursed Achievements
('death_10', 'Learning Experience', 'Die 10 times', 'Cursed', '💀', 'deaths', 10),
('death_50', 'Clumsy', 'Die 50 times', 'Cursed', '💀', 'deaths', 50),
('death_500', 'Death Magnet', 'Die 500 times', 'Cursed', '💀', 'deaths', 500),
('death_5000', 'Immortal... Not', 'Die 5,000 times', 'Cursed', '💀', 'deaths', 5000),
('lose_auction', 'Outbid', 'Lose an auction you were winning', 'Cursed', '😢', 'action', 1),
('overpay', 'Bad Deal', 'Pay 2x market price for an item', 'Cursed', '🤦', 'action', 1),
('broke_1m', 'From Riches to Rags', 'Go from 1M+ coins to 0', 'Cursed', '😭', 'action', 1),
('fall_damage', 'Gravity Hurts', 'Die from fall damage', 'Cursed', '🪨', 'action', 1),
('void_death', 'Into the Void', 'Die by falling into the void', 'Cursed', '🕳️', 'action', 1),

-- Speed Achievements
('speed_run_dungeon', 'Speed Runner', 'Complete a dungeon in under 5 minutes', 'Speed', '⚡', 'action', 1),
('speed_craft_100', 'Fast Crafter', 'Craft 100 items in one session', 'Speed', '⚡', 'action', 1),
('speed_collection', 'Quick Collector', 'Gain 1000 collection in one item', 'Speed', '⚡', 'action', 1),

-- Prestige Achievements
('prestige_1', 'Prestige I', 'Reach Prestige Level 1', 'Prestige', '⭐', 'prestige', 1),
('prestige_5', 'Prestige V', 'Reach Prestige Level 5', 'Prestige', '⭐⭐', 'prestige', 5),
('prestige_10', 'Prestige X', 'Reach Prestige Level 10', 'Prestige', '⭐⭐⭐', 'prestige', 10);
