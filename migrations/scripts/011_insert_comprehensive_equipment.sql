-- Comprehensive Equipment Insert Script
-- This script inserts 50+ armor pieces and tools with stats, recipes, and lore

-- ============================================
-- LEATHER ARMOR SET
-- ============================================
INSERT OR REPLACE INTO game_items (item_id, name, rarity, item_type, stats, lore, special_ability, craft_recipe, npc_sell_price, collection_req, default_bazaar_price)
VALUES 
('leather_helmet', 'Leather Helmet', 'COMMON', 'HELMET', '{"defense": 5, "health": 10}', 'Basic leather protection', '', '{"leather": 5}', 5, '{}', 10),
('leather_chestplate', 'Leather Chestplate', 'COMMON', 'CHESTPLATE', '{"defense": 10, "health": 15}', 'Basic leather protection', '', '{"leather": 8}', 8, '{}', 15),
('leather_leggings', 'Leather Leggings', 'COMMON', 'LEGGINGS', '{"defense": 8, "health": 12}', 'Basic leather protection', '', '{"leather": 7}', 7, '{}', 12),
('leather_boots', 'Leather Boots', 'COMMON', 'BOOTS', '{"defense": 5, "health": 8}', 'Basic leather protection', '', '{"leather": 4}', 4, '{}', 8);

INSERT OR REPLACE INTO armor_stats (item_id, defense, health, strength, crit_chance, crit_damage, intelligence, speed, magic_find, pet_luck, true_defense)
VALUES 
('leather_helmet', 5, 10, 0, 0, 0, 0, 0, 0, 0, 0),
('leather_chestplate', 10, 15, 0, 0, 0, 0, 0, 0, 0, 0),
('leather_leggings', 8, 12, 0, 0, 0, 0, 0, 0, 0, 0),
('leather_boots', 5, 8, 0, 0, 0, 0, 0, 0, 0, 0);

-- ============================================
-- CHAINMAIL ARMOR SET
-- ============================================
INSERT OR REPLACE INTO game_items (item_id, name, rarity, item_type, stats, lore, special_ability, craft_recipe, npc_sell_price, collection_req, default_bazaar_price)
VALUES 
('chainmail_helmet', 'Chainmail Helmet', 'COMMON', 'HELMET', '{"defense": 15, "health": 20}', 'Light metal protection', '', '{"iron_ingot": 5, "string": 3}', 20, '{}', 40),
('chainmail_chestplate', 'Chainmail Chestplate', 'COMMON', 'CHESTPLATE', '{"defense": 25, "health": 30}', 'Light metal protection', '', '{"iron_ingot": 8, "string": 5}', 35, '{}', 70),
('chainmail_leggings', 'Chainmail Leggings', 'COMMON', 'LEGGINGS', '{"defense": 20, "health": 25}', 'Light metal protection', '', '{"iron_ingot": 7, "string": 4}', 28, '{}', 56),
('chainmail_boots', 'Chainmail Boots', 'COMMON', 'BOOTS', '{"defense": 12, "health": 15}', 'Light metal protection', '', '{"iron_ingot": 4, "string": 2}', 15, '{}', 30);

INSERT OR REPLACE INTO armor_stats (item_id, defense, health, strength, crit_chance, crit_damage, intelligence, speed, magic_find, pet_luck, true_defense)
VALUES 
('chainmail_helmet', 15, 20, 0, 0, 0, 0, 0, 0, 0, 0),
('chainmail_chestplate', 25, 30, 0, 0, 0, 0, 0, 0, 0, 0),
('chainmail_leggings', 20, 25, 0, 0, 0, 0, 0, 0, 0, 0),
('chainmail_boots', 12, 15, 0, 0, 0, 0, 0, 0, 0, 0);

-- ============================================
-- IRON ARMOR SET
-- ============================================
INSERT OR REPLACE INTO game_items (item_id, name, rarity, item_type, stats, lore, special_ability, craft_recipe, npc_sell_price, collection_req, default_bazaar_price)
VALUES 
('iron_helmet', 'Iron Helmet', 'COMMON', 'HELMET', '{"defense": 25, "health": 30}', 'Sturdy iron protection', '', '{"iron_ingot": 5}', 50, '{}', 100),
('iron_chestplate', 'Iron Chestplate', 'COMMON', 'CHESTPLATE', '{"defense": 40, "health": 50}', 'Sturdy iron protection', '', '{"iron_ingot": 8}', 80, '{}', 160),
('iron_leggings', 'Iron Leggings', 'COMMON', 'LEGGINGS', '{"defense": 35, "health": 40}', 'Sturdy iron protection', '', '{"iron_ingot": 7}', 70, '{}', 140),
('iron_boots', 'Iron Boots', 'COMMON', 'BOOTS', '{"defense": 20, "health": 25}', 'Sturdy iron protection', '', '{"iron_ingot": 4}', 40, '{}', 80);

INSERT OR REPLACE INTO armor_stats (item_id, defense, health, strength, crit_chance, crit_damage, intelligence, speed, magic_find, pet_luck, true_defense)
VALUES 
('iron_helmet', 25, 30, 0, 0, 0, 0, 0, 0, 0, 0),
('iron_chestplate', 40, 50, 0, 0, 0, 0, 0, 0, 0, 0),
('iron_leggings', 35, 40, 0, 0, 0, 0, 0, 0, 0, 0),
('iron_boots', 20, 25, 0, 0, 0, 0, 0, 0, 0, 0);

