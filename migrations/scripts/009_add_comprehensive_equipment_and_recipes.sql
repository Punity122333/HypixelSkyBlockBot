-- ============================================
-- COMPREHENSIVE EQUIPMENT AND CRAFTING SYSTEM
-- Adds 15+ new swords, ensures all crafting dependencies exist
-- ============================================

-- ============================================
-- BASIC MATERIALS (Used in crafting recipes)
-- ============================================

INSERT OR IGNORE INTO game_items (item_id, name, rarity, item_type, stats, lore, special_ability, craft_recipe, npc_sell_price, collection_req, default_bazaar_price)
VALUES
-- Basic Vanilla Materials
('stick', 'Stick', 'COMMON', 'MATERIAL', '{}', 'A simple wooden stick', '', '{"oak_wood": 2}', 1, '{}', 2),
('oak_wood', 'Oak Wood', 'COMMON', 'MATERIAL', '{}', 'Wood from an oak tree', '', '{}', 2, '{}', 4),
('cobblestone', 'Cobblestone', 'COMMON', 'MATERIAL', '{}', 'Basic stone material', '', '{}', 1, '{}', 2),
('iron_ingot', 'Iron Ingot', 'COMMON', 'MATERIAL', '{}', 'A refined iron ingot', '', '{}', 5, '{}', 10),
('gold_ingot', 'Gold Ingot', 'COMMON', 'MATERIAL', '{}', 'A shiny gold ingot', '', '{}', 8, '{}', 16),
('diamond', 'Diamond', 'RARE', 'MATERIAL', '{}', 'A precious diamond', '', '{}', 50, '{}', 100),
('emerald', 'Emerald', 'UNCOMMON', 'MATERIAL', '{}', 'A green emerald', '', '{}', 20, '{}', 40),
('leather', 'Leather', 'COMMON', 'MATERIAL', '{}', 'Tanned animal hide', '', '{}', 3, '{}', 6),
('string', 'String', 'COMMON', 'MATERIAL', '{}', 'String from spiders', '', '{}', 2, '{}', 4),
('bone', 'Bone', 'COMMON', 'MATERIAL', '{}', 'A skeleton bone', '', '{}', 2, '{}', 4),

-- Enchanted Materials (Tier 1)
('enchanted_oak_wood', 'Enchanted Oak Wood', 'UNCOMMON', 'MATERIAL', '{}', 'Compressed oak wood', '', '{"oak_wood": 160}', 320, '{}', 640),
('enchanted_cobblestone', 'Enchanted Cobblestone', 'UNCOMMON', 'MATERIAL', '{}', 'Compressed cobblestone', '', '{"cobblestone": 160}', 160, '{}', 320),
('enchanted_iron', 'Enchanted Iron', 'UNCOMMON', 'MATERIAL', '{}', 'Compressed iron', '', '{"iron_ingot": 160}', 800, '{}', 1600),
('enchanted_gold', 'Enchanted Gold', 'UNCOMMON', 'MATERIAL', '{}', 'Compressed gold', '', '{"gold_ingot": 160}', 1280, '{}', 2560),
('enchanted_diamond', 'Enchanted Diamond', 'RARE', 'MATERIAL', '{}', 'Compressed diamonds', '', '{"diamond": 160}', 8000, '{}', 16000),
('enchanted_emerald', 'Enchanted Emerald', 'RARE', 'MATERIAL', '{}', 'Compressed emeralds', '', '{"emerald": 160}', 3200, '{}', 6400),
('enchanted_string', 'Enchanted String', 'UNCOMMON', 'MATERIAL', '{}', 'Compressed string', '', '{"string": 160}', 320, '{}', 640),
('enchanted_bone', 'Enchanted Bone', 'UNCOMMON', 'MATERIAL', '{}', 'Compressed bones', '', '{"bone": 160}', 320, '{}', 640),

