CREATE TABLE IF NOT EXISTS weapon_tiers (
    tier TEXT PRIMARY KEY,
    tier_level INTEGER NOT NULL,
    base_damage_multiplier REAL DEFAULT 1.0,
    stat_multiplier REAL DEFAULT 1.0
);

INSERT OR REPLACE INTO weapon_tiers (tier, tier_level, base_damage_multiplier, stat_multiplier) VALUES
('EARLY_GAME', 1, 1.0, 1.0),
('MID_GAME', 2, 3.0, 2.0),
('LATE_GAME', 3, 7.0, 4.0),
('END_GAME', 4, 15.0, 8.0);

CREATE TABLE IF NOT EXISTS item_tier_classification (
    item_id TEXT PRIMARY KEY,
    tier TEXT NOT NULL,
    category TEXT NOT NULL,
    FOREIGN KEY (tier) REFERENCES weapon_tiers(tier)
);

UPDATE game_items SET stats = json_set(stats, '$.damage', 1200, '$.strength', 500, '$.intelligence', 700, '$.crit_damage', 200, '$.ability_damage', 200, '$.ferocity', 30) WHERE item_id = 'hyperion';
UPDATE game_items SET stats = json_set(stats, '$.damage', 1050, '$.strength', 420, '$.intelligence', 550, '$.crit_damage', 170, '$.ability_damage', 140, '$.ferocity', 20) WHERE item_id = 'valkyrie';
UPDATE game_items SET stats = json_set(stats, '$.damage', 1000, '$.strength', 400, '$.intelligence', 500, '$.crit_damage', 160, '$.ability_damage', 120, '$.ferocity', 15) WHERE item_id = 'astraea';
UPDATE game_items SET stats = json_set(stats, '$.damage', 950, '$.strength', 380, '$.intelligence', 450, '$.crit_damage', 150, '$.ability_damage', 100) WHERE item_id = 'scylla';

UPDATE game_items SET stats = json_set(stats, '$.damage', 750, '$.strength', 320, '$.crit_damage', 120, '$.intelligence', 150, '$.ability_damage', 60) WHERE item_id = 'necron_blade';
UPDATE game_items SET stats = json_set(stats, '$.damage', 900, '$.strength', 350, '$.crit_damage', 40, '$.attack_speed', 50, '$.ferocity', 20) WHERE item_id = 'shadow_fury';
UPDATE game_items SET stats = json_set(stats, '$.damage', 850, '$.strength', 500, '$.crit_damage', 150) WHERE item_id = 'giants_sword';
UPDATE game_items SET stats = json_set(stats, '$.damage', 1100, '$.strength', 400, '$.crit_damage', 180) WHERE item_id = 'dark_claymore';
UPDATE game_items SET stats = json_set(stats, '$.damage', 700, '$.strength', 300, '$.crit_damage', 100) WHERE item_id = 'atomsplit_katana';

UPDATE game_items SET stats = json_set(stats, '$.damage', 650, '$.strength', 260, '$.intelligence', 250, '$.ability_damage', 40) WHERE item_id = 'reaper_scythe';
UPDATE game_items SET stats = json_set(stats, '$.damage', 580, '$.strength', 240) WHERE item_id = 'reaper_sword';
UPDATE game_items SET stats = json_set(stats, '$.damage', 600, '$.strength', 250, '$.intelligence', 120) WHERE item_id = 'wither_cloak_sword';

UPDATE game_items SET stats = json_set(stats, '$.damage', 420, '$.strength', 200, '$.crit_damage', 50, '$.ability_damage', 30) WHERE item_id = 'aspect_of_the_dragons';
UPDATE game_items SET stats = json_set(stats, '$.damage', 500, '$.strength', 220, '$.crit_damage', 100, '$.attack_speed', 110) WHERE item_id = 'livid_dagger';
UPDATE game_items SET stats = json_set(stats, '$.damage', 480, '$.strength', 200) WHERE item_id = 'midas_sword';
UPDATE game_items SET stats = json_set(stats, '$.damage', 380, '$.strength', 150, '$.intelligence', 100, '$.ability_damage', 20) WHERE item_id = 'yeti_sword';
UPDATE game_items SET stats = json_set(stats, '$.damage', 360, '$.strength', 170, '$.crit_damage', 50) WHERE item_id = 'flower_of_truth';

UPDATE game_items SET stats = json_set(stats, '$.damage', 250, '$.strength', 130, '$.crit_damage', 20) WHERE item_id = 'aspect_of_the_end';
UPDATE game_items SET stats = json_set(stats, '$.damage', 280, '$.strength', 150, '$.crit_damage', 30) WHERE item_id = 'thick_aspect_of_the_end';