-- ============================================
-- GOLD ARMOR SET (Speed focused)
-- ============================================
INSERT OR REPLACE INTO game_items (item_id, name, rarity, item_type, stats, lore, special_ability, craft_recipe, npc_sell_price, collection_req, default_bazaar_price)
VALUES 
('gold_helmet', 'Gold Helmet', 'UNCOMMON', 'HELMET', '{"defense": 15, "health": 20, "speed": 5}', 'Lightweight golden armor', '', '{"gold_ingot": 5}', 100, '{}', 200),
('gold_chestplate', 'Gold Chestplate', 'UNCOMMON', 'CHESTPLATE', '{"defense": 25, "health": 30, "speed": 8}', 'Lightweight golden armor', '', '{"gold_ingot": 8}', 160, '{}', 320),
('gold_leggings', 'Gold Leggings', 'UNCOMMON', 'LEGGINGS', '{"defense": 20, "health": 25, "speed": 6}', 'Lightweight golden armor', '', '{"gold_ingot": 7}', 140, '{}', 280),
('gold_boots', 'Gold Boots', 'UNCOMMON', 'BOOTS', '{"defense": 12, "health": 15, "speed": 4}', 'Lightweight golden armor', '', '{"gold_ingot": 4}', 80, '{}', 160);

INSERT OR REPLACE INTO armor_stats (item_id, defense, health, strength, crit_chance, crit_damage, intelligence, speed, magic_find, pet_luck, true_defense)
VALUES 
('gold_helmet', 15, 20, 0, 0, 0, 0, 5, 0, 0, 0),
('gold_chestplate', 25, 30, 0, 0, 0, 0, 8, 0, 0, 0),
('gold_leggings', 20, 25, 0, 0, 0, 0, 6, 0, 0, 0),
('gold_boots', 12, 15, 0, 0, 0, 0, 4, 0, 0, 0);

-- ============================================
-- DIAMOND ARMOR SET
-- ============================================
INSERT OR REPLACE INTO game_items (item_id, name, rarity, item_type, stats, lore, special_ability, craft_recipe, npc_sell_price, collection_req, default_bazaar_price)
VALUES 
('diamond_helmet', 'Diamond Helmet', 'UNCOMMON', 'HELMET', '{"defense": 45, "health": 50, "strength": 5}', 'Premium diamond protection', '', '{"diamond": 5}', 500, '{}', 1000),
('diamond_chestplate', 'Diamond Chestplate', 'UNCOMMON', 'CHESTPLATE', '{"defense": 70, "health": 80, "strength": 10}', 'Premium diamond protection', '', '{"diamond": 8}', 800, '{}', 1600),
('diamond_leggings', 'Diamond Leggings', 'UNCOMMON', 'LEGGINGS', '{"defense": 60, "health": 65, "strength": 8}', 'Premium diamond protection', '', '{"diamond": 7}', 700, '{}', 1400),
('diamond_boots', 'Diamond Boots', 'UNCOMMON', 'BOOTS', '{"defense": 35, "health": 40, "strength": 5}', 'Premium diamond protection', '', '{"diamond": 4}', 400, '{}', 800);

INSERT OR REPLACE INTO armor_stats (item_id, defense, health, strength, crit_chance, crit_damage, intelligence, speed, magic_find, pet_luck, true_defense)
VALUES 
('diamond_helmet', 45, 50, 5, 0, 0, 0, 0, 0, 0, 0),
('diamond_chestplate', 70, 80, 10, 0, 0, 0, 0, 0, 0, 0),
('diamond_leggings', 60, 65, 8, 0, 0, 0, 0, 0, 0, 0),
('diamond_boots', 35, 40, 5, 0, 0, 0, 0, 0, 0, 0);

-- ============================================
-- HARDENED DIAMOND ARMOR SET (Already exists, updating)
-- ============================================
INSERT OR REPLACE INTO game_items (item_id, name, rarity, item_type, stats, lore, special_ability, craft_recipe, npc_sell_price, collection_req, default_bazaar_price)
VALUES 
('hardened_diamond_chestplate', 'Hardened Diamond Chestplate', 'RARE', 'CHESTPLATE', '{"defense": 100, "health": 120, "strength": 15}', 'Reinforced diamond armor|Provides excellent protection', '', '{"diamond": 24, "enchanted_diamond": 4}', 2000, '{}', 4000),
('hardened_diamond_leggings', 'Hardened Diamond Leggings', 'RARE', 'LEGGINGS', '{"defense": 85, "health": 100, "strength": 12}', 'Reinforced diamond armor|Provides excellent protection', '', '{"diamond": 21, "enchanted_diamond": 3}', 1800, '{}', 3600),
('hardened_diamond_boots', 'Hardened Diamond Boots', 'RARE', 'BOOTS', '{"defense": 55, "health": 65, "strength": 8}', 'Reinforced diamond armor|Provides excellent protection', '', '{"diamond": 12, "enchanted_diamond": 2}', 1200, '{}', 2400);

