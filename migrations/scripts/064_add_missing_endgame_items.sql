-- Insert items into game_items (using 'lore' column as TEXT, not JSON)
INSERT OR IGNORE INTO game_items (item_id, name, rarity, item_type, lore) VALUES
('lumberjack_axe', 'Lumberjack Axe', 'LEGENDARY', 'AXE', '["The ultimate woodcutting tool"]'),
('soul_eater_bow', 'Soul Eater Bow', 'MYTHIC', 'BOW', '["Devours enemy souls"]'),
('wooden_drill', 'Wooden Drill', 'COMMON', 'DRILL', '["A basic drill"]'),
('refined_mithril_drill', 'Refined Mithril Drill', 'LEGENDARY', 'DRILL', '["A refined mithril drill"]'),
('gemstone_drill', 'Gemstone Drill', 'MYTHIC', 'DRILL', '["Drills through gemstones"]'),
('farmers_delight', 'Farmers Delight', 'LEGENDARY', 'HOE', '["Pure farming excellence"]'),
('rod_of_legends', 'Rod of Legends', 'LEGENDARY', 'FISHING_ROD', '["Legendary fishing power"]'),
('divan_pickaxe', 'Divan Pickaxe', 'MYTHIC', 'PICKAXE', '["The ultimate mining tool"]');

-- Insert weapon stats for weapons (based on titanium pickaxe baseline: end-game = 2-5x late game)
INSERT OR REPLACE INTO weapon_stats (item_id, damage, strength, crit_chance, crit_damage, attack_speed, ferocity) VALUES
('lumberjack_axe', 400, 150, 15, 50, 0, 10),
('soul_eater_bow', 1200, 400, 50, 150, 60, 30);

-- Insert into tool_stats (for tools like DRILL, PICKAXE, HOE, FISHING_ROD)
-- Based on Titanium Pickaxe baseline: 200 speed, 200 fortune (Late Game)
-- End Game = 2-5x Late Game stats
INSERT OR REPLACE INTO tool_stats (item_id, tool_type, mining_speed, mining_fortune, breaking_power, farming_fortune, foraging_fortune, fishing_speed, sea_creature_chance) VALUES
('lumberjack_axe', 'axe', 0, 0, 0, 0, 600, 0, 0),
('wooden_drill', 'drill', 50, 40, 2, 0, 0, 0, 0),
('refined_mithril_drill', 'drill', 600, 600, 8, 0, 0, 0, 0),
('gemstone_drill', 'drill', 800, 800, 9, 0, 0, 0, 0),
('farmers_delight', 'hoe', 0, 0, 0, 800, 0, 0, 0),
('rod_of_legends', 'fishing_rod', 0, 0, 0, 0, 0, 600, 60),
('divan_pickaxe', 'pickaxe', 1000, 1000, 10, 0, 0, 0, 0);

-- Insert into crafting_recipes (using 'recipe_id' and 'ingredients', not 'item_id' and 'recipe')
INSERT OR IGNORE INTO crafting_recipes (recipe_id, output_item, ingredients, output_amount) VALUES
('lumberjack_axe_recipe', 'lumberjack_axe', '{"enchanted_wood_block": 64, "enchanted_diamond_block": 16, "treecapitator": 1}', 1),
('soul_eater_bow_recipe', 'soul_eater_bow', '{"wither_essence": 256, "undead_essence": 256, "last_breath": 1}', 1),
('wooden_drill_recipe', 'wooden_drill', '{"wood": 256, "enchanted_iron": 8}', 1),
('refined_mithril_drill_recipe', 'refined_mithril_drill', '{"refined_mithril": 256, "enchanted_redstone_block": 128, "mithril_drill": 1}', 1),
('gemstone_drill_recipe', 'gemstone_drill', '{"refined_mithril": 512, "perfect_gemstone": 32, "refined_mithril_drill": 1}', 1),
('farmers_delight_recipe', 'farmers_delight', '{"enchanted_melon_block": 64, "enchanted_pumpkin": 64, "mathematical_hoe": 1}', 1),
('rod_of_legends_recipe', 'rod_of_legends', '{"enchanted_sponge": 256, "enchanted_prismarine_block": 64, "rod_of_champions": 1}', 1),
('divan_pickaxe_recipe', 'divan_pickaxe', '{"refined_mithril": 256, "enchanted_diamond_block": 64, "mithril_pickaxe": 1}', 1);

INSERT OR IGNORE INTO weapon_abilities (item_id, ability_name, mana_cost, cooldown, base_damage_multiplier, strength_scaling, description) VALUES
('lumberjack_axe', 'Timber Strike', 80, 2.5, 12.0, 0.02, 'Strike with the force of a lumberjack'),
('soul_eater_bow', 'Devour', 150, 2.5, 15.0, 0.02, 'Devour enemy souls for massive damage');

UPDATE weapon_abilities SET aoe_radius = 10 WHERE item_id = 'lumberjack_axe';
UPDATE weapon_abilities SET lifesteal_percent = 40 WHERE item_id = 'soul_eater_bow';