UPDATE game_items SET stats = json_set(stats, '$.damage', 20, '$.strength', 5) WHERE item_id = 'wooden_sword';
UPDATE game_items SET stats = json_set(stats, '$.damage', 30, '$.strength', 8) WHERE item_id = 'stone_sword';
UPDATE game_items SET stats = json_set(stats, '$.damage', 40, '$.strength', 12) WHERE item_id = 'iron_sword';
UPDATE game_items SET stats = json_set(stats, '$.damage', 60, '$.strength', 18, '$.crit_damage', 5) WHERE item_id = 'diamond_sword';

UPDATE game_items SET stats = json_set(stats, '$.damage', 55, '$.strength', 10) WHERE item_id = 'rogue_sword';
UPDATE game_items SET stats = json_set(stats, '$.damage', 75, '$.strength', 20) WHERE item_id = 'spider_sword';
UPDATE game_items SET stats = json_set(stats, '$.damage', 85, '$.strength', 25) WHERE item_id = 'zombie_sword';

UPDATE game_items SET stats = json_set(stats, '$.damage', 95, '$.strength', 40, '$.intelligence', 20) WHERE item_id = 'fancy_sword';
UPDATE game_items SET stats = json_set(stats, '$.damage', 105, '$.strength', 45) WHERE item_id = 'hunter_knife';
UPDATE game_items SET stats = json_set(stats, '$.damage', 125, '$.strength', 60) WHERE item_id = 'end_sword';
UPDATE game_items SET stats = json_set(stats, '$.damage', 180, '$.strength', 85, '$.intelligence', 50) WHERE item_id = 'shaman_sword';
UPDATE game_items SET stats = json_set(stats, '$.damage', 170, '$.strength', 80, '$.crit_chance', 15) WHERE item_id = 'silver_fang';

UPDATE game_items SET stats = json_set(stats, '$.health', 200, '$.defense', 180, '$.strength', 60, '$.crit_damage', 45, '$.intelligence', 40) WHERE item_id = 'necron_helmet';
UPDATE game_items SET stats = json_set(stats, '$.health', 420, '$.defense', 320, '$.strength', 60, '$.crit_damage', 45, '$.intelligence', 40) WHERE item_id = 'necron_chestplate';
UPDATE game_items SET stats = json_set(stats, '$.health', 350, '$.defense', 260, '$.strength', 60, '$.crit_damage', 45, '$.intelligence', 40) WHERE item_id = 'necron_leggings';
UPDATE game_items SET stats = json_set(stats, '$.health', 230, '$.defense', 170, '$.strength', 60, '$.crit_damage', 45, '$.intelligence', 40) WHERE item_id = 'necron_boots';

UPDATE game_items SET stats = json_set(stats, '$.health', 200, '$.defense', 180, '$.strength', 50, '$.crit_damage', 35) WHERE item_id = 'goldor_helmet';
UPDATE game_items SET stats = json_set(stats, '$.health', 400, '$.defense', 300, '$.strength', 50, '$.crit_damage', 35) WHERE item_id = 'goldor_chestplate';
UPDATE game_items SET stats = json_set(stats, '$.health', 330, '$.defense', 240, '$.strength', 50, '$.crit_damage', 35) WHERE item_id = 'goldor_leggings';
UPDATE game_items SET stats = json_set(stats, '$.health', 220, '$.defense', 160, '$.strength', 50, '$.crit_damage', 35) WHERE item_id = 'goldor_boots';

UPDATE game_items SET stats = json_set(stats, '$.health', 180, '$.defense', 140, '$.crit_damage', 50, '$.speed', 15, '$.strength', 20) WHERE item_id = 'shadow_assassin_helmet';
UPDATE game_items SET stats = json_set(stats, '$.health', 350, '$.defense', 220, '$.crit_damage', 50, '$.speed', 15, '$.strength', 20) WHERE item_id = 'shadow_assassin_chestplate';
UPDATE game_items SET stats = json_set(stats, '$.health', 280, '$.defense', 180, '$.crit_damage', 50, '$.speed', 15, '$.strength', 20) WHERE item_id = 'shadow_assassin_leggings';
UPDATE game_items SET stats = json_set(stats, '$.health', 200, '$.defense', 125, '$.crit_damage', 50, '$.speed', 15, '$.strength', 20) WHERE item_id = 'shadow_assassin_boots';