INSERT OR REPLACE INTO armor_stats (item_id, defense, health, strength, crit_chance, crit_damage, intelligence, speed, magic_find, pet_luck, true_defense)
VALUES 
('hardened_diamond_chestplate', 100, 120, 15, 0, 0, 0, 0, 0, 0, 0),
('hardened_diamond_leggings', 85, 100, 12, 0, 0, 0, 0, 0, 0, 0),
('hardened_diamond_boots', 55, 65, 8, 0, 0, 0, 0, 0, 0, 0);

-- ============================================
-- EMERALD ARMOR SET (Intelligence focused)
-- ============================================
INSERT OR REPLACE INTO game_items (item_id, name, rarity, item_type, stats, lore, special_ability, craft_recipe, npc_sell_price, collection_req, default_bazaar_price)
VALUES 
('emerald_helmet', 'Emerald Helmet', 'RARE', 'HELMET', '{"defense": 35, "health": 40, "intelligence": 50}', 'Magical emerald headgear|Increases mana capacity', '', '{"emerald": 40}', 800, '{}', 1600),
('emerald_chestplate', 'Emerald Chestplate', 'RARE', 'CHESTPLATE', '{"defense": 60, "health": 70, "intelligence": 80}', 'Magical emerald armor|Increases mana capacity', '', '{"emerald": 64}', 1280, '{}', 2560),
('emerald_leggings', 'Emerald Leggings', 'RARE', 'LEGGINGS', '{"defense": 50, "health": 55, "intelligence": 65}', 'Magical emerald legwear|Increases mana capacity', '', '{"emerald": 56}', 1120, '{}', 2240),
('emerald_boots', 'Emerald Boots', 'RARE', 'BOOTS', '{"defense": 30, "health": 35, "intelligence": 40}', 'Magical emerald boots|Increases mana capacity', '', '{"emerald": 32}', 640, '{}', 1280);

INSERT OR REPLACE INTO armor_stats (item_id, defense, health, strength, crit_chance, crit_damage, intelligence, speed, magic_find, pet_luck, true_defense)
VALUES 
('emerald_helmet', 35, 40, 0, 0, 0, 50, 0, 0, 0, 0),
('emerald_chestplate', 60, 70, 0, 0, 0, 80, 0, 0, 0, 0),
('emerald_leggings', 50, 55, 0, 0, 0, 65, 0, 0, 0, 0),
('emerald_boots', 30, 35, 0, 0, 0, 40, 0, 0, 0, 0);

-- ============================================
-- YOUNG DRAGON ARMOR SET (Speed focused)
-- ============================================
INSERT OR REPLACE INTO game_items (item_id, name, rarity, item_type, stats, lore, special_ability, craft_recipe, npc_sell_price, collection_req, default_bazaar_price)
VALUES 
('young_dragon_chestplate', 'Young Dragon Chestplate', 'LEGENDARY', 'CHESTPLATE', '{"defense": 120, "health": 160, "speed": 50}', 'Armor of the Young Dragon|Increases movement speed|Full Set Bonus: +100 Speed', 'Young Blood: +70% Speed', '{"young_dragon_fragment": 80, "enchanted_ender_pearl": 32}', 10000, '{}', 50000),
('young_dragon_leggings', 'Young Dragon Leggings', 'LEGENDARY', 'LEGGINGS', '{"defense": 100, "health": 140, "speed": 40}', 'Armor of the Young Dragon|Increases movement speed|Full Set Bonus: +100 Speed', 'Young Blood: +70% Speed', '{"young_dragon_fragment": 70, "enchanted_ender_pearl": 28}', 9000, '{}', 45000),
('young_dragon_boots', 'Young Dragon Boots', 'LEGENDARY', 'BOOTS', '{"defense": 70, "health": 100, "speed": 30}', 'Armor of the Young Dragon|Increases movement speed|Full Set Bonus: +100 Speed', 'Young Blood: +70% Speed', '{"young_dragon_fragment": 50, "enchanted_ender_pearl": 20}', 7000, '{}', 35000);

INSERT OR REPLACE INTO armor_stats (item_id, defense, health, strength, crit_chance, crit_damage, intelligence, speed, magic_find, pet_luck, true_defense)
VALUES 
('young_dragon_chestplate', 120, 160, 0, 0, 0, 0, 50, 0, 0, 0),
('young_dragon_leggings', 100, 140, 0, 0, 0, 0, 40, 0, 0, 0),
('young_dragon_boots', 70, 100, 0, 0, 0, 0, 30, 0, 0, 0);

-- ============================================
-- STRONG DRAGON ARMOR SET (Strength focused)
-- ============================================
INSERT OR REPLACE INTO game_items (item_id, name, rarity, item_type, stats, lore, special_ability, craft_recipe, npc_sell_price, collection_req, default_bazaar_price)
VALUES 
('strong_dragon_chestplate', 'Strong Dragon Chestplate', 'LEGENDARY', 'CHESTPLATE', '{"defense": 140, "health": 200, "strength": 40}', 'Armor of the Strong Dragon|Grants immense strength|Full Set Bonus: +100 Strength', 'Superior Strength: Deal more damage', '{"strong_dragon_fragment": 80, "enchanted_diamond": 64}', 12000, '{}', 60000),
('strong_dragon_leggings', 'Strong Dragon Leggings', 'LEGENDARY', 'LEGGINGS', '{"defense": 115, "health": 170, "strength": 35}', 'Armor of the Strong Dragon|Grants immense strength|Full Set Bonus: +100 Strength', 'Superior Strength: Deal more damage', '{"strong_dragon_fragment": 70, "enchanted_diamond": 56}', 10500, '{}', 52500),
('strong_dragon_boots', 'Strong Dragon Boots', 'LEGENDARY', 'BOOTS', '{"defense": 70, "health": 100, "strength": 25}', 'Armor of the Strong Dragon|Grants immense strength|Full Set Bonus: +100 Strength', 'Superior Strength: Deal more damage', '{"strong_dragon_fragment": 50, "enchanted_diamond": 40}', 7500, '{}', 37500);

