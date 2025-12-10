-- ============================================
-- POPULATE CRAFTING RECIPES FROM MIGRATIONS 009 AND 011
-- This migration extracts all craft_recipe data from game_items
-- and inserts them into the crafting_recipes table
-- ============================================

-- Extract recipes from migration 009 (Basic Materials)
INSERT OR IGNORE INTO crafting_recipes (recipe_id, output_item, ingredients, output_amount)
VALUES
-- Basic Materials Tier 1
('stick_recipe', 'stick', '{"oak_wood": 2}', 1),
('enchanted_oak_wood_recipe', 'enchanted_oak_wood', '{"oak_wood": 160}', 1),
('enchanted_cobblestone_recipe', 'enchanted_cobblestone', '{"cobblestone": 160}', 1),
('enchanted_iron_recipe', 'enchanted_iron', '{"iron_ingot": 160}', 1),
('enchanted_gold_recipe', 'enchanted_gold', '{"gold_ingot": 160}', 1),
('enchanted_diamond_recipe', 'enchanted_diamond', '{"diamond": 160}', 1),
('enchanted_emerald_recipe', 'enchanted_emerald', '{"emerald": 160}', 1),
('enchanted_string_recipe', 'enchanted_string', '{"string": 160}', 1),
('enchanted_bone_recipe', 'enchanted_bone', '{"bone": 160}', 1),

-- Basic Materials Tier 2
('enchanted_iron_block_recipe', 'enchanted_iron_block', '{"enchanted_iron": 160}', 1),
('enchanted_gold_block_recipe', 'enchanted_gold_block', '{"enchanted_gold": 160}', 1),
('enchanted_diamond_block_recipe', 'enchanted_diamond_block', '{"enchanted_diamond": 160}', 1),

-- Special Materials
('blaze_powder_recipe', 'blaze_powder', '{"blaze_rod": 1}', 1),
('enchanted_ender_pearl_recipe', 'enchanted_ender_pearl', '{"ender_pearl": 160}', 1),
('enchanted_eye_of_ender_recipe', 'enchanted_eye_of_ender', '{"enchanted_ender_pearl": 16, "blaze_powder": 16}', 1),
('enchanted_blaze_rod_recipe', 'enchanted_blaze_rod', '{"blaze_rod": 160}', 1),
('enchanted_obsidian_recipe', 'enchanted_obsidian', '{"obsidian": 160}', 1),
('refined_mithril_recipe', 'refined_mithril', '{"mithril": 16, "enchanted_coal": 8}', 1),
('refined_titanium_recipe', 'refined_titanium', '{"titanium": 16, "enchanted_iron": 8}', 1),