-- Enchanted Materials (Tier 2 - Made from Tier 1)
('enchanted_iron_block', 'Enchanted Iron Block', 'RARE', 'MATERIAL', '{}', 'Super compressed iron', '', '{"enchanted_iron": 160}', 128000, '{}', 256000),
('enchanted_gold_block', 'Enchanted Gold Block', 'RARE', 'MATERIAL', '{}', 'Super compressed gold', '', '{"enchanted_gold": 160}', 204800, '{}', 409600),
('enchanted_diamond_block', 'Enchanted Diamond Block', 'EPIC', 'MATERIAL', '{}', 'Super compressed diamonds', '', '{"enchanted_diamond": 160}', 1280000, '{}', 2560000),

-- Special Materials
('ender_pearl', 'Ender Pearl', 'UNCOMMON', 'MATERIAL', '{}', 'Dropped by Endermen', '', '{}', 10, '{}', 20),
('enchanted_ender_pearl', 'Enchanted Ender Pearl', 'RARE', 'MATERIAL', '{}', 'Compressed ender pearls', '', '{"ender_pearl": 160}', 1600, '{}', 3200),
('enchanted_eye_of_ender', 'Enchanted Eye of Ender', 'RARE', 'MATERIAL', '{}', 'A mystical eye', '', '{"enchanted_ender_pearl": 16, "blaze_powder": 16}', 25600, '{}', 51200),
('blaze_rod', 'Blaze Rod', 'UNCOMMON', 'MATERIAL', '{}', 'Dropped by Blazes', '', '{}', 20, '{}', 40),
('blaze_powder', 'Blaze Powder', 'UNCOMMON', 'MATERIAL', '{}', 'Ground blaze rod', '', '{"blaze_rod": 1}', 10, '{}', 20),
('enchanted_blaze_rod', 'Enchanted Blaze Rod', 'RARE', 'MATERIAL', '{}', 'Compressed blaze rods', '', '{"blaze_rod": 160}', 3200, '{}', 6400),
('nether_star', 'Nether Star', 'LEGENDARY', 'MATERIAL', '{}', 'Dropped by Withers', '', '{}', 50000, '{}', 100000),
('dragon_scale', 'Dragon Scale', 'EPIC', 'MATERIAL', '{}', 'Scale from a dragon', '', '{}', 10000, '{}', 20000),
('titanium', 'Titanium', 'RARE', 'MATERIAL', '{}', 'Rare ore from Deep Caverns', '', '{}', 1000, '{}', 2000),
('mithril', 'Mithril', 'RARE', 'MATERIAL', '{}', 'Magical ore', '', '{}', 800, '{}', 1600),
('obsidian', 'Obsidian', 'UNCOMMON', 'MATERIAL', '{}', 'Hardened lava', '', '{}', 25, '{}', 50),
('enchanted_obsidian', 'Enchanted Obsidian', 'RARE', 'MATERIAL', '{}', 'Compressed obsidian', '', '{"obsidian": 160}', 4000, '{}', 8000),
('refined_mithril', 'Refined Mithril', 'EPIC', 'MATERIAL', '{}', 'Purified mithril', '', '{"mithril": 16, "enchanted_coal": 8}', 16000, '{}', 32000),
('refined_titanium', 'Refined Titanium', 'EPIC', 'MATERIAL', '{}', 'Purified titanium', '', '{"titanium": 16, "enchanted_iron": 8}', 20000, '{}', 40000);

-- ============================================
-- NEW SWORDS (15+)
-- ============================================