INSERT OR REPLACE INTO armor_stats (item_id, defense, health, strength, crit_chance, crit_damage, intelligence, speed, magic_find, pet_luck, true_defense)
VALUES 
('strong_dragon_chestplate', 140, 200, 40, 0, 0, 0, 0, 0, 0, 0),
('strong_dragon_leggings', 115, 170, 35, 0, 0, 0, 0, 0, 0, 0),
('strong_dragon_boots', 70, 100, 25, 0, 0, 0, 0, 0, 0, 0);

-- ============================================
-- WISE DRAGON ARMOR SET (Intelligence focused)
-- ============================================
INSERT OR REPLACE INTO game_items (item_id, name, rarity, item_type, stats, lore, special_ability, craft_recipe, npc_sell_price, collection_req, default_bazaar_price)
VALUES 
('wise_dragon_helmet', 'Wise Dragon Helmet', 'LEGENDARY', 'HELMET', '{"defense": 90, "health": 130, "intelligence": 125}', 'Helmet of the Wise Dragon|Massive mana pool|Full Set Bonus: +200 Intelligence', 'Wisdom: Abilities cost less mana', '{"wise_dragon_fragment": 60, "enchanted_lapis_block": 32}', 9000, '{}', 45000),
('wise_dragon_chestplate', 'Wise Dragon Chestplate', 'LEGENDARY', 'CHESTPLATE', '{"defense": 140, "health": 200, "intelligence": 175}', 'Armor of the Wise Dragon|Massive mana pool|Full Set Bonus: +200 Intelligence', 'Wisdom: Abilities cost less mana', '{"wise_dragon_fragment": 80, "enchanted_lapis_block": 64}', 12000, '{}', 60000),
('wise_dragon_leggings', 'Wise Dragon Leggings', 'LEGENDARY', 'LEGGINGS', '{"defense": 115, "health": 170, "intelligence": 150}', 'Leggings of the Wise Dragon|Massive mana pool|Full Set Bonus: +200 Intelligence', 'Wisdom: Abilities cost less mana', '{"wise_dragon_fragment": 70, "enchanted_lapis_block": 56}', 10500, '{}', 52500),
('wise_dragon_boots', 'Wise Dragon Boots', 'LEGENDARY', 'BOOTS', '{"defense": 70, "health": 100, "intelligence": 100}', 'Boots of the Wise Dragon|Massive mana pool|Full Set Bonus: +200 Intelligence', 'Wisdom: Abilities cost less mana', '{"wise_dragon_fragment": 50, "enchanted_lapis_block": 40}', 7500, '{}', 37500);

INSERT OR REPLACE INTO armor_stats (item_id, defense, health, strength, crit_chance, crit_damage, intelligence, speed, magic_find, pet_luck, true_defense)
VALUES 
('wise_dragon_helmet', 90, 130, 0, 0, 0, 125, 0, 0, 0, 0),
('wise_dragon_chestplate', 140, 200, 0, 0, 0, 175, 0, 0, 0, 0),
('wise_dragon_leggings', 115, 170, 0, 0, 0, 150, 0, 0, 0, 0),
('wise_dragon_boots', 70, 100, 0, 0, 0, 100, 0, 0, 0, 0);

-- ============================================
-- SUPERIOR DRAGON ARMOR SET (Balanced Legendary)
-- ============================================
INSERT OR REPLACE INTO game_items (item_id, name, rarity, item_type, stats, lore, special_ability, craft_recipe, npc_sell_price, collection_req, default_bazaar_price)
VALUES 
('superior_dragon_helmet', 'Superior Dragon Helmet', 'LEGENDARY', 'HELMET', '{"defense": 110, "health": 150, "strength": 20, "crit_damage": 20, "intelligence": 50}', 'Helmet of the Superior Dragon|Balanced and powerful|Full Set Bonus: +50 to all stats', 'Superior: All stats increased', '{"superior_dragon_fragment": 60, "nether_star": 4}', 20000, '{}', 100000),
('superior_dragon_chestplate', 'Superior Dragon Chestplate', 'LEGENDARY', 'CHESTPLATE', '{"defense": 170, "health": 230, "strength": 30, "crit_damage": 30, "intelligence": 75}', 'Armor of the Superior Dragon|Balanced and powerful|Full Set Bonus: +50 to all stats', 'Superior: All stats increased', '{"superior_dragon_fragment": 80, "nether_star": 8}', 30000, '{}', 150000),
('superior_dragon_leggings', 'Superior Dragon Leggings', 'LEGENDARY', 'LEGGINGS', '{"defense": 140, "health": 190, "strength": 25, "crit_damage": 25, "intelligence": 60}', 'Leggings of the Superior Dragon|Balanced and powerful|Full Set Bonus: +50 to all stats', 'Superior: All stats increased', '{"superior_dragon_fragment": 70, "nether_star": 6}', 25000, '{}', 125000),
('superior_dragon_boots', 'Superior Dragon Boots', 'LEGENDARY', 'BOOTS', '{"defense": 90, "health": 130, "strength": 15, "crit_damage": 15, "intelligence": 40}', 'Boots of the Superior Dragon|Balanced and powerful|Full Set Bonus: +50 to all stats', 'Superior: All stats increased', '{"superior_dragon_fragment": 50, "nether_star": 4}', 15000, '{}', 75000);