-- Swords from Migration 009
('undead_sword_recipe', 'undead_sword', '{"enchanted_bone": 8, "stick": 1}', 1),
('ender_sword_recipe', 'ender_sword', '{"enchanted_ender_pearl": 32, "stick": 1}', 1),
('prismarine_blade_recipe', 'prismarine_blade', '{"prismarine_shard": 64, "stick": 1}', 1),
('flaming_sword_recipe', 'flaming_sword', '{"enchanted_blaze_rod": 16, "diamond_sword": 1}', 1),
('emerald_blade_recipe', 'emerald_blade', '{"enchanted_emerald": 32, "stick": 1}', 1),
('spider_sword_recipe', 'spider_sword', '{"enchanted_string": 32, "stick": 1}', 1),
('thick_scorpion_foil_recipe', 'thick_scorpion_foil', '{"scorpion_foil": 1, "enchanted_iron_block": 8}', 1),
('thick_aspect_of_the_end_recipe', 'thick_aspect_of_the_end', '{"aspect_of_the_end": 1, "enchanted_ender_pearl": 64}', 1),
('scorpion_foil_recipe', 'scorpion_foil', '{"enchanted_string": 64, "stick": 1, "spider_eye": 32}', 1),
('ornate_zombie_sword_recipe', 'ornate_zombie_sword', '{"zombie_sword": 1, "enchanted_rotten_flesh": 64}', 1),
('fabled_sword_recipe', 'fabled_sword', '{"enchanted_diamond_block": 32, "nether_star": 1}', 1),
('void_sword_recipe', 'void_sword', '{"enchanted_obsidian": 32, "enchanted_eye_of_ender": 16}', 1),
('crimson_blade_recipe', 'crimson_blade', '{"enchanted_blaze_rod": 64, "enchanted_gold_block": 16}', 1),
('aurora_sword_recipe', 'aurora_sword', '{"enchanted_diamond_block": 16, "enchanted_lapis_block": 32, "nether_star": 1}', 1),
('tacticians_sword_recipe', 'tacticians_sword', '{"enchanted_iron_block": 32, "enchanted_diamond": 64}', 1),
('glacial_scythe_recipe', 'glacial_scythe', '{"frozen_scythe": 1, "enchanted_ice": 64, "enchanted_diamond_block": 32}', 1),
('voidwalker_katana_recipe', 'voidwalker_katana', '{"void_sword": 1, "enchanted_ender_pearl": 128, "nether_star": 2}', 1),
('molten_edge_recipe', 'molten_edge', '{"crimson_blade": 1, "dragon_scale": 16, "enchanted_blaze_rod": 128}', 1),
('dark_claymore_recipe', 'dark_claymore', '{"fabled_sword": 1, "necron_blade": 1, "wither_catalyst": 64}', 1),

-- Additional Materials
('enchanted_rotten_flesh_recipe', 'enchanted_rotten_flesh', '{"rotten_flesh": 160}', 1),
('enchanted_coal_recipe', 'enchanted_coal', '{"coal": 160}', 1),
('enchanted_lapis_recipe', 'enchanted_lapis', '{"lapis_lazuli": 160}', 1),
('enchanted_lapis_block_recipe', 'enchanted_lapis_block', '{"enchanted_lapis": 160}', 1),
('enchanted_ice_recipe', 'enchanted_ice', '{"ice": 160}', 1),
('wither_catalyst_recipe', 'wither_catalyst', '{"nether_star": 4, "enchanted_bone": 64}', 1),

-- Armor Sets from Migration 009
('hardened_diamond_chestplate_recipe', 'hardened_diamond_chestplate', '{"diamond": 24}', 1),
('hardened_diamond_leggings_recipe', 'hardened_diamond_leggings', '{"diamond": 21}', 1),
('hardened_diamond_boots_recipe', 'hardened_diamond_boots', '{"diamond": 12}', 1),
('ender_helmet_recipe', 'ender_helmet', '{"enchanted_ender_pearl": 64, "enchanted_eye_of_ender": 8}', 1),
('ender_chestplate_recipe', 'ender_chestplate', '{"enchanted_ender_pearl": 128, "enchanted_eye_of_ender": 16}', 1),
('ender_leggings_recipe', 'ender_leggings', '{"enchanted_ender_pearl": 96, "enchanted_eye_of_ender": 12}', 1),
('ender_boots_recipe', 'ender_boots', '{"enchanted_ender_pearl": 64, "enchanted_eye_of_ender": 8}', 1),
('miner_helmet_recipe', 'miner_helmet', '{"enchanted_iron": 16, "enchanted_coal": 8}', 1),
('miner_chestplate_recipe', 'miner_chestplate', '{"enchanted_iron": 32, "enchanted_coal": 16}', 1),
('miner_leggings_recipe', 'miner_leggings', '{"enchanted_iron": 24, "enchanted_coal": 12}', 1),
('miner_boots_recipe', 'miner_boots', '{"enchanted_iron": 16, "enchanted_coal": 8}', 1),