INSERT OR IGNORE INTO game_items (item_id, name, rarity, item_type, stats, lore, special_ability, craft_recipe, npc_sell_price, collection_req, default_bazaar_price)
VALUES
-- Early Game Swords
('undead_sword', 'Undead Sword', 'COMMON', 'SWORD', '{"damage": 50, "strength": 10}', 'Deals extra damage to undead', 'Undead Slayer: +50% damage vs undead', '{"enchanted_bone": 8, "stick": 1}', 100, '{}', 200),
('ender_sword', 'Ender Sword', 'RARE', 'SWORD', '{"damage": 80, "strength": 20}', 'Infused with End energy', 'End Stone Sharpness: +15 damage', '{"enchanted_ender_pearl": 32, "stick": 1}', 500, '{}', 1000),
('prismarine_blade', 'Prismarine Blade', 'UNCOMMON', 'SWORD', '{"damage": 65, "strength": 15}', 'Forged from ocean materials', 'Aquatic Affinity: +10% damage in water', '{"prismarine_shard": 64, "stick": 1}', 300, '{}', 600),
('flaming_sword', 'Flaming Sword', 'UNCOMMON', 'SWORD', '{"damage": 70, "strength": 12}', 'Burns enemies on hit', 'Ignite: Sets enemies on fire', '{"enchanted_blaze_rod": 16, "diamond_sword": 1}', 800, '{}', 1600),
('emerald_blade', 'Emerald Blade', 'RARE', 'SWORD', '{"damage": 100, "strength": 30}', 'A blade for the wealthy', 'Merchant''s Fortune: +10 coins per kill', '{"enchanted_emerald": 32, "stick": 1}', 1500, '{}', 3000),

-- Mid Game Swords
('spider_sword', 'Spider Sword', 'UNCOMMON', 'SWORD', '{"damage": 60, "strength": 10}', 'Crafted from spider parts', 'Web Shot: Slows enemies', '{"enchanted_string": 32, "stick": 1}', 250, '{}', 500),
('thick_scorpion_foil', 'Thick Scorpion Foil', 'EPIC', 'SWORD', '{"damage": 120, "strength": 50, "crit_damage": 25}', 'Scorpion venom coats the blade', 'Venom Strike: Poisons enemies', '{"scorpion_foil": 1, "enchanted_iron_block": 8}', 5000, '{}', 10000),
('thick_aspect_of_the_end', 'Thick Aspect of the End', 'EPIC', 'SWORD', '{"damage": 140, "strength": 120}', 'Enhanced teleportation sword', 'Instant Transmission: Teleport 12 blocks', '{"aspect_of_the_end": 1, "enchanted_ender_pearl": 64}', 10000, '{}', 20000),
('scorpion_foil', 'Scorpion Foil', 'RARE', 'SWORD', '{"damage": 90, "strength": 30, "crit_damage": 15}', 'Swift and deadly', 'Quick Strike: +20% attack speed', '{"enchanted_string": 64, "stick": 1, "spider_eye": 32}', 2500, '{}', 5000),
('ornate_zombie_sword', 'Ornate Zombie Sword', 'RARE', 'SWORD', '{"damage": 110, "strength": 40}', 'Upgraded zombie sword', 'Undead Army: Summon zombie minions', '{"zombie_sword": 1, "enchanted_rotten_flesh": 64}', 3000, '{}', 6000),

-- Late Game Swords
('fabled_sword', 'Fabled Sword', 'LEGENDARY', 'SWORD', '{"damage": 200, "strength": 80, "crit_damage": 50}', 'A sword of legends', 'Legendary Strike: Massive critical hits', '{"enchanted_diamond_block": 32, "nether_star": 1}', 100000, '{}', 200000),
('void_sword', 'Void Sword', 'EPIC', 'SWORD', '{"damage": 150, "strength": 60, "crit_chance": 15}', 'Forged in the void', 'Void Strike: Ignores 25% defense', '{"enchanted_obsidian": 32, "enchanted_eye_of_ender": 16}', 25000, '{}', 50000),
('crimson_blade', 'Crimson Blade', 'EPIC', 'SWORD', '{"damage": 135, "strength": 55}', 'Burns with eternal flame', 'Crimson Slash: Fire damage over time', '{"enchanted_blaze_rod": 64, "enchanted_gold_block": 16}', 20000, '{}', 40000),
('aurora_sword', 'Aurora Sword', 'LEGENDARY', 'SWORD', '{"damage": 180, "strength": 75, "intelligence": 50}', 'Channels aurora energy', 'Aurora Beam: Shoots energy beam', '{"enchanted_diamond_block": 16, "enchanted_lapis_block": 32, "nether_star": 1}', 80000, '{}', 160000),
('tacticians_sword', 'Tactician''s Sword', 'EPIC', 'SWORD', '{"damage": 125, "strength": 45, "intelligence": 100}', 'For the strategic warrior', 'Battle Plan: +15% damage per ally nearby', '{"enchanted_iron_block": 32, "enchanted_diamond": 64}', 15000, '{}', 30000),

