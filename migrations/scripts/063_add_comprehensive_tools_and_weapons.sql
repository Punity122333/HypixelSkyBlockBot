-- Fixed version of migration 063
-- Adds comprehensive tools and weapons

-- Insert items into game_items (using 'lore' column, not 'description')
INSERT OR IGNORE INTO game_items (item_id, name, rarity, item_type, lore) VALUES
('treecapitator', 'Treecapitator', 'EPIC', 'AXE', '["Instantly mines entire trees"]'),
('jungle_axe', 'Jungle Axe', 'RARE', 'AXE', '["Chop logs in a 3x3 area"]'),
('wooden_axe', 'Wooden Axe', 'COMMON', 'AXE', '["A basic wooden axe"]'),
('stone_axe', 'Stone Axe', 'COMMON', 'AXE', '["A stone axe for chopping"]'),
('iron_axe', 'Iron Axe', 'UNCOMMON', 'AXE', '["An iron axe"]'),
('golden_axe', 'Golden Axe', 'RARE', 'AXE', '["A golden axe"]'),
('diamond_axe', 'Diamond Axe', 'EPIC', 'AXE', '["A powerful diamond axe"]'),
('efficiency_axe', 'Efficiency Axe', 'UNCOMMON', 'AXE', '["Cuts wood faster"]'),
('farming_hoe', 'Farming Hoe', 'COMMON', 'HOE', '["Basic farming tool"]'),
('blessed_hoe', 'Blessed Hoe', 'UNCOMMON', 'HOE', '["Increases crop yields"]'),
('mathematical_hoe', 'Mathematical Hoe Blueprint', 'LEGENDARY', 'HOE', '["The ultimate farming tool", "The pinnacle of farming technology"]'),
('newton_hoe', 'Newton Hoe', 'EPIC', 'HOE', '["Advanced farming efficiency", "Harness the power of gravity"]'),
('pythagorean_hoe', 'Pythagorean Hoe', 'EPIC', 'HOE', '["Mathematical farming power"]'),
('rookie_hoe', 'Rookie Hoe', 'COMMON', 'HOE', '["A starter hoe for farming"]'),
('decent_hoe', 'Decent Hoe', 'UNCOMMON', 'HOE', '["Better than rookie"]'),
('advanced_hoe', 'Advanced Hoe', 'RARE', 'HOE', '["Advanced farming capabilities"]'),
('rookie_pickaxe', 'Rookie Pickaxe', 'COMMON', 'PICKAXE', '["A basic mining tool"]'),
('promising_pickaxe', 'Promising Pickaxe', 'UNCOMMON', 'PICKAXE', '["Shows promise"]'),
('iron_pickaxe', 'Iron Pickaxe', 'UNCOMMON', 'PICKAXE', '["Standard iron pickaxe"]'),
('golden_pickaxe', 'Golden Pickaxe', 'RARE', 'PICKAXE', '["Fast but fragile"]'),
('diamond_pickaxe', 'Diamond Pickaxe', 'EPIC', 'PICKAXE', '["Very durable pickaxe"]'),
('mithril_pickaxe', 'Mithril Pickaxe', 'RARE', 'PICKAXE', '["Mines mithril efficiently"]'),
('titanium_pickaxe', 'Titanium Pickaxe', 'EPIC', 'PICKAXE', '["Strong and durable"]'),
('gemstone_gauntlet', 'Gemstone Gauntlet', 'LEGENDARY', 'PICKAXE', '["Mine gemstones effectively", "Mine gemstones with perfect precision"]'),
('ruby_drill', 'Ruby Drill', 'RARE', 'DRILL', '["Powerful mining drill"]'),
('sapphire_drill', 'Sapphire Drill', 'RARE', 'DRILL', '["Advanced drill technology"]'),
('amber_drill', 'Amber Drill', 'RARE', 'DRILL', '["Efficient mining"]'),
('topaz_drill', 'Topaz Drill', 'RARE', 'DRILL', '["Fast mining speed"]'),
('jasper_drill', 'Jasper Drill', 'RARE', 'DRILL', '["Heavy-duty drilling"]'),
('amethyst_drill', 'Amethyst Drill', 'EPIC', 'DRILL', '["Magical drilling power"]'),
('x655_drill', 'X-655 Drill', 'EPIC', 'DRILL', '["Industrial grade drill"]'),
('x855_drill', 'X-855 Drill', 'LEGENDARY', 'DRILL', '["Advanced industrial drill"]'),
('divan_drill', 'Divan Drill', 'MYTHIC', 'DRILL', '["The ultimate mining tool", "The most powerful drill ever created"]'),
('prismarine_rod', 'Prismarine Rod', 'COMMON', 'FISHING_ROD', '["Basic fishing rod"]'),
('sponge_rod', 'Sponge Rod', 'UNCOMMON', 'FISHING_ROD', '["Absorbs water magic"]'),
('challenging_rod', 'Challenging Rod', 'RARE', 'FISHING_ROD', '["For experienced fishers"]'),
('rod_of_champions', 'Rod of Champions', 'EPIC', 'FISHING_ROD', '["Elite fishing tool"]'),
('shredder', 'Shredder', 'EPIC', 'FISHING_ROD', '["Shreds through water"]'),
('hellfire_rod', 'Hellfire Rod', 'LEGENDARY', 'FISHING_ROD', '["Fish in lava", "Fish in the depths of the nether"]'),
('auger_rod', 'Auger Rod', 'LEGENDARY', 'FISHING_ROD', '["Drills through fishing spots", "Drill through the ocean floor"]'),
('hurricane_bow', 'Hurricane Bow', 'EPIC', 'BOW', '["Summons storm arrows", "Summon the fury of the storm"]'),
('runaans_bow', 'Runaans Bow', 'LEGENDARY', 'BOW', '["Shoots 3 arrows", "Three arrows, three times the destruction"]'),
('explosive_bow', 'Explosive Bow', 'RARE', 'BOW', '["Arrows explode on impact", "Why aim when you can just explode?"]'),
('magma_bow', 'Magma Bow', 'EPIC', 'BOW', '["Sets enemies ablaze"]'),
('last_breath', 'Last Breath', 'LEGENDARY', 'BOW', '["Your enemies last sight", "The last thing your enemies will see"]'),
('artisanal_shortbow', 'Artisanal Shortbow', 'RARE', 'BOW', '["Crafted with precision"]'),
('mosquito_bow', 'Mosquito Bow', 'UNCOMMON', 'BOW', '["Quick and annoying"]');