-- Tools from Migration 009
('mithril_pickaxe_recipe', 'mithril_pickaxe', '{"refined_mithril": 4, "enchanted_diamond": 32}', 1),
('titanium_pickaxe_recipe', 'titanium_pickaxe', '{"refined_titanium": 4, "enchanted_diamond": 32}', 1),
('drill_recipe', 'drill', '{"titanium_pickaxe": 1, "enchanted_iron_block": 32, "enchanted_redstone_block": 16}', 1),
('jungle_axe_recipe', 'jungle_axe', '{"enchanted_oak_wood": 64, "diamond_axe": 1}', 1),
('treecapitator_recipe', 'treecapitator', '{"jungle_axe": 1, "enchanted_oak_wood": 128, "enchanted_diamond": 32}', 1),
('blessed_hoe_recipe', 'blessed_hoe', '{"enchanted_wheat": 64, "diamond_hoe": 1}', 1),
('mathematical_hoe_recipe', 'mathematical_hoe', '{"blessed_hoe": 1, "enchanted_emerald": 64, "enchanted_diamond": 32}', 1),
('prismarine_rod_recipe', 'prismarine_rod', '{"prismarine_shard": 128, "diamond_fishing_rod": 1}', 1),
('rod_of_champions_recipe', 'rod_of_champions', '{"prismarine_rod": 1, "enchanted_diamond": 64, "nether_star": 1}', 1),

-- More Materials
('enchanted_wheat_recipe', 'enchanted_wheat', '{"wheat": 160}', 1),
('enchanted_redstone_recipe', 'enchanted_redstone', '{"redstone": 160}', 1),
('enchanted_redstone_block_recipe', 'enchanted_redstone_block', '{"enchanted_redstone": 160}', 1);

-- ============================================
-- Extract recipes from migration 011
-- ============================================

INSERT OR IGNORE INTO crafting_recipes (recipe_id, output_item, ingredients, output_amount)
VALUES
-- Leather Armor
('leather_helmet_recipe', 'leather_helmet', '{"leather": 5}', 1),
('leather_chestplate_recipe', 'leather_chestplate', '{"leather": 8}', 1),
('leather_leggings_recipe', 'leather_leggings', '{"leather": 7}', 1),
('leather_boots_recipe', 'leather_boots', '{"leather": 4}', 1),

-- Chainmail Armor
('chainmail_helmet_recipe', 'chainmail_helmet', '{"iron_ingot": 5, "string": 3}', 1),
('chainmail_chestplate_recipe', 'chainmail_chestplate', '{"iron_ingot": 8, "string": 5}', 1),
('chainmail_leggings_recipe', 'chainmail_leggings', '{"iron_ingot": 7, "string": 4}', 1),
('chainmail_boots_recipe', 'chainmail_boots', '{"iron_ingot": 4, "string": 2}', 1),

-- Iron Armor
('iron_helmet_recipe', 'iron_helmet', '{"iron_ingot": 5}', 1),
('iron_chestplate_recipe', 'iron_chestplate', '{"iron_ingot": 8}', 1),
('iron_leggings_recipe', 'iron_leggings', '{"iron_ingot": 7}', 1),
('iron_boots_recipe', 'iron_boots', '{"iron_ingot": 4}', 1),

-- Gold Armor
('gold_helmet_recipe', 'gold_helmet', '{"gold_ingot": 5}', 1),
('gold_chestplate_recipe', 'gold_chestplate', '{"gold_ingot": 8}', 1),
('gold_leggings_recipe', 'gold_leggings', '{"gold_ingot": 7}', 1),
('gold_boots_recipe', 'gold_boots', '{"gold_ingot": 4}', 1),

-- Diamond Armor
('diamond_helmet_recipe', 'diamond_helmet', '{"diamond": 5}', 1),
('diamond_chestplate_recipe', 'diamond_chestplate', '{"diamond": 8}', 1),
('diamond_leggings_recipe', 'diamond_leggings', '{"diamond": 7}', 1),
('diamond_boots_recipe', 'diamond_boots', '{"diamond": 4}', 1),

-- Hardened Diamond Armor (from migration 011)
('hardened_diamond_chestplate_011_recipe', 'hardened_diamond_chestplate', '{"diamond": 24, "enchanted_diamond": 4}', 1),
('hardened_diamond_leggings_011_recipe', 'hardened_diamond_leggings', '{"diamond": 21, "enchanted_diamond": 3}', 1),
('hardened_diamond_boots_011_recipe', 'hardened_diamond_boots', '{"diamond": 12, "enchanted_diamond": 2}', 1),