-- Endgame Swords
('glacial_scythe', 'Glacial Scythe', 'LEGENDARY', 'SWORD', '{"damage": 220, "strength": 100, "crit_damage": 75}', 'Freezes all it touches', 'Absolute Zero: Freezes enemies solid', '{"frozen_scythe": 1, "enchanted_ice": 64, "enchanted_diamond_block": 32}', 150000, '{}', 300000),
('voidwalker_katana', 'Voidwalker Katana', 'LEGENDARY', 'SWORD', '{"damage": 210, "strength": 90, "crit_chance": 20, "attack_speed": 15}', 'Walk between dimensions', 'Dimensional Slash: Attack all nearby enemies', '{"void_sword": 1, "enchanted_ender_pearl": 128, "nether_star": 2}', 175000, '{}', 350000),
('molten_edge', 'Molten Edge', 'LEGENDARY', 'SWORD', '{"damage": 195, "strength": 85, "ferocity": 25}', 'Forged in dragon fire', 'Molten Strike: Multiple hits per attack', '{"crimson_blade": 1, "dragon_scale": 16, "enchanted_blaze_rod": 128}', 120000, '{}', 240000),
('dark_claymore', 'Dark Claymore', 'MYTHIC', 'SWORD', '{"damage": 300, "strength": 150, "crit_damage": 100}', 'The ultimate dark weapon', 'Dark Devastation: Massive AoE attack', '{"fabled_sword": 1, "necron_blade": 1, "wither_catalyst": 64}', 500000, '{}', 1000000);

-- Add weapon stats for all new swords
INSERT OR IGNORE INTO weapon_stats (item_id, damage, strength, crit_chance, crit_damage, attack_speed, ability_damage, ferocity, bonus_attack_speed)
VALUES
('undead_sword', 50, 10, 0, 0, 0, 0, 0, 0),
('ender_sword', 80, 20, 0, 0, 0, 0, 0, 0),
('prismarine_blade', 65, 15, 0, 0, 0, 0, 0, 0),
('flaming_sword', 70, 12, 0, 0, 0, 0, 0, 0),
('emerald_blade', 100, 30, 0, 0, 0, 0, 0, 0),
('spider_sword', 60, 10, 0, 0, 0, 0, 0, 0),
('thick_scorpion_foil', 120, 50, 0, 25, 0, 0, 0, 0),
('thick_aspect_of_the_end', 140, 120, 0, 0, 0, 0, 0, 0),
('scorpion_foil', 90, 30, 0, 15, 0, 0, 0, 0),
('ornate_zombie_sword', 110, 40, 0, 0, 0, 0, 0, 0),
('fabled_sword', 200, 80, 0, 50, 0, 0, 0, 0),
('void_sword', 150, 60, 15, 0, 0, 0, 0, 0),
('crimson_blade', 135, 55, 0, 0, 0, 0, 0, 0),
('aurora_sword', 180, 75, 0, 0, 0, 100, 0, 0),
('tacticians_sword', 125, 45, 0, 0, 0, 0, 0, 0),
('glacial_scythe', 220, 100, 0, 75, 0, 0, 0, 0),
('voidwalker_katana', 210, 90, 20, 0, 15, 0, 0, 0.15),
('molten_edge', 195, 85, 0, 0, 0, 0, 25, 0),
('dark_claymore', 300, 150, 0, 100, 0, 0, 0, 0);

-- ============================================
-- ADDITIONAL SPECIAL MATERIALS FOR RECIPES
-- ============================================