-- Insert tool stats (removing non-existent columns: farming_speed, foraging_speed)
-- Based on Titanium Pickaxe baseline: 200 mining_speed, 200 mining_fortune (Late Game tier)
-- Early: 10-30, Mid: 50-100, Late: 150-250, End: 400+
INSERT OR REPLACE INTO tool_stats (item_id, tool_type, mining_speed, mining_fortune, breaking_power, farming_fortune, foraging_fortune, fishing_speed, sea_creature_chance) VALUES
-- Axes (foraging tools)
('wooden_axe', 'AXE', 0, 0, 0, 0, 10, 0, 0),
('stone_axe', 'AXE', 0, 0, 0, 0, 20, 0, 0),
('iron_axe', 'AXE', 0, 0, 0, 0, 40, 0, 0),
('golden_axe', 'AXE', 0, 0, 0, 0, 75, 0, 0),
('diamond_axe', 'AXE', 0, 0, 0, 0, 100, 0, 0),
('efficiency_axe', 'AXE', 0, 0, 0, 0, 60, 0, 0),
('jungle_axe', 'AXE', 0, 0, 0, 0, 180, 0, 0),
('treecapitator', 'AXE', 0, 0, 0, 0, 350, 0, 0),
-- Hoes (farming tools)
('rookie_hoe', 'HOE', 0, 0, 0, 10, 0, 0, 0),
('farming_hoe', 'HOE', 0, 0, 0, 20, 0, 0, 0),
('decent_hoe', 'HOE', 0, 0, 0, 40, 0, 0, 0),
('blessed_hoe', 'HOE', 0, 0, 0, 80, 0, 0, 0),
('advanced_hoe', 'HOE', 0, 0, 0, 100, 0, 0, 0),
('newton_hoe', 'HOE', 0, 0, 0, 150, 0, 0, 0),
('pythagorean_hoe', 'HOE', 0, 0, 0, 200, 0, 0, 0),
('mathematical_hoe', 'HOE', 0, 0, 0, 400, 0, 0, 0),
-- Pickaxes (mining tools) - Titanium is baseline
('rookie_pickaxe', 'PICKAXE', 15, 10, 1, 0, 0, 0, 0),
('promising_pickaxe', 'PICKAXE', 30, 20, 2, 0, 0, 0, 0),
('iron_pickaxe', 'PICKAXE', 60, 40, 3, 0, 0, 0, 0),
('golden_pickaxe', 'PICKAXE', 100, 75, 3, 0, 0, 0, 0),
('diamond_pickaxe', 'PICKAXE', 125, 100, 4, 0, 0, 0, 0),
('mithril_pickaxe', 'PICKAXE', 175, 150, 5, 0, 0, 0, 0),
('titanium_pickaxe', 'PICKAXE', 200, 200, 6, 0, 0, 0, 0),
('gemstone_gauntlet', 'PICKAXE', 450, 500, 8, 0, 0, 0, 0),
-- Drills (advanced mining tools)
('ruby_drill', 'DRILL', 250, 250, 7, 0, 0, 0, 0),
('sapphire_drill', 'DRILL', 260, 260, 7, 0, 0, 0, 0),
('amber_drill', 'DRILL', 270, 270, 7, 0, 0, 0, 0),
('topaz_drill', 'DRILL', 280, 280, 7, 0, 0, 0, 0),
('jasper_drill', 'DRILL', 290, 290, 7, 0, 0, 0, 0),
('amethyst_drill', 'DRILL', 350, 350, 8, 0, 0, 0, 0),
('x655_drill', 'DRILL', 400, 400, 8, 0, 0, 0, 0),
('x855_drill', 'DRILL', 500, 500, 9, 0, 0, 0, 0),
('divan_drill', 'DRILL', 1000, 1000, 10, 0, 0, 0, 0),
-- Fishing Rods
('prismarine_rod', 'FISHING_ROD', 0, 0, 0, 0, 0, 20, 2),
('sponge_rod', 'FISHING_ROD', 0, 0, 0, 0, 0, 40, 4),
('challenging_rod', 'FISHING_ROD', 0, 0, 0, 0, 0, 80, 8),
('rod_of_champions', 'FISHING_ROD', 0, 0, 0, 0, 0, 150, 15),
('shredder', 'FISHING_ROD', 0, 0, 0, 0, 0, 200, 20),
('hellfire_rod', 'FISHING_ROD', 0, 0, 0, 0, 0, 350, 35),
('auger_rod', 'FISHING_ROD', 0, 0, 0, 0, 0, 400, 40),
('hurricane_bow', 'BOW', 0, 0, 0, 0, 0, 0, 0),
('runaans_bow', 'BOW', 0, 0, 0, 0, 0, 0, 0),
('explosive_bow', 'BOW', 0, 0, 0, 0, 0, 0, 0),
('magma_bow', 'BOW', 0, 0, 0, 0, 0, 0, 0),
('last_breath', 'BOW', 0, 0, 0, 0, 0, 0, 0),
('artisanal_shortbow', 'BOW', 0, 0, 0, 0, 0, 0, 0),
('mosquito_bow', 'BOW', 0, 0, 0, 0, 0, 0, 0);