INSERT OR REPLACE INTO armor_stats (item_id, defense, health, strength, crit_chance, crit_damage, intelligence, speed, magic_find, pet_luck, true_defense)
VALUES 
('superior_dragon_helmet', 110, 150, 20, 0, 20, 50, 0, 0, 0, 0),
('superior_dragon_chestplate', 170, 230, 30, 0, 30, 75, 0, 0, 0, 0),
('superior_dragon_leggings', 140, 190, 25, 0, 25, 60, 0, 0, 0, 0),
('superior_dragon_boots', 90, 130, 15, 0, 15, 40, 0, 0, 0, 0);

-- ============================================
-- TOOLS - PICKAXES
-- ============================================
INSERT OR REPLACE INTO game_items (item_id, name, rarity, item_type, stats, lore, special_ability, craft_recipe, npc_sell_price, collection_req, default_bazaar_price)
VALUES 
('stone_pickaxe', 'Stone Pickaxe', 'COMMON', 'PICKAXE', '{"damage": 15, "mining_speed": 20}', 'Better than wood at least', '', '{"stick": 2, "cobblestone": 3}', 10, '{}', 20),
('gold_pickaxe', 'Gold Pickaxe', 'UNCOMMON', 'PICKAXE', '{"damage": 18, "mining_speed": 50, "mining_fortune": 5}', 'Fast but fragile', '', '{"stick": 2, "gold_ingot": 3}', 50, '{}', 100),
('iron_pickaxe', 'Iron Pickaxe', 'COMMON', 'PICKAXE', '{"damage": 20, "mining_speed": 40, "mining_fortune": 10}', 'Good mining tool|Can mine most ores', '', '{"stick": 2, "iron_ingot": 3}', 100, '{}', 200),
('diamond_pickaxe', 'Diamond Pickaxe', 'UNCOMMON', 'PICKAXE', '{"damage": 30, "mining_speed": 80, "mining_fortune": 25}', 'Great mining tool|Can mine all ores', '', '{"stick": 2, "diamond": 3}', 500, '{}', 1000),
('mithril_pickaxe', 'Mithril Pickaxe', 'RARE', 'PICKAXE', '{"damage": 40, "mining_speed": 120, "mining_fortune": 40, "breaking_power": 4}', 'Enchanted mining tool|Excellent for deep mining', 'Efficient Miner', '{"diamond_pickaxe": 1, "enchanted_mithril": 16}', 2000, '{}', 4000),
('titanium_pickaxe', 'Titanium Pickaxe', 'EPIC', 'PICKAXE', '{"damage": 50, "mining_speed": 180, "mining_fortune": 60, "breaking_power": 6}', 'Superior mining tool|Breaks through anything|Fortune bonus on ores', 'Titanium Power', '{"mithril_pickaxe": 1, "titanium": 32}', 5000, '{}', 10000);

INSERT OR REPLACE INTO tool_stats (item_id, tool_type, damage, breaking_power, mining_speed, mining_fortune, farming_fortune, foraging_fortune, fishing_speed, sea_creature_chance, crop_yield_multiplier, wood_yield_multiplier, ore_yield_multiplier, durability)
VALUES 
('stone_pickaxe', 'pickaxe', 15, 2, 20, 0, 0, 0, 0, 0, 1.0, 1.0, 1.0, 100),
('gold_pickaxe', 'pickaxe', 18, 2, 50, 5, 0, 0, 0, 0, 1.0, 1.0, 1.0, 50),
('iron_pickaxe', 'pickaxe', 20, 3, 40, 10, 0, 0, 0, 0, 1.0, 1.0, 1.05, 200),
('diamond_pickaxe', 'pickaxe', 30, 4, 80, 25, 0, 0, 0, 0, 1.0, 1.0, 1.1, 500),
('mithril_pickaxe', 'pickaxe', 40, 4, 120, 40, 0, 0, 0, 0, 1.0, 1.0, 1.15, 1000),
('titanium_pickaxe', 'pickaxe', 50, 6, 180, 60, 0, 0, 0, 0, 1.0, 1.0, 1.25, 2000);