INSERT OR IGNORE INTO game_items (item_id, name, rarity, item_type, stats, lore, special_ability, craft_recipe, npc_sell_price, collection_req, default_bazaar_price)
VALUES
('prismarine_shard', 'Prismarine Shard', 'UNCOMMON', 'MATERIAL', '{}', 'Ocean crystal fragment', '', '{}', 15, '{}', 30),
('spider_eye', 'Spider Eye', 'COMMON', 'MATERIAL', '{}', 'Dropped by spiders', '', '{}', 3, '{}', 6),
('rotten_flesh', 'Rotten Flesh', 'COMMON', 'MATERIAL', '{}', 'Zombie meat', '', '{}', 2, '{}', 4),
('enchanted_rotten_flesh', 'Enchanted Rotten Flesh', 'UNCOMMON', 'MATERIAL', '{}', 'Compressed rotten flesh', '', '{"rotten_flesh": 160}', 320, '{}', 640),
('enchanted_coal', 'Enchanted Coal', 'UNCOMMON', 'MATERIAL', '{}', 'Compressed coal', '', '{"coal": 160}', 160, '{}', 320),
('coal', 'Coal', 'COMMON', 'MATERIAL', '{}', 'Fuel and crafting material', '', '{}', 1, '{}', 2),
('enchanted_lapis_block', 'Enchanted Lapis Block', 'RARE', 'MATERIAL', '{}', 'Super compressed lapis', '', '{"enchanted_lapis": 160}', 32000, '{}', 64000),
('enchanted_lapis', 'Enchanted Lapis', 'UNCOMMON', 'MATERIAL', '{}', 'Compressed lapis lazuli', '', '{"lapis_lazuli": 160}', 200, '{}', 400),
('lapis_lazuli', 'Lapis Lazuli', 'COMMON', 'MATERIAL', '{}', 'Blue dye material', '', '{}', 1, '{}', 2),
('enchanted_ice', 'Enchanted Ice', 'RARE', 'MATERIAL', '{}', 'Never melts', '', '{"ice": 160}', 800, '{}', 1600),
('ice', 'Ice', 'COMMON', 'MATERIAL', '{}', 'Frozen water', '', '{}', 5, '{}', 10),
('wither_catalyst', 'Wither Catalyst', 'LEGENDARY', 'MATERIAL', '{}', 'Summons a Wither boss', '', '{"nether_star": 4, "enchanted_bone": 64}', 250000, '{}', 500000);

-- ============================================
-- ARMOR SETS (Early, Mid, Late Game)
-- ============================================

-- Hardened Diamond Set
INSERT OR IGNORE INTO game_items (item_id, name, rarity, item_type, stats, lore, special_ability, craft_recipe, npc_sell_price, collection_req, default_bazaar_price)
VALUES
('hardened_diamond_chestplate', 'Hardened Diamond Chestplate', 'RARE', 'CHESTPLATE', '{"defense": 80, "health": 60}', 'Reinforced diamond armor', '', '{"diamond": 24}', 1200, '{}', 2400),
('hardened_diamond_leggings', 'Hardened Diamond Leggings', 'RARE', 'LEGGINGS', '{"defense": 60, "health": 50}', 'Reinforced diamond armor', '', '{"diamond": 21}', 1050, '{}', 2100),
('hardened_diamond_boots', 'Hardened Diamond Boots', 'RARE', 'BOOTS', '{"defense": 40, "health": 30}', 'Reinforced diamond armor', '', '{"diamond": 12}', 600, '{}', 1200);

INSERT OR IGNORE INTO armor_stats (item_id, defense, health, strength, crit_chance, crit_damage, intelligence, speed, magic_find, pet_luck, true_defense)
VALUES
('hardened_diamond_helmet', 50, 40, 0, 0, 0, 0, 0, 0, 0, 0),
('hardened_diamond_chestplate', 80, 60, 0, 0, 0, 0, 0, 0, 0, 0),
('hardened_diamond_leggings', 60, 50, 0, 0, 0, 0, 0, 0, 0, 0),
('hardened_diamond_boots', 40, 30, 0, 0, 0, 0, 0, 0, 0, 0);

