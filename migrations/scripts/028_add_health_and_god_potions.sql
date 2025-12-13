INSERT OR REPLACE INTO game_items (item_id, name, rarity, item_type, stats, lore, special_ability, npc_sell_price, default_bazaar_price)
VALUES 
('health_potion', 'Health Potion', 'COMMON', 'POTION', '{}', '["Instantly restores 100 HP"]', 'Heals 100 HP instantly', 10, 50),
('greater_health_potion', 'Greater Health Potion', 'UNCOMMON', 'POTION', '{}', '["Instantly restores 250 HP"]', 'Heals 250 HP instantly', 30, 150),
('super_health_potion', 'Super Health Potion', 'RARE', 'POTION', '{}', '["Instantly restores 500 HP"]', 'Heals 500 HP instantly', 100, 500),
('ultimate_health_potion', 'Ultimate Health Potion', 'EPIC', 'POTION', '{}', '["Instantly restores 1000 HP"]', 'Heals 1000 HP instantly', 500, 2500),
('god_potion', 'God Potion', 'LEGENDARY', 'POTION', '{}', '["Grants ALL stat bonuses for 20 minutes!", "+50 to most stats", "+25 to special stats"]', 'Grants all stat bonuses', 10000, 50000);

INSERT OR REPLACE INTO crafting_recipes (recipe_id, output_item, ingredients, output_amount)
VALUES 
('health_potion_recipe', 'health_potion', '{"melon": 8, "sugar_cane": 4}', 1),
('greater_health_potion_recipe', 'greater_health_potion', '{"health_potion": 3, "enchanted_melon": 2, "glowstone_dust": 4}', 1),
('super_health_potion_recipe', 'super_health_potion', '{"greater_health_potion": 3, "enchanted_melon_block": 1, "enchanted_glowstone": 2}', 1),
('ultimate_health_potion_recipe', 'ultimate_health_potion', '{"super_health_potion": 3, "enchanted_golden_carrot": 1, "enchanted_glowstone_block": 1}', 1),
('god_potion_recipe', 'god_potion', '{"enchanted_gold_block": 4, "enchanted_diamond_block": 2, "enchanted_redstone_block": 2, "enchanted_lapis_block": 2, "enchanted_emerald_block": 2}', 1);