-- ============================================
-- TOOLS - AXES
-- ============================================
INSERT OR REPLACE INTO game_items (item_id, name, rarity, item_type, stats, lore, special_ability, craft_recipe, npc_sell_price, collection_req, default_bazaar_price)
VALUES 
('wooden_axe', 'Wooden Axe', 'COMMON', 'AXE', '{"damage": 15, "foraging_fortune": 5}', 'Basic chopping tool', '', '{"stick": 2, "oak_wood": 3}', 5, '{}', 10),
('stone_axe', 'Stone Axe', 'COMMON', 'AXE', '{"damage": 20, "foraging_fortune": 10}', 'Better chopping tool', '', '{"stick": 2, "cobblestone": 3}', 10, '{}', 20),
('iron_axe', 'Iron Axe', 'COMMON', 'AXE', '{"damage": 25, "foraging_fortune": 15}', 'Good chopping tool|Faster than stone', '', '{"stick": 2, "iron_ingot": 3}', 50, '{}', 100),
('diamond_axe', 'Diamond Axe', 'UNCOMMON', 'AXE', '{"damage": 35, "foraging_fortune": 25}', 'Great chopping tool|Extra wood drops', '', '{"stick": 2, "diamond": 3}', 250, '{}', 500),
('jungle_axe', 'Jungle Axe', 'RARE', 'AXE', '{"damage": 40, "foraging_fortune": 40}', 'Chops entire trees instantly!|Bonus wood from jungle logs', 'Timber: Break whole trees', '{"diamond_axe": 1, "enchanted_jungle_wood": 64}', 1500, '{}', 3000),
('treecapitator', 'Treecapitator', 'EPIC', 'AXE', '{"damage": 50, "foraging_fortune": 60}', 'The ultimate logging tool|Breaks entire trees|Massive fortune bonus', 'Timbersaw: Instant tree destruction', '{"jungle_axe": 1, "enchanted_oak_wood": 128, "enchanted_dark_oak_wood": 64}', 5000, '{}', 10000);

INSERT OR REPLACE INTO tool_stats (item_id, tool_type, damage, breaking_power, mining_speed, mining_fortune, farming_fortune, foraging_fortune, fishing_speed, sea_creature_chance, crop_yield_multiplier, wood_yield_multiplier, ore_yield_multiplier, durability)
VALUES 
('wooden_axe', 'axe', 15, 0, 0, 0, 0, 5, 0, 0, 1.0, 1.0, 1.0, 50),
('stone_axe', 'axe', 20, 0, 0, 0, 0, 10, 0, 0, 1.0, 1.05, 1.0, 100),
('iron_axe', 'axe', 25, 0, 0, 0, 0, 15, 0, 0, 1.0, 1.1, 1.0, 200),
('diamond_axe', 'axe', 35, 0, 0, 0, 0, 25, 0, 0, 1.0, 1.15, 1.0, 500),
('jungle_axe', 'axe', 40, 0, 0, 0, 0, 40, 0, 0, 1.0, 1.25, 1.0, 1000),
('treecapitator', 'axe', 50, 0, 0, 0, 0, 60, 0, 0, 1.0, 1.5, 1.0, 2000);

-- ============================================
-- TOOLS - HOES
-- ============================================
INSERT OR REPLACE INTO game_items (item_id, name, rarity, item_type, stats, lore, special_ability, craft_recipe, npc_sell_price, collection_req, default_bazaar_price)
VALUES 
('wooden_hoe', 'Wooden Hoe', 'COMMON', 'HOE', '{"farming_fortune": 10}', 'Basic farming tool', '', '{"stick": 2, "oak_wood": 2}', 5, '{}', 10),
('stone_hoe', 'Stone Hoe', 'COMMON', 'HOE', '{"farming_fortune": 20}', 'Better farming tool', '', '{"stick": 2, "cobblestone": 2}', 10, '{}', 20),
('iron_hoe', 'Iron Hoe', 'COMMON', 'HOE', '{"farming_fortune": 30}', 'Good farming tool', '', '{"stick": 2, "iron_ingot": 2}', 50, '{}', 100),
('diamond_hoe', 'Diamond Hoe', 'UNCOMMON', 'HOE', '{"farming_fortune": 50}', 'Great farming tool|Bonus crop drops', '', '{"stick": 2, "diamond": 2}', 250, '{}', 500),
('blessed_hoe', 'Blessed Hoe', 'RARE', 'HOE', '{"farming_fortune": 80}', 'Enchanted farming tool|Greatly increases crop yield', 'Blessed Harvest', '{"diamond_hoe": 1, "enchanted_hay_bale": 32}', 2000, '{}', 4000),
('mathematical_hoe', 'Mathematical Hoe Blueprint', 'EPIC', 'HOE', '{"farming_fortune": 120}', 'Calculates optimal farming|Maximum crop efficiency|Legendary yield multiplier', 'Perfect Farming: 2x crop drops', '{"blessed_hoe": 1, "enchanted_melon_block": 64, "enchanted_pumpkin": 64}', 8000, '{}', 16000);

INSERT OR REPLACE INTO tool_stats (item_id, tool_type, damage, breaking_power, mining_speed, mining_fortune, farming_fortune, foraging_fortune, fishing_speed, sea_creature_chance, crop_yield_multiplier, wood_yield_multiplier, ore_yield_multiplier, durability)
VALUES 
('wooden_hoe', 'hoe', 0, 0, 0, 0, 10, 0, 0, 0, 1.05, 1.0, 1.0, 50),
('stone_hoe', 'hoe', 0, 0, 0, 0, 20, 0, 0, 0, 1.1, 1.0, 1.0, 100),
('iron_hoe', 'hoe', 0, 0, 0, 0, 30, 0, 0, 0, 1.15, 1.0, 1.0, 200),
('diamond_hoe', 'hoe', 0, 0, 0, 0, 50, 0, 0, 0, 1.25, 1.0, 1.0, 500),
('blessed_hoe', 'hoe', 0, 0, 0, 0, 80, 0, 0, 0, 1.4, 1.0, 1.0, 1000),
('mathematical_hoe', 'hoe', 0, 0, 0, 0, 120, 0, 0, 0, 2.0, 1.0, 1.0, 2000);