-- Ender Armor Set
INSERT OR IGNORE INTO game_items (item_id, name, rarity, item_type, stats, lore, special_ability, craft_recipe, npc_sell_price, collection_req, default_bazaar_price)
VALUES
('ender_helmet', 'Ender Helmet', 'EPIC', 'HELMET', '{"defense": 80, "health": 100, "intelligence": 100}', 'Infused with End magic', 'Full Set Bonus: Teleport on hit', '{"enchanted_ender_pearl": 64, "enchanted_eye_of_ender": 8}', 25000, '{}', 50000),
('ender_chestplate', 'Ender Chestplate', 'EPIC', 'CHESTPLATE', '{"defense": 120, "health": 150, "intelligence": 150}', 'Infused with End magic', '', '{"enchanted_ender_pearl": 128, "enchanted_eye_of_ender": 16}', 50000, '{}', 100000),
('ender_leggings', 'Ender Leggings', 'EPIC', 'LEGGINGS', '{"defense": 100, "health": 125, "intelligence": 125}', 'Infused with End magic', '', '{"enchanted_ender_pearl": 96, "enchanted_eye_of_ender": 12}', 37500, '{}', 75000),
('ender_boots', 'Ender Boots', 'EPIC', 'BOOTS', '{"defense": 70, "health": 80, "intelligence": 80, "speed": 10}', 'Infused with End magic', '', '{"enchanted_ender_pearl": 64, "enchanted_eye_of_ender": 8}', 25000, '{}', 50000);

INSERT OR IGNORE INTO armor_stats (item_id, defense, health, strength, crit_chance, crit_damage, intelligence, speed, magic_find, pet_luck, true_defense)
VALUES
('ender_helmet', 80, 100, 0, 0, 0, 100, 0, 0, 0, 0),
('ender_chestplate', 120, 150, 0, 0, 0, 150, 0, 0, 0, 0),
('ender_leggings', 100, 125, 0, 0, 0, 125, 0, 0, 0, 0),
('ender_boots', 70, 80, 0, 0, 0, 80, 10, 0, 0, 0);

-- Miner Armor Set
INSERT OR IGNORE INTO game_items (item_id, name, rarity, item_type, stats, lore, special_ability, craft_recipe, npc_sell_price, collection_req, default_bazaar_price)
VALUES
('miner_helmet', 'Miner Helmet', 'RARE', 'HELMET', '{"defense": 30, "mining_speed": 50}', 'Built for mining', 'Haste I Effect', '{"enchanted_iron": 16, "enchanted_coal": 8}', 5000, '{}', 10000),
('miner_chestplate', 'Miner Chestplate', 'RARE', 'CHESTPLATE', '{"defense": 50, "mining_speed": 75}', 'Built for mining', '', '{"enchanted_iron": 32, "enchanted_coal": 16}', 10000, '{}', 20000),
('miner_leggings', 'Miner Leggings', 'RARE', 'LEGGINGS', '{"defense": 40, "mining_speed": 60}', 'Built for mining', '', '{"enchanted_iron": 24, "enchanted_coal": 12}', 7500, '{}', 15000),
('miner_boots', 'Miner Boots', 'RARE', 'BOOTS', '{"defense": 25, "mining_speed": 40}', 'Built for mining', '', '{"enchanted_iron": 16, "enchanted_coal": 8}', 5000, '{}', 10000);

INSERT OR IGNORE INTO armor_stats (item_id, defense, health, strength, crit_chance, crit_damage, intelligence, speed, magic_find, pet_luck, true_defense)
VALUES
('miner_helmet', 30, 0, 0, 0, 0, 0, 0, 0, 0, 0),
('miner_chestplate', 50, 0, 0, 0, 0, 0, 0, 0, 0, 0),
('miner_leggings', 40, 0, 0, 0, 0, 0, 0, 0, 0, 0),
('miner_boots', 25, 0, 0, 0, 0, 0, 0, 0, 0, 0);

-- ============================================
-- ADVANCED TOOLS
-- ============================================