-- Emerald Armor
('emerald_helmet_recipe', 'emerald_helmet', '{"emerald": 40}', 1),
('emerald_chestplate_recipe', 'emerald_chestplate', '{"emerald": 64}', 1),
('emerald_leggings_recipe', 'emerald_leggings', '{"emerald": 56}', 1),
('emerald_boots_recipe', 'emerald_boots', '{"emerald": 32}', 1),

-- Young Dragon Armor
('young_dragon_chestplate_recipe', 'young_dragon_chestplate', '{"young_dragon_fragment": 80, "enchanted_ender_pearl": 32}', 1),
('young_dragon_leggings_recipe', 'young_dragon_leggings', '{"young_dragon_fragment": 70, "enchanted_ender_pearl": 28}', 1),
('young_dragon_boots_recipe', 'young_dragon_boots', '{"young_dragon_fragment": 50, "enchanted_ender_pearl": 20}', 1),

-- Strong Dragon Armor
('strong_dragon_chestplate_recipe', 'strong_dragon_chestplate', '{"strong_dragon_fragment": 80, "enchanted_diamond": 64}', 1),
('strong_dragon_leggings_recipe', 'strong_dragon_leggings', '{"strong_dragon_fragment": 70, "enchanted_diamond": 56}', 1),
('strong_dragon_boots_recipe', 'strong_dragon_boots', '{"strong_dragon_fragment": 50, "enchanted_diamond": 40}', 1),

-- Wise Dragon Armor
('wise_dragon_helmet_recipe', 'wise_dragon_helmet', '{"wise_dragon_fragment": 60, "enchanted_lapis_block": 32}', 1),
('wise_dragon_chestplate_recipe', 'wise_dragon_chestplate', '{"wise_dragon_fragment": 80, "enchanted_lapis_block": 64}', 1),
('wise_dragon_leggings_recipe', 'wise_dragon_leggings', '{"wise_dragon_fragment": 70, "enchanted_lapis_block": 56}', 1),
('wise_dragon_boots_recipe', 'wise_dragon_boots', '{"wise_dragon_fragment": 50, "enchanted_lapis_block": 40}', 1),

-- Superior Dragon Armor
('superior_dragon_helmet_recipe', 'superior_dragon_helmet', '{"superior_dragon_fragment": 60, "nether_star": 4}', 1),
('superior_dragon_chestplate_recipe', 'superior_dragon_chestplate', '{"superior_dragon_fragment": 80, "nether_star": 8}', 1),
('superior_dragon_leggings_recipe', 'superior_dragon_leggings', '{"superior_dragon_fragment": 70, "nether_star": 6}', 1),
('superior_dragon_boots_recipe', 'superior_dragon_boots', '{"superior_dragon_fragment": 50, "nether_star": 4}', 1),

-- Pickaxes
('stone_pickaxe_recipe', 'stone_pickaxe', '{"stick": 2, "cobblestone": 3}', 1),
('gold_pickaxe_recipe', 'gold_pickaxe', '{"stick": 2, "gold_ingot": 3}', 1),
('iron_pickaxe_recipe', 'iron_pickaxe', '{"stick": 2, "iron_ingot": 3}', 1),
('diamond_pickaxe_recipe', 'diamond_pickaxe', '{"stick": 2, "diamond": 3}', 1),
('mithril_pickaxe_011_recipe', 'mithril_pickaxe', '{"diamond_pickaxe": 1, "enchanted_mithril": 16}', 1),
('titanium_pickaxe_011_recipe', 'titanium_pickaxe', '{"mithril_pickaxe": 1, "titanium": 32}', 1),