UPDATE game_items SET stats = json_set(stats, '$.health', 180, '$.defense', 180, '$.strength', 15, '$.crit_damage', 15, '$.intelligence', 35) WHERE item_id = 'superior_dragon_helmet';
UPDATE game_items SET stats = json_set(stats, '$.health', 280, '$.defense', 280, '$.strength', 15, '$.crit_damage', 15, '$.intelligence', 35) WHERE item_id = 'superior_dragon_chestplate';
UPDATE game_items SET stats = json_set(stats, '$.health', 240, '$.defense', 240, '$.strength', 15, '$.crit_damage', 15, '$.intelligence', 35) WHERE item_id = 'superior_dragon_leggings';
UPDATE game_items SET stats = json_set(stats, '$.health', 150, '$.defense', 150, '$.strength', 15, '$.crit_damage', 15, '$.intelligence', 35) WHERE item_id = 'superior_dragon_boots';

UPDATE game_items SET stats = json_set(stats, '$.health', 160, '$.defense', 110, '$.strength', 35) WHERE item_id = 'strong_dragon_helmet';
UPDATE game_items SET stats = json_set(stats, '$.health', 250, '$.defense', 170, '$.strength', 35) WHERE item_id = 'strong_dragon_chestplate';
UPDATE game_items SET stats = json_set(stats, '$.health', 210, '$.defense', 140, '$.strength', 35) WHERE item_id = 'strong_dragon_leggings';
UPDATE game_items SET stats = json_set(stats, '$.health', 130, '$.defense', 85, '$.strength', 35) WHERE item_id = 'strong_dragon_boots';

UPDATE game_items SET stats = json_set(stats, '$.health', 140, '$.defense', 90, '$.speed', 35) WHERE item_id = 'young_dragon_helmet';
UPDATE game_items SET stats = json_set(stats, '$.health', 220, '$.defense', 140, '$.speed', 35) WHERE item_id = 'young_dragon_chestplate';
UPDATE game_items SET stats = json_set(stats, '$.health', 180, '$.defense', 120, '$.speed', 35) WHERE item_id = 'young_dragon_leggings';
UPDATE game_items SET stats = json_set(stats, '$.health', 110, '$.defense', 75, '$.speed', 35) WHERE item_id = 'young_dragon_boots';

UPDATE game_items SET stats = json_set(stats, '$.health', 85, '$.defense', 120, '$.strength', 5) WHERE item_id = 'hardened_diamond_helmet';
UPDATE game_items SET stats = json_set(stats, '$.health', 140, '$.defense', 195, '$.strength', 5) WHERE item_id = 'hardened_diamond_chestplate';
UPDATE game_items SET stats = json_set(stats, '$.health', 120, '$.defense', 165, '$.strength', 5) WHERE item_id = 'hardened_diamond_leggings';
UPDATE game_items SET stats = json_set(stats, '$.health', 70, '$.defense', 100, '$.strength', 5) WHERE item_id = 'hardened_diamond_boots';

UPDATE game_items SET stats = json_set(stats, '$.health', 30, '$.defense', 20) WHERE item_id = 'leather_helmet';
UPDATE game_items SET stats = json_set(stats, '$.health', 50, '$.defense', 35) WHERE item_id = 'leather_chestplate';
UPDATE game_items SET stats = json_set(stats, '$.health', 40, '$.defense', 28) WHERE item_id = 'leather_leggings';
UPDATE game_items SET stats = json_set(stats, '$.health', 25, '$.defense', 18) WHERE item_id = 'leather_boots';

UPDATE game_items SET stats = json_set(stats, '$.health', 45, '$.defense', 35) WHERE item_id = 'iron_helmet';
UPDATE game_items SET stats = json_set(stats, '$.health', 75, '$.defense', 60) WHERE item_id = 'iron_chestplate';
UPDATE game_items SET stats = json_set(stats, '$.health', 60, '$.defense', 50) WHERE item_id = 'iron_leggings';
UPDATE game_items SET stats = json_set(stats, '$.health', 35, '$.defense', 30) WHERE item_id = 'iron_boots';

UPDATE game_items SET stats = json_set(stats, '$.damage', 310, '$.strength', 40, '$.crit_damage', 20, '$.attack_speed', 50, '$.ability_damage', 20) WHERE item_id = 'juju_shortbow';
UPDATE game_items SET stats = json_set(stats, '$.damage', 500, '$.strength', 60, '$.crit_damage', 50, '$.attack_speed', 30, '$.ability_damage', 40) WHERE item_id = 'terminator';

UPDATE armor_stats SET health = 200, defense = 180, strength = 60, crit_damage = 45, intelligence = 40 WHERE item_id = 'necron_helmet';
UPDATE armor_stats SET health = 420, defense = 320, strength = 60, crit_damage = 45, intelligence = 40 WHERE item_id = 'necron_chestplate';
UPDATE armor_stats SET health = 350, defense = 260, strength = 60, crit_damage = 45, intelligence = 40 WHERE item_id = 'necron_leggings';
UPDATE armor_stats SET health = 230, defense = 170, strength = 60, crit_damage = 45, intelligence = 40 WHERE item_id = 'necron_boots';