INSERT OR IGNORE INTO game_items (item_id, name, rarity, item_type, stats, lore, special_ability, craft_recipe, npc_sell_price, collection_req, default_bazaar_price)
VALUES
-- Pickaxes
('mithril_pickaxe', 'Mithril Pickaxe', 'EPIC', 'PICKAXE', '{"mining_speed": 100, "mining_fortune": 50, "breaking_power": 5}', 'Mines mithril efficiently', '', '{"refined_mithril": 4, "enchanted_diamond": 32}', 50000, '{}', 100000),
('titanium_pickaxe', 'Titanium Pickaxe', 'EPIC', 'PICKAXE', '{"mining_speed": 120, "mining_fortune": 60, "breaking_power": 6}', 'Powerful mining tool', '', '{"refined_titanium": 4, "enchanted_diamond": 32}', 75000, '{}', 150000),
('drill', 'Drill', 'LEGENDARY', 'PICKAXE', '{"mining_speed": 200, "mining_fortune": 100, "breaking_power": 8}', 'High-tech mining device', 'Drill Fuel: Uses fuel cells', '{"titanium_pickaxe": 1, "enchanted_iron_block": 32, "enchanted_redstone_block": 16}', 500000, '{}', 1000000),

-- Axes
('jungle_axe', 'Jungle Axe', 'RARE', 'AXE', '{"foraging_fortune": 50}', 'Breaks entire trees', 'Forester: Breaks entire trees', '{"enchanted_oak_wood": 64, "diamond_axe": 1}', 15000, '{}', 30000),
('treecapitator', 'Treecapitator', 'EPIC', 'AXE', '{"foraging_fortune": 100, "foraging_speed": 50}', 'Ultimate tree destroyer', 'Full Tree Break: Instantly breaks whole tree', '{"jungle_axe": 1, "enchanted_oak_wood": 128, "enchanted_diamond": 32}', 100000, '{}', 200000),

-- Hoes
('blessed_hoe', 'Blessed Hoe', 'RARE', 'HOE', '{"farming_fortune": 75, "farming_speed": 40}', 'Blessed by nature spirits', '', '{"enchanted_wheat": 64, "diamond_hoe": 1}', 20000, '{}', 40000),
('mathematical_hoe', 'Mathematical Hoe', 'EPIC', 'HOE', '{"farming_fortune": 150, "farming_speed": 75}', 'Calculated perfection', 'Precision Farming: +25% crop yield', '{"blessed_hoe": 1, "enchanted_emerald": 64, "enchanted_diamond": 32}', 150000, '{}', 300000),

-- Fishing Rods
('prismarine_rod', 'Prismarine Rod', 'RARE', 'FISHING_ROD', '{"fishing_speed": 40, "sea_creature_chance": 5}', 'Catches ocean creatures', '', '{"prismarine_shard": 128, "diamond_fishing_rod": 1}', 25000, '{}', 50000),
('rod_of_champions', 'Rod of Champions', 'LEGENDARY', 'FISHING_ROD', '{"fishing_speed": 100, "sea_creature_chance": 15}', 'The ultimate fishing rod', 'Champion''s Luck: Double loot chance', '{"prismarine_rod": 1, "enchanted_diamond": 64, "nether_star": 1}', 500000, '{}', 1000000);