-- ============================================
-- TOOLS - FISHING RODS
-- ============================================
INSERT OR REPLACE INTO game_items (item_id, name, rarity, item_type, stats, lore, special_ability, craft_recipe, npc_sell_price, collection_req, default_bazaar_price)
VALUES 
('fishing_rod', 'Fishing Rod', 'COMMON', 'FISHING_ROD', '{"fishing_speed": 10}', 'Basic fishing rod|Catch common fish', '', '{"stick": 3, "string": 2}', 10, '{}', 20),
('prismarine_rod', 'Prismarine Rod', 'UNCOMMON', 'FISHING_ROD', '{"fishing_speed": 25, "sea_creature_chance": 5}', 'Ocean-enchanted rod|Catches fish faster', '', '{"fishing_rod": 1, "prismarine_shard": 16}', 100, '{}', 200),
('sponge_rod', 'Sponge Rod', 'RARE', 'FISHING_ROD', '{"fishing_speed": 40, "sea_creature_chance": 10}', 'Absorbs water energy|Great for sea creatures', 'Sponge: +Sea Creature Chance', '{"prismarine_rod": 1, "sponge": 8}', 500, '{}', 1000),
('rod_of_champions', 'Rod of Champions', 'EPIC', 'FISHING_ROD', '{"fishing_speed": 70, "sea_creature_chance": 20}', 'The champion''s choice|Excellent sea creature rates|Rare catch bonus', 'Champion Fisher', '{"sponge_rod": 1, "enchanted_sponge": 16, "enchanted_prismarine": 32}', 3000, '{}', 6000),
('rod_of_legends', 'Rod of Legends', 'LEGENDARY', 'FISHING_ROD', '{"fishing_speed": 100, "sea_creature_chance": 35}', 'Legendary fishing power|Summons mythical creatures|Best fishing rod available', 'Legendary Catch: Double drops', '{"rod_of_champions": 1, "enchanted_sponge": 64, "sea_lantern": 32}', 10000, '{}', 50000);

INSERT OR REPLACE INTO tool_stats (item_id, tool_type, damage, breaking_power, mining_speed, mining_fortune, farming_fortune, foraging_fortune, fishing_speed, sea_creature_chance, crop_yield_multiplier, wood_yield_multiplier, ore_yield_multiplier, durability)
VALUES 
('fishing_rod', 'fishing_rod', 0, 0, 0, 0, 0, 0, 10, 1, 1.0, 1.0, 1.0, 100),
('prismarine_rod', 'fishing_rod', 0, 0, 0, 0, 0, 0, 25, 5, 1.0, 1.0, 1.0, 200),
('sponge_rod', 'fishing_rod', 0, 0, 0, 0, 0, 0, 40, 10, 1.0, 1.0, 1.0, 400),
('rod_of_champions', 'fishing_rod', 0, 0, 0, 0, 0, 0, 70, 20, 1.0, 1.0, 1.0, 800),
('rod_of_legends', 'fishing_rod', 0, 0, 0, 0, 0, 0, 100, 35, 1.0, 1.0, 1.0, 2000);

-- ============================================
-- WEAPONS - SWORDS
-- ============================================
INSERT OR REPLACE INTO game_items (item_id, name, rarity, item_type, stats, lore, special_ability, craft_recipe, npc_sell_price, collection_req, default_bazaar_price)
VALUES 
('gold_sword', 'Gold Sword', 'UNCOMMON', 'SWORD', '{"damage": 35, "strength": 5}', 'Golden blade|Looks fancy but brittle', '', '{"stick": 1, "gold_ingot": 2}', 100, '{}', 200),
('cleaver', 'Cleaver', 'RARE', 'SWORD', '{"damage": 80, "strength": 30}', 'Heavy meat cleaver|Cleaves through enemies', 'Cleave: Deal AoE damage', '{"iron_sword": 1, "enchanted_pork": 32}', 800, '{}', 1600),
('silver_fang', 'Silver Fang', 'RARE', 'SWORD', '{"damage": 100, "strength": 40, "crit_chance": 15}', 'Swift silver blade|High critical chance|Bonus vs undead', 'Fang Strike', '{"diamond_sword": 1, "enchanted_quartz": 32, "wolf_tooth": 16}', 2000, '{}', 4000),
('golem_sword', 'Golem Sword', 'RARE', 'SWORD', '{"damage": 90, "strength": 60}', 'Forged from golem cores|Massive strength bonus', 'Golem Strength: +50 Defense when held', '{"diamond_sword": 1, "enchanted_iron_block": 16}', 2500, '{}', 5000),
('ember_rod', 'Ember Rod', 'EPIC', 'SWORD', '{"damage": 120, "strength": 50, "crit_damage": 30}', 'Blazing hot weapon|Burns enemies|Fire damage over time', 'Inferno: Set enemies on fire', '{"blaze_rod": 128, "enchanted_blaze_powder": 32}', 5000, '{}', 10000),
('frozen_scythe', 'Frozen Scythe', 'EPIC', 'SWORD', '{"damage": 140, "strength": 40, "crit_damage": 50, "intelligence": 25}', 'Icy weapon of death|Slows enemies|Critical hits freeze targets', 'Frozen Touch: Slow and freeze', '{"diamond_sword": 1, "ice": 64, "packed_ice": 32}', 6000, '{}', 12000);

