BEGIN TRANSACTION;

INSERT OR IGNORE INTO game_items (item_id, name, rarity, item_type, stats, lore, special_ability, craft_recipe, npc_sell_price, collection_req, default_bazaar_price)
VALUES 
('melon', 'Melon', 'COMMON', 'ITEM', '{}', '', '', NULL, 2, NULL, 10),
('apple', 'Apple', 'COMMON', 'ITEM', '{}', '', '', NULL, 1, NULL, 10),
('enchanted_glistering_melon', 'Enchanted Glistering Melon', 'RARE', 'ITEM', '{}', '', '', '{"enchanted_melon": 160, "enchanted_gold": 8}', 100, NULL, 12500),
('golden_apple', 'Golden Apple', 'UNCOMMON', 'ITEM', '{}', '', '', '{"enchanted_gold": 8, "apple": 1}', 10, NULL, 500),
('enchanted_golden_apple', 'Enchanted Golden Apple', 'RARE', 'ITEM', '{}', '', '', '{"golden_apple": 160}', 50, NULL, 12500),
('health_potion', 'Health Potion', 'COMMON', 'POTION', '{}', 'Instantly restores 100 HP', '', '{"awkward_potion": 1, "enchanted_ghast_tear": 8, "enchanted_melon": 8}', 50, NULL, 1000),
('greater_health_potion', 'Greater Health Potion', 'UNCOMMON', 'POTION', '{}', 'Instantly restores 250 HP', '', '{"health_potion": 1, "enchanted_golden_apple": 4, "enchanted_ghast_tear": 16}', 150, NULL, 5000),
('super_health_potion', 'Super Health Potion', 'RARE', 'POTION', '{}', 'Instantly restores 500 HP', '', '{"greater_health_potion": 1, "enchanted_glistering_melon": 16, "enchanted_golden_apple": 8}', 300, NULL, 25000),
('ultimate_health_potion', 'Ultimate Health Potion', 'EPIC', 'POTION', '{}', 'Instantly restores 1000 HP', '', '{"super_health_potion": 1, "enchanted_glistering_melon": 32, "enchanted_golden_apple": 16}', 500, NULL, 125000),
('god_potion', 'God Potion', 'MYTHIC', 'POTION', '{}', 'Grants ALL stat bonuses for 20 minutes! +50 Strength, Defense, Speed, +15 Crit Chance, Ferocity, +50 Crit Damage, Intelligence, +25 Magic Find, True Defense, +30 Ability Damage, +15 Attack Speed, +50 Mining/Farming/Foraging Fortune, +50 Fishing Speed, +15 Pet Luck', '', '{"strength_potion_3": 1, "defense_potion_3": 1, "speed_potion_3": 1, "critical_potion_3": 1, "crit_damage_potion_3": 1, "intelligence_potion_3": 1, "magic_find_potion_3": 1, "ability_damage_potion_3": 1, "ferocity_potion_3": 1, "true_defense_potion_3": 1, "attack_speed_potion_3": 1, "enchanted_diamond_block": 64, "enchanted_gold_block": 64, "nether_star": 16}', 10000, NULL, 3125000);

UPDATE game_items SET rarity = 'MYTHIC' WHERE item_id = 'god_potion';

INSERT OR IGNORE INTO crafting_recipes (recipe_id, output_item, ingredients, output_amount)
VALUES 
('enchanted_glistering_melon', 'enchanted_glistering_melon', '{"enchanted_melon": 160, "enchanted_gold": 8}', 1),
('golden_apple', 'golden_apple', '{"enchanted_gold": 8, "apple": 1}', 1),
('enchanted_golden_apple', 'enchanted_golden_apple', '{"golden_apple": 160}', 1),
('health_potion', 'health_potion', '{"awkward_potion": 1, "enchanted_ghast_tear": 8, "enchanted_melon": 8}', 1),
('greater_health_potion', 'greater_health_potion', '{"health_potion": 1, "enchanted_golden_apple": 4, "enchanted_ghast_tear": 16}', 1),
('super_health_potion', 'super_health_potion', '{"greater_health_potion": 1, "enchanted_glistering_melon": 16, "enchanted_golden_apple": 8}', 1),
('ultimate_health_potion', 'ultimate_health_potion', '{"super_health_potion": 1, "enchanted_glistering_melon": 32, "enchanted_golden_apple": 16}', 1),
('god_potion', 'god_potion', '{"strength_potion_3": 1, "defense_potion_3": 1, "speed_potion_3": 1, "critical_potion_3": 1, "crit_damage_potion_3": 1, "intelligence_potion_3": 1, "magic_find_potion_3": 1, "ability_damage_potion_3": 1, "ferocity_potion_3": 1, "true_defense_potion_3": 1, "attack_speed_potion_3": 1, "enchanted_diamond_block": 64, "enchanted_gold_block": 64, "nether_star": 16}', 1);

COMMIT;