UPDATE armor_stats SET health = 200, defense = 180, strength = 50, crit_damage = 35 WHERE item_id = 'goldor_helmet';
UPDATE armor_stats SET health = 400, defense = 300, strength = 50, crit_damage = 35 WHERE item_id = 'goldor_chestplate';
UPDATE armor_stats SET health = 330, defense = 240, strength = 50, crit_damage = 35 WHERE item_id = 'goldor_leggings';
UPDATE armor_stats SET health = 220, defense = 160, strength = 50, crit_damage = 35 WHERE item_id = 'goldor_boots';

UPDATE armor_stats SET health = 180, defense = 140, crit_damage = 50, speed = 15, strength = 20 WHERE item_id = 'shadow_assassin_helmet';
UPDATE armor_stats SET health = 350, defense = 220, crit_damage = 50, speed = 15, strength = 20 WHERE item_id = 'shadow_assassin_chestplate';
UPDATE armor_stats SET health = 280, defense = 180, crit_damage = 50, speed = 15, strength = 20 WHERE item_id = 'shadow_assassin_leggings';
UPDATE armor_stats SET health = 200, defense = 125, crit_damage = 50, speed = 15, strength = 20 WHERE item_id = 'shadow_assassin_boots';

UPDATE armor_stats SET health = 180, defense = 180, strength = 15, crit_damage = 15, intelligence = 35 WHERE item_id = 'superior_dragon_helmet';
UPDATE armor_stats SET health = 280, defense = 280, strength = 15, crit_damage = 15, intelligence = 35 WHERE item_id = 'superior_dragon_chestplate';
UPDATE armor_stats SET health = 240, defense = 240, strength = 15, crit_damage = 15, intelligence = 35 WHERE item_id = 'superior_dragon_leggings';
UPDATE armor_stats SET health = 150, defense = 150, strength = 15, crit_damage = 15, intelligence = 35 WHERE item_id = 'superior_dragon_boots';

UPDATE armor_stats SET health = 160, defense = 110, strength = 35 WHERE item_id = 'strong_dragon_helmet';
UPDATE armor_stats SET health = 250, defense = 170, strength = 35 WHERE item_id = 'strong_dragon_chestplate';
UPDATE armor_stats SET health = 210, defense = 140, strength = 35 WHERE item_id = 'strong_dragon_leggings';
UPDATE armor_stats SET health = 130, defense = 85, strength = 35 WHERE item_id = 'strong_dragon_boots';

UPDATE armor_stats SET health = 140, defense = 90, speed = 35 WHERE item_id = 'young_dragon_helmet';
UPDATE armor_stats SET health = 220, defense = 140, speed = 35 WHERE item_id = 'young_dragon_chestplate';
UPDATE armor_stats SET health = 180, defense = 120, speed = 35 WHERE item_id = 'young_dragon_leggings';
UPDATE armor_stats SET health = 110, defense = 75, speed = 35 WHERE item_id = 'young_dragon_boots';

UPDATE armor_stats SET health = 85, defense = 120, strength = 5 WHERE item_id = 'hardened_diamond_helmet';
UPDATE armor_stats SET health = 140, defense = 195, strength = 5 WHERE item_id = 'hardened_diamond_chestplate';
UPDATE armor_stats SET health = 120, defense = 165, strength = 5 WHERE item_id = 'hardened_diamond_leggings';
UPDATE armor_stats SET health = 70, defense = 100, strength = 5 WHERE item_id = 'hardened_diamond_boots';

UPDATE weapon_stats SET damage = 1200, strength = 500, intelligence = 700, crit_damage = 200, ability_damage = 200, ferocity = 30 WHERE item_id = 'hyperion';
UPDATE weapon_stats SET damage = 1050, strength = 420, intelligence = 550, crit_damage = 170, ability_damage = 140, ferocity = 20 WHERE item_id = 'valkyrie';
UPDATE weapon_stats SET damage = 1000, strength = 400, intelligence = 500, crit_damage = 160, ability_damage = 120, ferocity = 15 WHERE item_id = 'astraea';
UPDATE weapon_stats SET damage = 950, strength = 380, intelligence = 450, crit_damage = 150, ability_damage = 100 WHERE item_id = 'scylla';