INSERT OR REPLACE INTO weapon_stats (item_id, damage, strength, crit_chance, crit_damage, attack_speed, ability_damage, ferocity, bonus_attack_speed)
VALUES 
('gold_sword', 35, 5, 0, 0, 0, 0, 0, 0),
('cleaver', 80, 30, 0, 0, -10, 0, 0, 0),
('silver_fang', 100, 40, 15, 0, 10, 0, 0, 0.1),
('golem_sword', 90, 60, 0, 0, -20, 0, 0, 0),
('ember_rod', 120, 50, 0, 30, 0, 50, 10, 0),
('frozen_scythe', 140, 40, 0, 50, 0, 30, 0, 0);

-- ============================================
-- SPECIAL ARMOR - FARMING SET
-- ============================================
INSERT OR REPLACE INTO game_items (item_id, name, rarity, item_type, stats, lore, special_ability, craft_recipe, npc_sell_price, collection_req, default_bazaar_price)
VALUES 
('farmer_helmet', 'Farmer Helmet', 'RARE', 'HELMET', '{"defense": 20, "health": 30, "farming_fortune": 30}', 'For dedicated farmers|Increases crop yields', '', '{"hay_bale": 40, "enchanted_seeds": 16}', 500, '{}', 1000),
('farmer_chestplate', 'Farmer Chestplate', 'RARE', 'CHESTPLATE', '{"defense": 35, "health": 50, "farming_fortune": 50}', 'For dedicated farmers|Increases crop yields|Full Set: +100 Farming Fortune', '', '{"hay_bale": 64, "enchanted_seeds": 32}', 800, '{}', 1600),
('farmer_leggings', 'Farmer Leggings', 'RARE', 'LEGGINGS', '{"defense": 30, "health": 40, "farming_fortune": 40}', 'For dedicated farmers|Increases crop yields', '', '{"hay_bale": 56, "enchanted_seeds": 24}', 700, '{}', 1400),
('farmer_boots', 'Farmer Boots', 'RARE', 'BOOTS', '{"defense": 18, "health": 25, "farming_fortune": 25}', 'For dedicated farmers|Increases crop yields', '', '{"hay_bale": 32, "enchanted_seeds": 16}', 400, '{}', 800);

INSERT OR REPLACE INTO armor_stats (item_id, defense, health, strength, crit_chance, crit_damage, intelligence, speed, magic_find, pet_luck, true_defense)
VALUES 
('farmer_helmet', 20, 30, 0, 0, 0, 0, 0, 0, 0, 0),
('farmer_chestplate', 35, 50, 0, 0, 0, 0, 0, 0, 0, 0),
('farmer_leggings', 30, 40, 0, 0, 0, 0, 0, 0, 0, 0),
('farmer_boots', 18, 25, 0, 0, 0, 0, 0, 0, 0, 0);

-- ============================================
-- SPECIAL ARMOR - MINER SET
-- ============================================
INSERT OR REPLACE INTO game_items (item_id, name, rarity, item_type, stats, lore, special_ability, craft_recipe, npc_sell_price, collection_req, default_bazaar_price)
VALUES 
('miner_helmet', 'Miner Helmet', 'RARE', 'HELMET', '{"defense": 25, "health": 35, "mining_fortune": 40}', 'Reinforced mining helmet|Built-in headlamp|Ore detection', 'Night Vision', '{"iron_block": 20, "enchanted_coal": 16}', 600, '{}', 1200),
('miner_chestplate', 'Miner Chestplate', 'RARE', 'CHESTPLATE', '{"defense": 45, "health": 60, "mining_fortune": 60}', 'Heavy duty protection|Perfect for deep mining|Full Set: +150 Mining Fortune', '', '{"iron_block": 32, "enchanted_coal": 32}', 1000, '{}', 2000),
('miner_leggings', 'Miner Leggings', 'RARE', 'LEGGINGS', '{"defense": 35, "health": 48, "mining_fortune": 50}', 'Reinforced mining pants|Protection underground', '', '{"iron_block": 28, "enchanted_coal": 24}', 850, '{}', 1700),
('miner_boots', 'Miner Boots', 'RARE', 'BOOTS', '{"defense": 22, "health": 30, "mining_fortune": 35, "speed": 5}', 'Steel-toed mining boots|Move faster in caves', '', '{"iron_block": 16, "enchanted_coal": 16}', 500, '{}', 1000);

INSERT OR REPLACE INTO armor_stats (item_id, defense, health, strength, crit_chance, crit_damage, intelligence, speed, magic_find, pet_luck, true_defense)
VALUES 
('miner_helmet', 25, 35, 0, 0, 0, 0, 0, 0, 0, 0),
('miner_chestplate', 45, 60, 0, 0, 0, 0, 0, 0, 0, 0),
('miner_leggings', 35, 48, 0, 0, 0, 0, 0, 0, 0, 0),
('miner_boots', 22, 30, 0, 0, 0, 0, 5, 0, 0, 0);
