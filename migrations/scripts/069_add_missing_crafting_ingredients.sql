-- Migration 069: Add missing items that are referenced in crafting recipes
-- This includes basic items like bow, tnt, and various materials

-- Basic combat items
INSERT OR IGNORE INTO game_items (item_id, name, rarity, item_type, lore, npc_sell_price, default_bazaar_price) VALUES
('bow', 'Bow', 'COMMON', 'BOW', 'A basic bow for shooting arrows', 50, 250),
('tnt', 'TNT', 'COMMON', 'ITEM', 'Explosive block', 20, 100),
('sugar', 'Sugar', 'COMMON', 'ITEM', 'Sweet crystalline substance', 1, 5);

-- Basic materials
INSERT OR IGNORE INTO game_items (item_id, name, rarity, item_type, lore, npc_sell_price, default_bazaar_price) VALUES
('oak_log', 'Oak Log', 'COMMON', 'ITEM', 'Raw oak wood', 2, 10),
('jungle_log', 'Jungle Log', 'COMMON', 'ITEM', 'Raw jungle wood', 3, 15),
('wood', 'Wood', 'COMMON', 'ITEM', 'Basic wood material', 1, 5),
('wooden_plank', 'Wooden Plank', 'COMMON', 'ITEM', 'Crafted wooden plank', 2, 8),
('iron_block', 'Iron Block', 'COMMON', 'ITEM', 'Block of iron', 100, 500);

-- Enchanted materials
INSERT OR IGNORE INTO game_items (item_id, name, rarity, item_type, lore, npc_sell_price, default_bazaar_price) VALUES
('enchanted_oak_log', 'Enchanted Oak Log', 'UNCOMMON', 'ITEM', '160 Oak Logs combined', 320, 1600),
('enchanted_blaze_powder', 'Enchanted Blaze Powder', 'UNCOMMON', 'ITEM', '160 Blaze Powder combined', 320, 1600),
('enchanted_cake', 'Enchanted Cake', 'RARE', 'ITEM', '160 Cakes combined', 3200, 16000),
('enchanted_chest', 'Enchanted Chest', 'UNCOMMON', 'ITEM', '160 Chests combined', 1600, 8000),
('enchanted_cocoa_beans', 'Enchanted Cocoa Beans', 'UNCOMMON', 'ITEM', '160 Cocoa Beans combined', 320, 1600),
('enchanted_cooked_salmon', 'Enchanted Cooked Salmon', 'UNCOMMON', 'ITEM', '160 Cooked Salmon combined', 480, 2400),
('enchanted_glowstone_block', 'Enchanted Glowstone Block', 'RARE', 'ITEM', '160 Glowstone Blocks combined', 3200, 16000),
('enchanted_golden_carrot', 'Enchanted Golden Carrot', 'RARE', 'ITEM', '160 Golden Carrots combined', 4800, 24000),
('enchanted_lily_pad', 'Enchanted Lily Pad', 'UNCOMMON', 'ITEM', '160 Lily Pads combined', 320, 1600),
('enchanted_raw_fish', 'Enchanted Raw Fish', 'UNCOMMON', 'ITEM', '160 Raw Fish combined', 320, 1600),
('enchanted_seeds', 'Enchanted Seeds', 'UNCOMMON', 'ITEM', '160 Seeds combined', 160, 800),
('enchanted_sponge', 'Enchanted Sponge', 'RARE', 'ITEM', '160 Sponges combined', 6400, 32000),
('enchanted_wood_block', 'Enchanted Wood Block', 'UNCOMMON', 'ITEM', '160 Wood Blocks combined', 320, 1600);

-- Gemstones and precious materials
INSERT OR IGNORE INTO game_items (item_id, name, rarity, item_type, lore, npc_sell_price, default_bazaar_price) VALUES
('ruby', 'Ruby', 'RARE', 'ITEM', 'A precious red gemstone', 100, 500),
('perfect_ruby', 'Perfect Ruby', 'EPIC', 'ITEM', 'A flawless ruby gemstone', 10000, 50000),
('perfect_sapphire', 'Perfect Sapphire', 'EPIC', 'ITEM', 'A flawless sapphire gemstone', 10000, 50000),
('perfect_amber', 'Perfect Amber', 'EPIC', 'ITEM', 'A flawless amber gemstone', 10000, 50000),
('perfect_gemstone', 'Perfect Gemstone', 'LEGENDARY', 'ITEM', 'A perfect gemstone of ultimate quality', 50000, 250000);