UPDATE weapon_stats SET damage = 750, strength = 320, crit_damage = 120, intelligence = 150, ability_damage = 60 WHERE item_id = 'necron_blade';
UPDATE weapon_stats SET damage = 900, strength = 350, crit_damage = 40, attack_speed = 50, ferocity = 20 WHERE item_id = 'shadow_fury';
UPDATE weapon_stats SET damage = 850, strength = 500, crit_damage = 150 WHERE item_id = 'giants_sword';
UPDATE weapon_stats SET damage = 1100, strength = 400, crit_damage = 180 WHERE item_id = 'dark_claymore';

UPDATE weapon_stats SET damage = 650, strength = 260, intelligence = 250, ability_damage = 40 WHERE item_id = 'reaper_scythe';
UPDATE weapon_stats SET damage = 580, strength = 240 WHERE item_id = 'reaper_sword';
UPDATE weapon_stats SET damage = 600, strength = 250, intelligence = 120 WHERE item_id = 'wither_cloak_sword';

UPDATE weapon_stats SET damage = 420, strength = 200, crit_damage = 50, ability_damage = 30 WHERE item_id = 'aspect_of_the_dragons';
UPDATE weapon_stats SET damage = 500, strength = 220, crit_damage = 100, attack_speed = 110 WHERE item_id = 'livid_dagger';
UPDATE weapon_stats SET damage = 480, strength = 200 WHERE item_id = 'midas_sword';
UPDATE weapon_stats SET damage = 380, strength = 150, intelligence = 100, ability_damage = 20 WHERE item_id = 'yeti_sword';

UPDATE weapon_stats SET damage = 250, strength = 130, crit_damage = 20 WHERE item_id = 'aspect_of_the_end';
UPDATE weapon_stats SET damage = 280, strength = 150, crit_damage = 30 WHERE item_id = 'thick_aspect_of_the_end';

UPDATE weapon_stats SET damage = 20, strength = 5 WHERE item_id = 'wooden_sword';
UPDATE weapon_stats SET damage = 30, strength = 8 WHERE item_id = 'stone_sword';
UPDATE weapon_stats SET damage = 40, strength = 12 WHERE item_id = 'iron_sword';
UPDATE weapon_stats SET damage = 60, strength = 18, crit_damage = 5 WHERE item_id = 'diamond_sword';

UPDATE weapon_stats SET damage = 310, strength = 40, crit_damage = 20, attack_speed = 50, ability_damage = 20 WHERE item_id = 'juju_shortbow';
UPDATE weapon_stats SET damage = 500, strength = 60, crit_damage = 50, attack_speed = 30, ability_damage = 40 WHERE item_id = 'terminator';

INSERT OR REPLACE INTO item_tier_classification (item_id, tier, category) VALUES
('wooden_sword', 'EARLY_GAME', 'WEAPON'),
('stone_sword', 'EARLY_GAME', 'WEAPON'),
('iron_sword', 'EARLY_GAME', 'WEAPON'),
('diamond_sword', 'EARLY_GAME', 'WEAPON'),
('rogue_sword', 'EARLY_GAME', 'WEAPON'),
('spider_sword', 'EARLY_GAME', 'WEAPON'),
('zombie_sword', 'EARLY_GAME', 'WEAPON'),
('fancy_sword', 'MID_GAME', 'WEAPON'),
('hunter_knife', 'MID_GAME', 'WEAPON'),
('end_sword', 'MID_GAME', 'WEAPON'),
('silver_fang', 'MID_GAME', 'WEAPON'),
('shaman_sword', 'MID_GAME', 'WEAPON'),
('raider_axe', 'MID_GAME', 'WEAPON'),
('hyperion', 'END_GAME', 'WEAPON'),
('valkyrie', 'END_GAME', 'WEAPON'),
('astraea', 'END_GAME', 'WEAPON'),
('scylla', 'END_GAME', 'WEAPON'),
('necron_blade', 'END_GAME', 'WEAPON'),
('shadow_fury', 'END_GAME', 'WEAPON'),
('giants_sword', 'END_GAME', 'WEAPON'),
('dark_claymore', 'END_GAME', 'WEAPON'),
('atomsplit_katana', 'END_GAME', 'WEAPON'),
('reaper_scythe', 'END_GAME', 'WEAPON'),
('wither_cloak_sword', 'END_GAME', 'WEAPON'),
('reaper_sword', 'END_GAME', 'WEAPON'),
('aspect_of_the_dragons', 'LATE_GAME', 'WEAPON'),
('livid_dagger', 'LATE_GAME', 'WEAPON'),
('midas_sword', 'LATE_GAME', 'WEAPON'),
('yeti_sword', 'LATE_GAME', 'WEAPON'),
('flower_of_truth', 'LATE_GAME', 'WEAPON'),
('aspect_of_the_end', 'LATE_GAME', 'WEAPON'),
('thick_aspect_of_the_end', 'LATE_GAME', 'WEAPON'),
('juju_shortbow', 'LATE_GAME', 'WEAPON'),
('terminator', 'END_GAME', 'WEAPON'),
('necron_helmet', 'END_GAME', 'ARMOR'),
('necron_chestplate', 'END_GAME', 'ARMOR'),
('necron_leggings', 'END_GAME', 'ARMOR'),
('necron_boots', 'END_GAME', 'ARMOR'),
('goldor_helmet', 'END_GAME', 'ARMOR'),
('goldor_chestplate', 'END_GAME', 'ARMOR'),
('goldor_leggings', 'END_GAME', 'ARMOR'),
('goldor_boots', 'END_GAME', 'ARMOR'),
('shadow_assassin_helmet', 'END_GAME', 'ARMOR'),
('shadow_assassin_chestplate', 'END_GAME', 'ARMOR'),
('shadow_assassin_leggings', 'END_GAME', 'ARMOR'),
('shadow_assassin_boots', 'END_GAME', 'ARMOR'),
('superior_dragon_helmet', 'LATE_GAME', 'ARMOR'),
('superior_dragon_chestplate', 'LATE_GAME', 'ARMOR'),
('superior_dragon_leggings', 'LATE_GAME', 'ARMOR'),
('superior_dragon_boots', 'LATE_GAME', 'ARMOR'),
('strong_dragon_helmet', 'LATE_GAME', 'ARMOR'),
('strong_dragon_chestplate', 'LATE_GAME', 'ARMOR'),
('strong_dragon_leggings', 'LATE_GAME', 'ARMOR'),
('strong_dragon_boots', 'LATE_GAME', 'ARMOR'),
('young_dragon_helmet', 'LATE_GAME', 'ARMOR'),
('young_dragon_chestplate', 'LATE_GAME', 'ARMOR'),
('young_dragon_leggings', 'LATE_GAME', 'ARMOR'),
('young_dragon_boots', 'LATE_GAME', 'ARMOR'),