INSERT OR IGNORE INTO tool_stats (item_id, tool_type, damage, breaking_power, mining_speed, mining_fortune, farming_fortune, foraging_fortune, fishing_speed, sea_creature_chance, crop_yield_multiplier, wood_yield_multiplier, ore_yield_multiplier, durability)
VALUES
('mithril_pickaxe', 'pickaxe', 0, 5, 100, 50, 0, 0, 0, 0, 1.0, 1.0, 1.0, 1000),
('titanium_pickaxe', 'pickaxe', 0, 6, 120, 60, 0, 0, 0, 0, 1.0, 1.0, 1.0, 1500),
('drill', 'pickaxe', 0, 8, 200, 100, 0, 0, 0, 0, 1.0, 1.0, 1.25, 5000),
('jungle_axe', 'axe', 0, 0, 0, 0, 0, 50, 0, 0, 1.0, 1.0, 1.0, 800),
('treecapitator', 'axe', 0, 0, 50, 0, 0, 100, 0, 0, 1.0, 1.5, 1.0, 2000),
('blessed_hoe', 'hoe', 0, 0, 0, 0, 75, 0, 0, 0, 1.25, 1.0, 1.0, 1000),
('mathematical_hoe', 'hoe', 0, 0, 0, 0, 150, 0, 0, 0, 1.5, 1.0, 1.0, 3000),
('prismarine_rod', 'fishing_rod', 0, 0, 0, 0, 0, 0, 40, 5, 1.0, 1.0, 1.0, 800),
('rod_of_champions', 'fishing_rod', 0, 0, 0, 0, 0, 0, 100, 15, 1.0, 1.0, 1.0, 5000);

-- ============================================
-- ADDITIONAL MATERIALS FOR NEW RECIPES
-- ============================================

INSERT OR IGNORE INTO game_items (item_id, name, rarity, item_type, stats, lore, special_ability, craft_recipe, npc_sell_price, collection_req, default_bazaar_price)
VALUES
('enchanted_wheat', 'Enchanted Wheat', 'UNCOMMON', 'MATERIAL', '{}', 'Compressed wheat', '', '{"wheat": 160}', 160, '{}', 320),
('wheat', 'Wheat', 'COMMON', 'MATERIAL', '{}', 'Farm crop', '', '{}', 1, '{}', 2),
('enchanted_redstone_block', 'Enchanted Redstone Block', 'RARE', 'MATERIAL', '{}', 'Super compressed redstone', '', '{"enchanted_redstone": 160}', 32000, '{}', 64000),
('enchanted_redstone', 'Enchanted Redstone', 'UNCOMMON', 'MATERIAL', '{}', 'Compressed redstone', '', '{"redstone": 160}', 200, '{}', 400),
('redstone', 'Redstone', 'COMMON', 'MATERIAL', '{}', 'Electrical component', '', '{}', 1, '{}', 2);

-- ============================================
-- CRAFTING RECIPES TABLE
-- (If it exists, populate it with all the recipes)
-- ============================================

-- Note: Many items have craft_recipe in their JSON field above
-- If you have a separate crafting_recipes table, uncomment and use this:

/*
INSERT OR IGNORE INTO crafting_recipes (recipe_id, output_item, ingredients, output_amount)
VALUES
-- Basic Tools
('wooden_sword', 'wooden_sword', '{"stick": 1, "oak_wood": 2}', 1),
('stone_sword', 'stone_sword', '{"stick": 1, "cobblestone": 2}', 1),
('iron_sword', 'iron_sword', '{"stick": 1, "iron_ingot": 2}', 1),
('diamond_sword', 'diamond_sword', '{"stick": 1, "diamond": 2}', 1),

-- Enchanted Materials
('enchanted_iron', 'enchanted_iron', '{"iron_ingot": 160}', 1),
('enchanted_gold', 'enchanted_gold', '{"gold_ingot": 160}', 1),
('enchanted_diamond', 'enchanted_diamond', '{"diamond": 160}', 1),

-- New Swords
('undead_sword', 'undead_sword', '{"enchanted_bone": 8, "stick": 1}', 1),
('ender_sword', 'ender_sword', '{"enchanted_ender_pearl": 32, "stick": 1}', 1),
('emerald_blade', 'emerald_blade', '{"enchanted_emerald": 32, "stick": 1}', 1),
('fabled_sword', 'fabled_sword', '{"enchanted_diamond_block": 32, "nether_star": 1}', 1),
('void_sword', 'void_sword', '{"enchanted_obsidian": 32, "enchanted_eye_of_ender": 16}', 1),
('dark_claymore', 'dark_claymore', '{"fabled_sword": 1, "necron_blade": 1, "wither_catalyst": 64}', 1);
*/