-- Special fragments and materials
INSERT OR IGNORE INTO game_items (item_id, name, rarity, item_type, lore, npc_sell_price, default_bazaar_price) VALUES
('holy_fragment', 'Holy Fragment', 'RARE', 'ITEM', 'A fragment blessed with holy power', 500, 2500),
('storm_fragment', 'Storm Fragment', 'EPIC', 'ITEM', 'Fragment of a powerful storm', 2000, 10000),
('soul_fragment', 'Soul Fragment', 'EPIC', 'ITEM', 'Fragment of a captured soul', 2000, 10000),
('dark_orb', 'Dark Orb', 'LEGENDARY', 'ITEM', 'A mysterious orb pulsing with dark energy', 10000, 50000),
('sea_emperor_fragment', 'Sea Emperor Fragment', 'LEGENDARY', 'ITEM', 'Fragment from the Sea Emperor', 15000, 75000),
('wise_dragon_fragment', 'Wise Dragon Fragment', 'LEGENDARY', 'ITEM', 'Fragment from a Wise Dragon', 20000, 100000),
('divans_fragment', 'Divan''s Fragment', 'MYTHIC', 'ITEM', 'Ancient fragment from Divan''s Mines', 50000, 250000),
('mathematical_blueprint', 'Mathematical Blueprint', 'LEGENDARY', 'ITEM', 'Blueprint for the Mathematical Hoe', 100000, 500000);

-- Special items
INSERT OR IGNORE INTO game_items (item_id, name, rarity, item_type, lore, npc_sell_price, default_bazaar_price) VALUES
('trophy_fish', 'Trophy Fish', 'RARE', 'ITEM', 'A rare trophy from fishing', 1000, 5000),
('sea_lantern', 'Sea Lantern', 'UNCOMMON', 'ITEM', 'Glowing underwater light source', 200, 1000);

-- Drill components
INSERT OR IGNORE INTO game_items (item_id, name, rarity, item_type, lore, npc_sell_price, default_bazaar_price) VALUES
('drill_engine', 'Drill Engine', 'RARE', 'ITEM', 'Engine component for drills', 5000, 25000),
('advanced_drill_engine', 'Advanced Drill Engine', 'EPIC', 'ITEM', 'Advanced engine component for drills', 20000, 100000);

-- Weapons that were missing
INSERT OR IGNORE INTO game_items (item_id, name, rarity, item_type, lore, npc_sell_price, default_bazaar_price) VALUES
('scorpion_bow', 'Scorpion Bow', 'EPIC', 'BOW', 'A bow with venomous power', 10000, 50000),
('mithril_drill', 'Mithril Drill', 'RARE', 'DRILL', 'A drill made from mithril', 15000, 75000);

-- Add weapon stats for bow
INSERT OR IGNORE INTO weapon_stats (item_id, damage, strength, crit_chance, crit_damage, attack_speed, intelligence, ability_damage) VALUES
('bow', 50, 0, 10, 50, 0, 0, 0);

-- Add weapon ability for bow
INSERT OR IGNORE INTO weapon_abilities (item_id, ability_name, mana_cost, cooldown, base_damage_multiplier, intelligence_scaling, strength_scaling, ability_damage_scaling, aoe_radius, arrows, description) VALUES
('bow', 'Shoot Arrow', 0, 0.0, 1.0, 0.0, 0.001, 0.0, 0, 1, 'Shoot an arrow at your target');

-- Add weapon stats for scorpion_bow
INSERT OR IGNORE INTO weapon_stats (item_id, damage, strength, crit_chance, crit_damage, attack_speed, intelligence, ability_damage) VALUES
('scorpion_bow', 160, 30, 15, 65, 0, 0, 0);

-- Add weapon ability for scorpion_bow
INSERT OR IGNORE INTO weapon_abilities (item_id, ability_name, mana_cost, cooldown, base_damage_multiplier, intelligence_scaling, strength_scaling, ability_damage_scaling, aoe_radius, arrows, description) VALUES
('scorpion_bow', 'Venom Shot', 50, 3.0, 8.0, 0.0, 0.012, 0.0, 0, 1, 'Shoot an arrow that poisons the target');

-- Add weapon stats for mithril_drill
INSERT OR IGNORE INTO weapon_stats (item_id, damage, strength, crit_chance, crit_damage, attack_speed, intelligence, ability_damage) VALUES
('mithril_drill', 120, 40, 0, 0, 0, 0, 0);

-- Add combat drop yield multipliers
UPDATE weapon_stats SET combat_drop_yield_multiplier = 1.0 WHERE item_id = 'bow';
UPDATE weapon_stats SET combat_drop_yield_multiplier = 4.5 WHERE item_id = 'scorpion_bow';
UPDATE weapon_stats SET combat_drop_yield_multiplier = 4.0 WHERE item_id = 'mithril_drill';

-- Add mining/gathering xp for new items
INSERT OR IGNORE INTO gathering_drop_xp (item_id, base_xp) VALUES
('oak_log', 50),
('jungle_log', 80),
('wood', 30),
('wooden_plank', 20),
('ruby', 50),
('sugar', 20);

INSERT OR IGNORE INTO combat_drop_xp (item_id, base_xp) VALUES
('trophy_fish', 100);