-- Axes
('wooden_axe_recipe', 'wooden_axe', '{"stick": 2, "oak_wood": 3}', 1),
('stone_axe_recipe', 'stone_axe', '{"stick": 2, "cobblestone": 3}', 1),
('iron_axe_recipe', 'iron_axe', '{"stick": 2, "iron_ingot": 3}', 1),
('diamond_axe_recipe', 'diamond_axe', '{"stick": 2, "diamond": 3}', 1),
('jungle_axe_011_recipe', 'jungle_axe', '{"diamond_axe": 1, "enchanted_jungle_wood": 64}', 1),
('treecapitator_011_recipe', 'treecapitator', '{"jungle_axe": 1, "enchanted_oak_wood": 128, "enchanted_dark_oak_wood": 64}', 1),

-- Hoes
('wooden_hoe_recipe', 'wooden_hoe', '{"stick": 2, "oak_wood": 2}', 1),
('stone_hoe_recipe', 'stone_hoe', '{"stick": 2, "cobblestone": 2}', 1),
('iron_hoe_recipe', 'iron_hoe', '{"stick": 2, "iron_ingot": 2}', 1),
('diamond_hoe_recipe', 'diamond_hoe', '{"stick": 2, "diamond": 2}', 1),
('blessed_hoe_011_recipe', 'blessed_hoe', '{"diamond_hoe": 1, "enchanted_hay_bale": 32}', 1),
('mathematical_hoe_011_recipe', 'mathematical_hoe', '{"blessed_hoe": 1, "enchanted_melon_block": 64, "enchanted_pumpkin": 64}', 1),
y
-- Fishing Rods
('fishing_rod_recipe', 'fishing_rod', '{"stick": 3, "string": 2}', 1),
('prismarine_rod_011_recipe', 'prismarine_rod', '{"fishing_rod": 1, "prismarine_shard": 16}', 1),
('sponge_rod_recipe', 'sponge_rod', '{"prismarine_rod": 1, "sponge": 8}', 1),
('rod_of_champions_011_recipe', 'rod_of_champions', '{"sponge_rod": 1, "enchanted_sponge": 16, "enchanted_prismarine": 32}', 1),
('rod_of_legends_recipe', 'rod_of_legends', '{"rod_of_champions": 1, "enchanted_sponge": 64, "sea_lantern": 32}', 1),

-- Swords from Migration 011
('gold_sword_recipe', 'gold_sword', '{"stick": 1, "gold_ingot": 2}', 1),
('cleaver_recipe', 'cleaver', '{"iron_sword": 1, "enchanted_pork": 32}', 1),
('silver_fang_recipe', 'silver_fang', '{"diamond_sword": 1, "enchanted_quartz": 32, "wolf_tooth": 16}', 1),
('golem_sword_recipe', 'golem_sword', '{"diamond_sword": 1, "enchanted_iron_block": 16}', 1),
('ember_rod_recipe', 'ember_rod', '{"blaze_rod": 128, "enchanted_blaze_powder": 32}', 1),
('frozen_scythe_recipe', 'frozen_scythe', '{"diamond_sword": 1, "ice": 64, "packed_ice": 32}', 1),

-- Special Armor Sets
('farmer_helmet_recipe', 'farmer_helmet', '{"hay_bale": 40, "enchanted_seeds": 16}', 1),
('farmer_chestplate_recipe', 'farmer_chestplate', '{"hay_bale": 64, "enchanted_seeds": 32}', 1),
('farmer_leggings_recipe', 'farmer_leggings', '{"hay_bale": 56, "enchanted_seeds": 24}', 1),
('farmer_boots_recipe', 'farmer_boots', '{"hay_bale": 32, "enchanted_seeds": 16}', 1),
('miner_helmet_011_recipe', 'miner_helmet', '{"iron_block": 20, "enchanted_coal": 16}', 1),
('miner_chestplate_011_recipe', 'miner_chestplate', '{"iron_block": 32, "enchanted_coal": 32}', 1),
('miner_leggings_011_recipe', 'miner_leggings', '{"iron_block": 28, "enchanted_coal": 24}', 1),
('miner_boots_011_recipe', 'miner_boots', '{"iron_block": 16, "enchanted_coal": 16}', 1);