-- Add weapon stats to game_items stats field
-- Based on progression: Early (50-150), Mid (200-350), Late (400-600), End (700-1000+)
UPDATE game_items SET stats = json('{"damage": 180, "strength": 60, "crit_chance": 15, "crit_damage": 40}') WHERE item_id = 'hurricane_bow';
UPDATE game_items SET stats = json('{"damage": 350, "strength": 120, "crit_chance": 30, "crit_damage": 75}') WHERE item_id = 'runaans_bow';
UPDATE game_items SET stats = json('{"damage": 150, "strength": 40, "crit_chance": 10, "crit_damage": 30}') WHERE item_id = 'explosive_bow';
UPDATE game_items SET stats = json('{"damage": 200, "strength": 70, "crit_chance": 18, "crit_damage": 50}') WHERE item_id = 'magma_bow';
UPDATE game_items SET stats = json('{"damage": 500, "strength": 180, "crit_chance": 40, "crit_damage": 100}') WHERE item_id = 'last_breath';
UPDATE game_items SET stats = json('{"damage": 120, "strength": 35, "crit_chance": 12, "crit_damage": 25}') WHERE item_id = 'artisanal_shortbow';
UPDATE game_items SET stats = json('{"damage": 80, "strength": 20, "crit_chance": 8, "crit_damage": 15}') WHERE item_id = 'mosquito_bow';