('wooden_pickaxe', 'EARLY_GAME', 'TOOL'),
('stone_pickaxe', 'EARLY_GAME', 'TOOL'),
('iron_pickaxe', 'MID_GAME', 'TOOL'),
('gold_pickaxe', 'MID_GAME', 'TOOL'),
('diamond_pickaxe', 'MID_GAME', 'TOOL'),
('mithril_pickaxe', 'LATE_GAME', 'TOOL'),
('titanium_pickaxe', 'LATE_GAME', 'TOOL'),
('drill', 'END_GAME', 'TOOL'),

('wooden_axe', 'EARLY_GAME', 'TOOL'),
('stone_axe', 'EARLY_GAME', 'TOOL'),
('iron_axe', 'MID_GAME', 'TOOL'),
('diamond_axe', 'MID_GAME', 'TOOL'),
('jungle_axe', 'LATE_GAME', 'TOOL'),
('raider_axe', 'LATE_GAME', 'TOOL'),
('treecapitator', 'LATE_GAME', 'TOOL'),
('ragnarock_axe', 'END_GAME', 'TOOL'),

('wooden_hoe', 'EARLY_GAME', 'TOOL'),
('stone_hoe', 'EARLY_GAME', 'TOOL'),
('iron_hoe', 'MID_GAME', 'TOOL'),
('diamond_hoe', 'MID_GAME', 'TOOL'),
('blessed_hoe', 'LATE_GAME', 'TOOL'),
('mathematical_hoe', 'END_GAME', 'TOOL'),

('wooden_fishing_rod', 'EARLY_GAME', 'TOOL'),
('fishing_rod', 'EARLY_GAME', 'TOOL'),
('iron_fishing_rod', 'MID_GAME', 'TOOL'),
('prismarine_rod', 'MID_GAME', 'TOOL'),
('diamond_fishing_rod', 'MID_GAME', 'TOOL'),
('rod_of_the_sea', 'LATE_GAME', 'TOOL'),
('sponge_rod', 'LATE_GAME', 'TOOL'),
('rod_of_champions', 'LATE_GAME', 'TOOL'),
('rod_of_legends', 'END_GAME', 'TOOL'),

('juju_shortbow', 'LATE_GAME', 'WEAPON'),
('terminator', 'END_GAME', 'WEAPON');

