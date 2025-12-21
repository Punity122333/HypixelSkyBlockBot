INSERT OR IGNORE INTO game_items (item_id, name, rarity, item_type, lore) VALUES
('personal_bank', 'Personal Bank', 'RARE', 'UTILITY', 'Store coins safely in your personal vault'),
('booster_cookie', 'Booster Cookie', 'RARE', 'CONSUMABLE', 'Provides various buffs for 4 days'),
('portable_crafter', 'Portable Crafting Table', 'UNCOMMON', 'UTILITY', 'Access crafting from anywhere'),
('portable_storage', 'Portable Storage', 'RARE', 'UTILITY', 'Access storage from anywhere'),
('warp_scroll', 'Warp Scroll', 'UNCOMMON', 'CONSUMABLE', 'Instantly warp to a previously visited location'),
('teleport_pad', 'Teleport Pad', 'EPIC', 'UTILITY', 'Create a teleportation waypoint'),
('travel_scroll', 'Travel Scroll', 'RARE', 'CONSUMABLE', 'Quick travel to hub islands'),
('dungeon_orb', 'Dungeon Orb', 'LEGENDARY', 'UTILITY', 'Grants special buffs in dungeons'),
('party_finder_token', 'Party Finder Token', 'RARE', 'UTILITY', 'Create premium party finder listings'),
('autopet_rules', 'Autopet Rules', 'EPIC', 'UTILITY', 'Automatically swap pets based on activity'),
('kiss_the_fish', 'Kiss The Fish', 'UNCOMMON', 'UTILITY', 'Grants Fishing Speed for 1 hour'),
('mining_speed_boost', 'Mining Speed Boost', 'UNCOMMON', 'CONSUMABLE', 'Increases mining speed for 1 hour'),
('farming_speed_boost', 'Farming Speed Boost', 'UNCOMMON', 'CONSUMABLE', 'Increases farming speed for 1 hour'),
('bits_talisman', 'Bits Talisman', 'RARE', 'ACCESSORY', 'Earn bits from various activities'),
('piggy_bank', 'Piggy Bank', 'UNCOMMON', 'UTILITY', 'Store extra coins with interest');

INSERT OR IGNORE INTO crafting_recipes (recipe_id, output_item, ingredients, output_amount) VALUES
('personal_bank_recipe', 'personal_bank', '{"enchanted_iron": 32, "enchanted_gold": 16, "enchanted_diamond": 8}', 1),
('booster_cookie_recipe', 'booster_cookie', '{"enchanted_sugar": 64, "enchanted_cocoa_beans": 32, "enchanted_wheat": 32}', 1),
('portable_crafter_recipe', 'portable_crafter', '{"oak_wood": 64, "enchanted_oak_wood": 8, "stick": 16}', 1),
('portable_storage_recipe', 'portable_storage', '{"enchanted_chest": 8, "enchanted_iron": 16, "enchanted_gold": 8}', 1),
('warp_scroll_recipe', 'warp_scroll', '{"paper": 16, "ender_pearl": 4, "enchanted_eye_of_ender": 1}', 1),
('teleport_pad_recipe', 'teleport_pad', '{"enchanted_obsidian": 32, "enchanted_ender_pearl": 16, "enchanted_diamond": 8}', 1),
('travel_scroll_recipe', 'travel_scroll', '{"paper": 8, "ender_pearl": 2, "enchanted_feather": 4}', 1),
('dungeon_orb_recipe', 'dungeon_orb', '{"enchanted_diamond": 64, "enchanted_gold": 64, "wither_essence": 16}', 1),
('party_finder_token_recipe', 'party_finder_token', '{"enchanted_gold": 16, "enchanted_paper": 8, "enchanted_quartz": 8}', 1),
('autopet_rules_recipe', 'autopet_rules', '{"enchanted_gold": 32, "enchanted_lapis": 16, "enchanted_redstone": 16}', 1),
('kiss_the_fish_recipe', 'kiss_the_fish', '{"raw_fish": 64, "enchanted_raw_fish": 16, "enchanted_lily_pad": 8}', 1),
('mining_speed_boost_recipe', 'mining_speed_boost', '{"enchanted_cobblestone": 16, "enchanted_coal": 8, "sugar": 32}', 1),
('farming_speed_boost_recipe', 'farming_speed_boost', '{"enchanted_wheat": 16, "enchanted_carrot": 8, "sugar": 32}', 1),
('bits_talisman_recipe', 'bits_talisman', '{"enchanted_quartz": 32, "enchanted_gold": 16, "enchanted_lapis": 16}', 1),
('piggy_bank_recipe', 'piggy_bank', '{"enchanted_pork": 16, "enchanted_gold": 8, "enchanted_iron": 8}', 1);