-- Insert weapon abilities
INSERT OR IGNORE INTO weapon_abilities (item_id, ability_name, mana_cost, cooldown, base_damage_multiplier, intelligence_scaling, ability_damage_scaling, aoe_radius, description) VALUES
('hurricane_bow', 'Storm Arrow', 80, 3.0, 8.0, 0.015, 0.02, 5, 'Launch a storm arrow that hits all enemies in an area'),
('runaans_bow', 'Triple Shot', 0, 0.0, 1.0, 0.0, 0.0, 0, 'Shoots 3 arrows at once'),
('explosive_bow', 'Explosive Arrow', 60, 2.5, 6.0, 0.01, 0.015, 3, 'Arrows explode on impact dealing AOE damage'),
('magma_bow', 'Magma Arrows', 50, 2.0, 5.0, 0.012, 0.015, 2, 'Sets enemies on fire dealing damage over time'),
('last_breath', 'Soul Eater', 120, 4.0, 15.0, 0.025, 0.03, 0, 'Absorb enemy souls for massive damage');

-- Update weapon abilities with special properties
UPDATE weapon_abilities SET aoe_radius = 5 WHERE item_id = 'hurricane_bow';
UPDATE weapon_abilities SET aoe_radius = 3 WHERE item_id = 'explosive_bow';