UPDATE tool_stats SET mining_speed = 5, mining_fortune = 5, breaking_power = 1 WHERE item_id = 'wooden_pickaxe';
UPDATE tool_stats SET mining_speed = 15, mining_fortune = 10, breaking_power = 2 WHERE item_id = 'stone_pickaxe';
UPDATE tool_stats SET mining_speed = 35, mining_fortune = 20, breaking_power = 3 WHERE item_id = 'iron_pickaxe';
UPDATE tool_stats SET mining_speed = 55, mining_fortune = 30, breaking_power = 4 WHERE item_id = 'gold_pickaxe';
UPDATE tool_stats SET mining_speed = 80, mining_fortune = 45, breaking_power = 5 WHERE item_id = 'diamond_pickaxe';
UPDATE tool_stats SET mining_speed = 200, mining_fortune = 120, breaking_power = 7 WHERE item_id = 'mithril_pickaxe';
UPDATE tool_stats SET mining_speed = 350, mining_fortune = 200, breaking_power = 8 WHERE item_id = 'titanium_pickaxe';
UPDATE tool_stats SET mining_speed = 800, mining_fortune = 500, breaking_power = 10 WHERE item_id = 'drill';

UPDATE tool_stats SET foraging_fortune = 5 WHERE item_id = 'wooden_axe';
UPDATE tool_stats SET foraging_fortune = 15 WHERE item_id = 'stone_axe';
UPDATE tool_stats SET foraging_fortune = 30 WHERE item_id = 'iron_axe';
UPDATE tool_stats SET foraging_fortune = 50 WHERE item_id = 'diamond_axe';
UPDATE tool_stats SET foraging_fortune = 120, damage = 40 WHERE item_id = 'jungle_axe';
UPDATE tool_stats SET foraging_fortune = 180, damage = 60 WHERE item_id = 'raider_axe';
UPDATE tool_stats SET foraging_fortune = 250, damage = 80 WHERE item_id = 'treecapitator';
UPDATE tool_stats SET foraging_fortune = 500, damage = 150 WHERE item_id = 'ragnarock_axe';

UPDATE tool_stats SET farming_fortune = 5 WHERE item_id = 'wooden_hoe';
UPDATE tool_stats SET farming_fortune = 15 WHERE item_id = 'stone_hoe';
UPDATE tool_stats SET farming_fortune = 35 WHERE item_id = 'iron_hoe';
UPDATE tool_stats SET farming_fortune = 60 WHERE item_id = 'diamond_hoe';
UPDATE tool_stats SET farming_fortune = 180 WHERE item_id = 'blessed_hoe';
UPDATE tool_stats SET farming_fortune = 450 WHERE item_id = 'mathematical_hoe';

UPDATE tool_stats SET fishing_speed = 5, sea_creature_chance = 1 WHERE item_id = 'wooden_fishing_rod';
UPDATE tool_stats SET fishing_speed = 10, sea_creature_chance = 2 WHERE item_id = 'fishing_rod';
UPDATE tool_stats SET fishing_speed = 25, sea_creature_chance = 4 WHERE item_id = 'iron_fishing_rod';
UPDATE tool_stats SET fishing_speed = 40, sea_creature_chance = 6 WHERE item_id = 'prismarine_rod';
UPDATE tool_stats SET fishing_speed = 60, sea_creature_chance = 8 WHERE item_id = 'diamond_fishing_rod';
UPDATE tool_stats SET fishing_speed = 150, sea_creature_chance = 15 WHERE item_id = 'rod_of_the_sea';
UPDATE tool_stats SET fishing_speed = 200, sea_creature_chance = 20 WHERE item_id = 'sponge_rod';
UPDATE tool_stats SET fishing_speed = 280, sea_creature_chance = 25 WHERE item_id = 'rod_of_champions';
UPDATE tool_stats SET fishing_speed = 500, sea_creature_chance = 40 WHERE item_id = 'rod_of_legends';

UPDATE weapon_stats SET damage = 650, strength = 280, crit_chance = 40, crit_damage = 150, attack_speed = 80 WHERE item_id = 'juju_shortbow';
UPDATE weapon_stats SET damage = 1300, strength = 550, crit_chance = 60, crit_damage = 250, attack_speed = 100, ability_damage = 180, ferocity = 25 WHERE item_id = 'terminator';

UPDATE game_items SET stats = json_set(stats, '$.mining_speed', 5, '$.mining_fortune', 5, '$.breaking_power', 1) WHERE item_id = 'wooden_pickaxe';
UPDATE game_items SET stats = json_set(stats, '$.mining_speed', 15, '$.mining_fortune', 10, '$.breaking_power', 2) WHERE item_id = 'stone_pickaxe';
UPDATE game_items SET stats = json_set(stats, '$.mining_speed', 35, '$.mining_fortune', 20, '$.breaking_power', 3) WHERE item_id = 'iron_pickaxe';
UPDATE game_items SET stats = json_set(stats, '$.mining_speed', 55, '$.mining_fortune', 30, '$.breaking_power', 4) WHERE item_id = 'gold_pickaxe';
UPDATE game_items SET stats = json_set(stats, '$.mining_speed', 80, '$.mining_fortune', 45, '$.breaking_power', 5) WHERE item_id = 'diamond_pickaxe';
UPDATE game_items SET stats = json_set(stats, '$.mining_speed', 200, '$.mining_fortune', 120, '$.breaking_power', 7) WHERE item_id = 'mithril_pickaxe';
UPDATE game_items SET stats = json_set(stats, '$.mining_speed', 350, '$.mining_fortune', 200, '$.breaking_power', 8) WHERE item_id = 'titanium_pickaxe';
UPDATE game_items SET stats = json_set(stats, '$.mining_speed', 800, '$.mining_fortune', 500, '$.breaking_power', 10) WHERE item_id = 'drill';