-- Insert crafting recipes (using correct schema: recipe_id, output_item, ingredients, output_amount)
INSERT OR IGNORE INTO crafting_recipes (recipe_id, output_item, ingredients, output_amount) VALUES
('wooden_axe_recipe', 'wooden_axe', '{"oak_log": 64, "stick": 32}', 1),
('stone_axe_recipe', 'stone_axe', '{"cobblestone": 128, "stick": 32}', 1),
('iron_axe_recipe', 'iron_axe', '{"iron_ingot": 32, "stick": 32}', 1),
('golden_axe_recipe', 'golden_axe', '{"gold_ingot": 48, "stick": 32}', 1),
('diamond_axe_recipe', 'diamond_axe', '{"diamond": 24, "stick": 32}', 1),
('jungle_axe_recipe', 'jungle_axe', '{"oak_log": 512, "jungle_log": 256, "stick": 64}', 1),
('efficiency_axe_recipe', 'efficiency_axe', '{"iron_axe": 1, "enchanted_iron": 16}', 1),
('treecapitator_recipe', 'treecapitator', '{"diamond_axe": 1, "enchanted_oak_log": 64, "enchanted_diamond": 32}', 1),
('farming_hoe_recipe', 'farming_hoe', '{"stick": 32, "iron_ingot": 16}', 1),
('blessed_hoe_recipe', 'blessed_hoe', '{"farming_hoe": 1, "enchanted_wheat": 32, "holy_fragment": 8}', 1),
('rookie_hoe_recipe', 'rookie_hoe', '{"stick": 16, "wooden_plank": 8}', 1),
('decent_hoe_recipe', 'decent_hoe', '{"rookie_hoe": 1, "iron_ingot": 32}', 1),
('advanced_hoe_recipe', 'advanced_hoe', '{"decent_hoe": 1, "diamond": 8, "enchanted_carrot": 16}', 1),
('newton_hoe_recipe', 'newton_hoe', '{"advanced_hoe": 1, "enchanted_melon": 64, "enchanted_pumpkin": 64}', 1),
('pythagorean_hoe_recipe', 'pythagorean_hoe', '{"newton_hoe": 1, "enchanted_potato": 128, "enchanted_hay_bale": 64}', 1),
('mathematical_hoe_recipe', 'mathematical_hoe', '{"pythagorean_hoe": 1, "enchanted_golden_carrot": 32, "enchanted_cake": 16, "mathematical_blueprint": 1}', 1),
('rookie_pickaxe_recipe', 'rookie_pickaxe', '{"stick": 32, "cobblestone": 64}', 1),
('promising_pickaxe_recipe', 'promising_pickaxe', '{"rookie_pickaxe": 1, "iron_ingot": 48}', 1),
('iron_pickaxe_recipe', 'iron_pickaxe', '{"iron_ingot": 48, "stick": 32}', 1),
('golden_pickaxe_recipe', 'golden_pickaxe', '{"gold_ingot": 80, "stick": 32}', 1),
('diamond_pickaxe_recipe', 'diamond_pickaxe', '{"diamond": 24, "stick": 32}', 1),
('mithril_pickaxe_recipe', 'mithril_pickaxe', '{"mithril": 64, "diamond_pickaxe": 1}', 1),
('titanium_pickaxe_recipe', 'titanium_pickaxe', '{"titanium": 96, "diamond_pickaxe": 1}', 1),
('gemstone_gauntlet_recipe', 'gemstone_gauntlet', '{"titanium_pickaxe": 1, "perfect_ruby": 4, "perfect_sapphire": 4, "perfect_amber": 4}', 1),
('ruby_drill_recipe', 'ruby_drill', '{"enchanted_iron": 32, "ruby": 16, "drill_engine": 1}', 1),
('sapphire_drill_recipe', 'sapphire_drill', '{"enchanted_iron": 32, "enchanted_lapis": 16, "drill_engine": 1}', 1),
('amber_drill_recipe', 'amber_drill', '{"enchanted_iron": 32, "enchanted_gold": 16, "drill_engine": 1}', 1),
('topaz_drill_recipe', 'topaz_drill', '{"enchanted_iron": 32, "enchanted_quartz": 16, "drill_engine": 1}', 1),
('jasper_drill_recipe', 'jasper_drill', '{"enchanted_iron": 32, "enchanted_redstone": 16, "drill_engine": 1}', 1),
('amethyst_drill_recipe', 'amethyst_drill', '{"ruby_drill": 1, "enchanted_diamond": 24, "advanced_drill_engine": 1}', 1),
('x655_drill_recipe', 'x655_drill', '{"amethyst_drill": 1, "titanium": 128, "advanced_drill_engine": 2}', 1),
('x855_drill_recipe', 'x855_drill', '{"x655_drill": 1, "mithril": 256, "perfect_ruby": 8, "refined_titanium": 64}', 1),
('divan_drill_recipe', 'divan_drill', '{"x855_drill": 1, "perfect_ruby": 32, "perfect_sapphire": 32, "divans_fragment": 128}', 1),
('prismarine_rod_recipe', 'prismarine_rod', '{"stick": 32, "prismarine_shard": 16}', 1),
('sponge_rod_recipe', 'sponge_rod', '{"prismarine_rod": 1, "sponge": 16, "enchanted_string": 8}', 1),
('challenging_rod_recipe', 'challenging_rod', '{"sponge_rod": 1, "enchanted_raw_fish": 32}', 1),
('rod_of_champions_recipe', 'rod_of_champions', '{"challenging_rod": 1, "enchanted_cooked_salmon": 64, "trophy_fish": 8}', 1),
('shredder_recipe', 'shredder', '{"rod_of_champions": 1, "shark_fin": 16, "enchanted_sponge": 32}', 1),
('hellfire_rod_recipe', 'hellfire_rod', '{"shredder": 1, "magma_cream": 64, "blaze_rod": 32, "enchanted_blaze_powder": 16}', 1),
('auger_rod_recipe', 'auger_rod', '{"hellfire_rod": 1, "diamond": 64, "titanium": 128, "sea_emperor_fragment": 8}', 1),
('hurricane_bow_recipe', 'hurricane_bow', '{"bow": 1, "enchanted_feather": 32, "storm_fragment": 8}', 1),
('explosive_bow_recipe', 'explosive_bow', '{"bow": 1, "tnt": 64, "gunpowder": 128}', 1),
('magma_bow_recipe', 'magma_bow', '{"bow": 1, "magma_cream": 32, "enchanted_blaze_rod": 8}', 1),
('runaans_bow_recipe', 'runaans_bow', '{"hurricane_bow": 1, "enchanted_string": 128, "enchanted_bone": 64, "enchanted_eye_of_ender": 16}', 1),
('last_breath_recipe', 'last_breath', '{"runaans_bow": 1, "wither_essence": 64, "dark_orb": 16, "soul_fragment": 32}', 1),
('artisanal_shortbow_recipe', 'artisanal_shortbow', '{"bow": 1, "enchanted_string": 16, "gold_ingot": 32}', 1),
('mosquito_bow_recipe', 'mosquito_bow', '{"bow": 1, "string": 64, "spider_eye": 32}', 1);