UPDATE game_items SET stats = json_set(stats, '$.foraging_fortune', 5) WHERE item_id = 'wooden_axe';
UPDATE game_items SET stats = json_set(stats, '$.foraging_fortune', 15) WHERE item_id = 'stone_axe';
UPDATE game_items SET stats = json_set(stats, '$.foraging_fortune', 30) WHERE item_id = 'iron_axe';
UPDATE game_items SET stats = json_set(stats, '$.foraging_fortune', 50) WHERE item_id = 'diamond_axe';
UPDATE game_items SET stats = json_set(stats, '$.foraging_fortune', 120, '$.damage', 40) WHERE item_id = 'jungle_axe';
UPDATE game_items SET stats = json_set(stats, '$.foraging_fortune', 180, '$.damage', 60) WHERE item_id = 'raider_axe';
UPDATE game_items SET stats = json_set(stats, '$.foraging_fortune', 250, '$.damage', 80) WHERE item_id = 'treecapitator';
UPDATE game_items SET stats = json_set(stats, '$.foraging_fortune', 500, '$.damage', 150) WHERE item_id = 'ragnarock_axe';

UPDATE game_items SET stats = json_set(stats, '$.farming_fortune', 5) WHERE item_id = 'wooden_hoe';
UPDATE game_items SET stats = json_set(stats, '$.farming_fortune', 15) WHERE item_id = 'stone_hoe';
UPDATE game_items SET stats = json_set(stats, '$.farming_fortune', 35) WHERE item_id = 'iron_hoe';
UPDATE game_items SET stats = json_set(stats, '$.farming_fortune', 60) WHERE item_id = 'diamond_hoe';
UPDATE game_items SET stats = json_set(stats, '$.farming_fortune', 180) WHERE item_id = 'blessed_hoe';
UPDATE game_items SET stats = json_set(stats, '$.farming_fortune', 450) WHERE item_id = 'mathematical_hoe';

UPDATE game_items SET stats = json_set(stats, '$.fishing_speed', 5, '$.sea_creature_chance', 1) WHERE item_id = 'wooden_fishing_rod';
UPDATE game_items SET stats = json_set(stats, '$.fishing_speed', 10, '$.sea_creature_chance', 2) WHERE item_id = 'fishing_rod';
UPDATE game_items SET stats = json_set(stats, '$.fishing_speed', 25, '$.sea_creature_chance', 4) WHERE item_id = 'iron_fishing_rod';
UPDATE game_items SET stats = json_set(stats, '$.fishing_speed', 40, '$.sea_creature_chance', 6) WHERE item_id = 'prismarine_rod';
UPDATE game_items SET stats = json_set(stats, '$.fishing_speed', 60, '$.sea_creature_chance', 8) WHERE item_id = 'diamond_fishing_rod';
UPDATE game_items SET stats = json_set(stats, '$.fishing_speed', 150, '$.sea_creature_chance', 15) WHERE item_id = 'rod_of_the_sea';
UPDATE game_items SET stats = json_set(stats, '$.fishing_speed', 200, '$.sea_creature_chance', 20) WHERE item_id = 'sponge_rod';
UPDATE game_items SET stats = json_set(stats, '$.fishing_speed', 280, '$.sea_creature_chance', 25) WHERE item_id = 'rod_of_champions';
UPDATE game_items SET stats = json_set(stats, '$.fishing_speed', 500, '$.sea_creature_chance', 40) WHERE item_id = 'rod_of_legends';

UPDATE game_items SET stats = json_set(stats, '$.damage', 650, '$.strength', 280, '$.crit_chance', 40, '$.crit_damage', 150, '$.attack_speed', 80) WHERE item_id = 'juju_shortbow';
UPDATE game_items SET stats = json_set(stats, '$.damage', 1300, '$.strength', 550, '$.crit_chance', 60, '$.crit_damage', 250, '$.attack_speed', 100, '$.ability_damage', 180, '$.ferocity', 25) WHERE item_id = 'terminator';

