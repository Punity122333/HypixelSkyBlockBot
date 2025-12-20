CREATE TABLE IF NOT EXISTS weapon_tiers (
    tier TEXT PRIMARY KEY,
    tier_level INTEGER NOT NULL,
    base_damage_multiplier REAL DEFAULT 1.0,
    stat_multiplier REAL DEFAULT 1.0
);

INSERT OR REPLACE INTO weapon_tiers (tier, tier_level, base_damage_multiplier, stat_multiplier) VALUES
('EARLY_GAME', 1, 1.0, 1.0),
('MID_GAME', 2, 2.5, 1.8),
('LATE_GAME', 3, 5.0, 3.0),
('END_GAME', 4, 10.0, 5.0);

UPDATE game_items SET stats = json_set(stats, '$.damage', 20) WHERE item_id = 'wooden_sword';
UPDATE game_items SET stats = json_set(stats, '$.damage', 30) WHERE item_id = 'stone_sword';
UPDATE game_items SET stats = json_set(stats, '$.damage', 45) WHERE item_id = 'gold_sword';
UPDATE game_items SET stats = json_set(stats, '$.damage', 50) WHERE item_id = 'iron_sword';
UPDATE game_items SET stats = json_set(stats, '$.damage', 70) WHERE item_id = 'diamond_sword';

UPDATE game_items SET stats = json_set(stats, '$.damage', 55, '$.strength', 10) WHERE item_id = 'rogue_sword';
UPDATE game_items SET stats = json_set(stats, '$.damage', 65, '$.strength', 15) WHERE item_id = 'undead_sword';
UPDATE game_items SET stats = json_set(stats, '$.damage', 75, '$.strength', 20) WHERE item_id = 'spider_sword';
UPDATE game_items SET stats = json_set(stats, '$.damage', 85, '$.strength', 25) WHERE item_id = 'zombie_sword';
UPDATE game_items SET stats = json_set(stats, '$.damage', 80, '$.strength', 18) WHERE item_id = 'prismarine_blade';

UPDATE game_items SET stats = json_set(stats, '$.damage', 90, '$.strength', 35, '$.speed', 25) WHERE item_id = 'rogue_sword';

UPDATE game_items SET stats = json_set(stats, '$.damage', 10, '$.strength', 5, '$.crit_damage', 10) WHERE item_id = 'aspect_of_the_jerry';

UPDATE game_items SET stats = json_set(stats, '$.damage', 95, '$.strength', 40, '$.intelligence', 20) WHERE item_id = 'fancy_sword';
UPDATE game_items SET stats = json_set(stats, '$.damage', 100, '$.strength', 30) WHERE item_id = 'flaming_sword';
UPDATE game_items SET stats = json_set(stats, '$.damage', 105, '$.strength', 45) WHERE item_id = 'hunter_knife';
UPDATE game_items SET stats = json_set(stats, '$.damage', 110, '$.strength', 50) WHERE item_id = 'cleaver';

UPDATE game_items SET stats = json_set(stats, '$.damage', 125, '$.strength', 60) WHERE item_id = 'end_sword';
UPDATE game_items SET stats = json_set(stats, '$.damage', 130, '$.strength', 55) WHERE item_id = 'ender_sword';
UPDATE game_items SET stats = json_set(stats, '$.damage', 140, '$.strength', 65) WHERE item_id = 'golem_sword';
UPDATE game_items SET stats = json_set(stats, '$.damage', 145, '$.strength', 70) WHERE item_id = 'emerald_blade';
UPDATE game_items SET stats = json_set(stats, '$.damage', 150, '$.strength', 60) WHERE item_id = 'ornate_zombie_sword';

UPDATE game_items SET stats = json_set(stats, '$.damage', 170, '$.strength', 80, '$.crit_chance', 15) WHERE item_id = 'silver_fang';
UPDATE game_items SET stats = json_set(stats, '$.damage', 180, '$.strength', 85) WHERE item_id = 'shaman_sword';
UPDATE game_items SET stats = json_set(stats, '$.damage', 190, '$.strength', 90, '$.crit_damage', 35) WHERE item_id = 'ember_rod';

UPDATE game_items SET stats = json_set(stats, '$.damage', 200, '$.strength', 100, '$.crit_damage', 50, '$.intelligence', 30) WHERE item_id = 'frozen_scythe';
UPDATE game_items SET stats = json_set(stats, '$.damage', 220, '$.strength', 110) WHERE item_id = 'crimson_blade';

UPDATE game_items SET stats = json_set(stats, '$.damage', 250, '$.strength', 130) WHERE item_id = 'aspect_of_the_end';
UPDATE game_items SET stats = json_set(stats, '$.damage', 280, '$.strength', 150, '$.crit_damage', 30) WHERE item_id = 'thick_aspect_of_the_end';

UPDATE game_items SET stats = json_set(stats, '$.damage', 240, '$.strength', 120, '$.crit_damage', 25) WHERE item_id = 'thick_scorpion_foil';
UPDATE game_items SET stats = json_set(stats, '$.damage', 260, '$.strength', 140, '$.intelligence', 60) WHERE item_id = 'tacticians_sword';

UPDATE game_items SET stats = json_set(stats, '$.damage', 320, '$.strength', 150, '$.intelligence', 70) WHERE item_id = 'aurora_sword';
UPDATE game_items SET stats = json_set(stats, '$.damage', 340, '$.strength', 160, '$.crit_chance', 20) WHERE item_id = 'void_sword';
UPDATE game_items SET stats = json_set(stats, '$.damage', 360, '$.strength', 170, '$.crit_damage', 50) WHERE item_id = 'flower_of_truth';

UPDATE game_items SET stats = json_set(stats, '$.damage', 380, '$.strength', 150, '$.intelligence', 100) WHERE item_id = 'yeti_sword';

UPDATE game_items SET stats = json_set(stats, '$.damage', 420, '$.strength', 190, '$.crit_damage', 85, '$.ferocity', 30) WHERE item_id = 'molten_edge';

UPDATE game_items SET stats = json_set(stats, '$.damage', 440, '$.strength', 180, '$.crit_damage', 60) WHERE item_id = 'fabled_sword';

UPDATE game_items SET stats = json_set(stats, '$.damage', 480, '$.strength', 200) WHERE item_id = 'midas_sword';

UPDATE game_items SET stats = json_set(stats, '$.damage', 500, '$.strength', 220, '$.crit_damage', 100, '$.attack_speed', 110) WHERE item_id = 'livid_dagger';

UPDATE game_items SET stats = json_set(stats, '$.damage', 520, '$.strength', 210, '$.crit_damage', 90, '$.crit_chance', 25, '$.attack_speed', 20) WHERE item_id = 'voidwalker_katana';

UPDATE game_items SET stats = json_set(stats, '$.damage', 550, '$.strength', 200, '$.crit_damage', 120, '$.intelligence', 40) WHERE item_id = 'glacial_scythe';

UPDATE game_items SET stats = json_set(stats, '$.damage', 420, '$.strength', 200, '$.crit_damage', 50) WHERE item_id = 'aspect_of_the_dragons';

UPDATE game_items SET stats = json_set(stats, '$.damage', 580, '$.strength', 240) WHERE item_id = 'reaper_sword';

UPDATE game_items SET stats = json_set(stats, '$.damage', 600, '$.strength', 250, '$.intelligence', 120) WHERE item_id = 'wither_cloak_sword';

UPDATE game_items SET stats = json_set(stats, '$.damage', 650, '$.strength', 260, '$.intelligence', 250) WHERE item_id = 'reaper_scythe';

UPDATE game_items SET stats = json_set(stats, '$.damage', 700, '$.strength', 300, '$.crit_damage', 100) WHERE item_id = 'atomsplit_katana';

UPDATE game_items SET stats = json_set(stats, '$.damage', 750, '$.strength', 320, '$.crit_damage', 120) WHERE item_id = 'necron_blade';

UPDATE game_items SET stats = json_set(stats, '$.damage', 900, '$.strength', 350, '$.crit_damage', 40) WHERE item_id = 'shadow_fury';

UPDATE game_items SET stats = json_set(stats, '$.damage', 850, '$.strength', 500, '$.crit_damage', 150) WHERE item_id = 'giants_sword';

UPDATE game_items SET stats = json_set(stats, '$.damage', 1100, '$.strength', 400, '$.crit_damage', 180) WHERE item_id = 'dark_claymore';

UPDATE game_items SET stats = json_set(stats, '$.damage', 950, '$.strength', 380, '$.intelligence', 450, '$.crit_damage', 150, '$.ability_damage', 100) WHERE item_id = 'scylla';

UPDATE game_items SET stats = json_set(stats, '$.damage', 1000, '$.strength', 400, '$.intelligence', 500, '$.crit_damage', 160, '$.ability_damage', 120, '$.ferocity', 15) WHERE item_id = 'astraea';

UPDATE game_items SET stats = json_set(stats, '$.damage', 1050, '$.strength', 420, '$.intelligence', 550, '$.crit_damage', 170, '$.ability_damage', 140, '$.ferocity', 20) WHERE item_id = 'valkyrie';

UPDATE game_items SET stats = json_set(stats, '$.damage', 1200, '$.strength', 500, '$.intelligence', 700, '$.crit_damage', 200, '$.ability_damage', 200, '$.ferocity', 30) WHERE item_id = 'hyperion';

UPDATE game_items SET stats = json_set(stats, '$.damage', 25, '$.defense', 8, '$.health', 15) WHERE item_id = 'leather_helmet';
UPDATE game_items SET stats = json_set(stats, '$.damage', 30, '$.defense', 15, '$.health', 25) WHERE item_id = 'leather_chestplate';
UPDATE game_items SET stats = json_set(stats, '$.damage', 28, '$.defense', 12, '$.health', 20) WHERE item_id = 'leather_leggings';
UPDATE game_items SET stats = json_set(stats, '$.damage', 22, '$.defense', 7, '$.health', 12) WHERE item_id = 'leather_boots';

UPDATE game_items SET stats = json_set(stats, '$.defense', 20, '$.health', 30) WHERE item_id = 'chainmail_helmet';
UPDATE game_items SET stats = json_set(stats, '$.defense', 35, '$.health', 50) WHERE item_id = 'chainmail_chestplate';
UPDATE game_items SET stats = json_set(stats, '$.defense', 28, '$.health', 40) WHERE item_id = 'chainmail_leggings';
UPDATE game_items SET stats = json_set(stats, '$.defense', 18, '$.health', 25) WHERE item_id = 'chainmail_boots';

UPDATE game_items SET stats = json_set(stats, '$.defense', 35, '$.health', 45) WHERE item_id = 'iron_helmet';
UPDATE game_items SET stats = json_set(stats, '$.defense', 60, '$.health', 75) WHERE item_id = 'iron_chestplate';
UPDATE game_items SET stats = json_set(stats, '$.defense', 50, '$.health', 60) WHERE item_id = 'iron_leggings';

UPDATE game_items SET stats = json_set(stats, '$.defense', 75, '$.health', 90) WHERE item_id = 'sponge_helmet';
UPDATE game_items SET stats = json_set(stats, '$.defense', 120, '$.health', 150) WHERE item_id = 'sponge_chestplate';
UPDATE game_items SET stats = json_set(stats, '$.defense', 100, '$.health', 125) WHERE item_id = 'sponge_leggings';
UPDATE game_items SET stats = json_set(stats, '$.defense', 65, '$.health', 80) WHERE item_id = 'sponge_boots';

UPDATE game_items SET stats = json_set(stats, '$.defense', 140, '$.health', 100) WHERE item_id = 'hardened_diamond_helmet';

UPDATE game_items SET stats = json_set(stats, '$.defense', 120, '$.health', 160, '$.strength', 30) WHERE item_id = 'dragon_leggings';
UPDATE game_items SET stats = json_set(stats, '$.defense', 95, '$.health', 105, '$.strength', 20) WHERE item_id = 'dragon_boots';

UPDATE game_items SET stats = json_set(stats, '$.health', 170, '$.defense', 120, '$.strength', 35) WHERE item_id = 'strong_dragon_helmet';
UPDATE game_items SET stats = json_set(stats, '$.health', 170, '$.defense', 120, '$.speed', 30) WHERE item_id = 'young_dragon_helmet';

UPDATE game_items SET stats = json_set(stats, '$.health', 180, '$.defense', 140, '$.crit_damage', 50, '$.speed', 15) WHERE item_id = 'shadow_assassin_helmet';
UPDATE game_items SET stats = json_set(stats, '$.health', 350, '$.defense', 220, '$.crit_damage', 50, '$.speed', 15) WHERE item_id = 'shadow_assassin_chestplate';
UPDATE game_items SET stats = json_set(stats, '$.health', 280, '$.defense', 180, '$.crit_damage', 50, '$.speed', 15) WHERE item_id = 'shadow_assassin_leggings';
UPDATE game_items SET stats = json_set(stats, '$.health', 200, '$.defense', 125, '$.crit_damage', 50, '$.speed', 15) WHERE item_id = 'shadow_assassin_boots';

UPDATE game_items SET stats = json_set(stats, '$.health', 200, '$.defense', 180, '$.strength', 50, '$.crit_damage', 35) WHERE item_id = 'goldor_helmet';
UPDATE game_items SET stats = json_set(stats, '$.health', 400, '$.defense', 300, '$.strength', 50, '$.crit_damage', 35) WHERE item_id = 'goldor_chestplate';
UPDATE game_items SET stats = json_set(stats, '$.health', 330, '$.defense', 240, '$.strength', 50, '$.crit_damage', 35) WHERE item_id = 'goldor_leggings';
UPDATE game_items SET stats = json_set(stats, '$.health', 220, '$.defense', 160, '$.strength', 50, '$.crit_damage', 35) WHERE item_id = 'goldor_boots';

UPDATE game_items SET stats = json_set(stats, '$.health', 200, '$.defense', 180, '$.strength', 60, '$.crit_damage', 45, '$.intelligence', 40) WHERE item_id = 'necron_helmet';
UPDATE game_items SET stats = json_set(stats, '$.health', 420, '$.defense', 320, '$.strength', 60, '$.crit_damage', 45, '$.intelligence', 40) WHERE item_id = 'necron_chestplate';
UPDATE game_items SET stats = json_set(stats, '$.health', 350, '$.defense', 260, '$.strength', 60, '$.crit_damage', 45, '$.intelligence', 40) WHERE item_id = 'necron_leggings';
UPDATE game_items SET stats = json_set(stats, '$.health', 230, '$.defense', 170, '$.strength', 60, '$.crit_damage', 45, '$.intelligence', 40) WHERE item_id = 'necron_boots';

UPDATE game_items SET stats = json_set(stats, '$.health', 50, '$.defense', 25, '$.strength', 10, '$.crit_damage', 10) WHERE item_id = 'necromancer_lord_helmet';
UPDATE game_items SET stats = json_set(stats, '$.health', 80, '$.defense', 40, '$.strength', 10, '$.crit_damage', 10) WHERE item_id = 'necromancer_lord_chestplate';
UPDATE game_items SET stats = json_set(stats, '$.health', 65, '$.defense', 35, '$.strength', 10, '$.crit_damage', 10) WHERE item_id = 'necromancer_lord_leggings';
UPDATE game_items SET stats = json_set(stats, '$.health', 45, '$.defense', 25, '$.strength', 10, '$.crit_damage', 10) WHERE item_id = 'necromancer_lord_boots';

UPDATE game_items SET stats = json_set(stats, '$.health', 60, '$.defense', 30, '$.strength', 15, '$.intelligence', 15) WHERE item_id = 'wither_helmet';
UPDATE game_items SET stats = json_set(stats, '$.health', 100, '$.defense', 50, '$.strength', 15, '$.intelligence', 15) WHERE item_id = 'wither_chestplate';
UPDATE game_items SET stats = json_set(stats, '$.health', 80, '$.defense', 40, '$.strength', 15, '$.intelligence', 15) WHERE item_id = 'wither_leggings';
UPDATE game_items SET stats = json_set(stats, '$.health', 55, '$.defense', 28, '$.strength', 15, '$.intelligence', 15) WHERE item_id = 'wither_boots';

UPDATE game_items SET item_type = 'HELMET' WHERE item_id IN ('necromancer_lord_helmet', 'wither_helmet');
UPDATE game_items SET item_type = 'CHESTPLATE' WHERE item_id IN ('necromancer_lord_chestplate', 'wither_chestplate');
UPDATE game_items SET item_type = 'LEGGINGS' WHERE item_id IN ('necromancer_lord_leggings', 'wither_leggings');
UPDATE game_items SET item_type = 'BOOTS' WHERE item_id IN ('necromancer_lord_boots', 'wither_boots');

UPDATE game_items SET stats = json_set(stats, '$.mining_speed', 80, '$.breaking_power', 3) WHERE item_id = 'wooden_pickaxe';
UPDATE game_items SET stats = json_set(stats, '$.mining_speed', 120, '$.breaking_power', 4) WHERE item_id = 'stone_pickaxe';
UPDATE game_items SET stats = json_set(stats, '$.mining_speed', 180, '$.breaking_power', 5) WHERE item_id = 'iron_pickaxe';
UPDATE game_items SET stats = json_set(stats, '$.mining_speed', 250, '$.breaking_power', 6, '$.mining_fortune', 10) WHERE item_id = 'gold_pickaxe';
UPDATE game_items SET stats = json_set(stats, '$.mining_speed', 350, '$.breaking_power', 7, '$.mining_fortune', 20) WHERE item_id = 'diamond_pickaxe';

UPDATE game_items SET stats = json_set(stats, '$.mining_speed', 100, '$.breaking_power', 4, '$.mining_fortune', 5) WHERE item_id = 'wooden_axe';
UPDATE game_items SET stats = json_set(stats, '$.mining_speed', 150, '$.breaking_power', 5, '$.foraging_fortune', 8) WHERE item_id = 'stone_axe';
UPDATE game_items SET stats = json_set(stats, '$.mining_speed', 220, '$.breaking_power', 6, '$.foraging_fortune', 12) WHERE item_id = 'iron_axe';
UPDATE game_items SET stats = json_set(stats, '$.mining_speed', 320, '$.breaking_power', 7, '$.foraging_fortune', 18) WHERE item_id = 'diamond_axe';

UPDATE game_items SET stats = json_set(stats, '$.farming_fortune', 10, '$.crop_yield_multiplier', 1.1) WHERE item_id = 'wooden_hoe';
UPDATE game_items SET stats = json_set(stats, '$.farming_fortune', 15, '$.crop_yield_multiplier', 1.15) WHERE item_id = 'stone_hoe';
UPDATE game_items SET stats = json_set(stats, '$.farming_fortune', 22, '$.crop_yield_multiplier', 1.22) WHERE item_id = 'iron_hoe';
UPDATE game_items SET stats = json_set(stats, '$.farming_fortune', 32, '$.crop_yield_multiplier', 1.32) WHERE item_id = 'diamond_hoe';

UPDATE game_items SET stats = json_set(stats, '$.sea_creature_chance', 5, '$.fishing_speed', 10) WHERE item_id = 'fishing_rod';

CREATE TABLE IF NOT EXISTS item_tier_classification (
    item_id TEXT PRIMARY KEY,
    tier TEXT NOT NULL,
    category TEXT NOT NULL,
    FOREIGN KEY (tier) REFERENCES weapon_tiers(tier)
);

INSERT OR REPLACE INTO item_tier_classification (item_id, tier, category) VALUES
('wooden_sword', 'EARLY_GAME', 'WEAPON'),
('stone_sword', 'EARLY_GAME', 'WEAPON'),
('gold_sword', 'EARLY_GAME', 'WEAPON'),
('iron_sword', 'EARLY_GAME', 'WEAPON'),
('diamond_sword', 'EARLY_GAME', 'WEAPON'),
('rogue_sword', 'EARLY_GAME', 'WEAPON'),
('undead_sword', 'EARLY_GAME', 'WEAPON'),
('spider_sword', 'EARLY_GAME', 'WEAPON'),
('zombie_sword', 'EARLY_GAME', 'WEAPON'),
('aspect_of_the_jerry', 'EARLY_GAME', 'WEAPON'),
('fancy_sword', 'MID_GAME', 'WEAPON'),
('flaming_sword', 'MID_GAME', 'WEAPON'),
('hunter_knife', 'MID_GAME', 'WEAPON'),
('cleaver', 'MID_GAME', 'WEAPON'),
('end_sword', 'MID_GAME', 'WEAPON'),
('ender_sword', 'MID_GAME', 'WEAPON'),
('golem_sword', 'MID_GAME', 'WEAPON'),
('emerald_blade', 'MID_GAME', 'WEAPON'),
('silver_fang', 'MID_GAME', 'WEAPON'),
('shaman_sword', 'MID_GAME', 'WEAPON'),
('ember_rod', 'MID_GAME', 'WEAPON'),
('frozen_scythe', 'MID_GAME', 'WEAPON'),
('crimson_blade', 'MID_GAME', 'WEAPON'),
('aspect_of_the_end', 'LATE_GAME', 'WEAPON'),
('thick_aspect_of_the_end', 'LATE_GAME', 'WEAPON'),
('tacticians_sword', 'LATE_GAME', 'WEAPON'),
('aurora_sword', 'LATE_GAME', 'WEAPON'),
('void_sword', 'LATE_GAME', 'WEAPON'),
('flower_of_truth', 'LATE_GAME', 'WEAPON'),
('yeti_sword', 'LATE_GAME', 'WEAPON'),
('molten_edge', 'LATE_GAME', 'WEAPON'),
('fabled_sword', 'LATE_GAME', 'WEAPON'),
('midas_sword', 'LATE_GAME', 'WEAPON'),
('livid_dagger', 'LATE_GAME', 'WEAPON'),
('voidwalker_katana', 'LATE_GAME', 'WEAPON'),
('glacial_scythe', 'LATE_GAME', 'WEAPON'),
('aspect_of_the_dragons', 'LATE_GAME', 'WEAPON'),
('reaper_sword', 'END_GAME', 'WEAPON'),
('wither_cloak_sword', 'END_GAME', 'WEAPON'),
('reaper_scythe', 'END_GAME', 'WEAPON'),
('atomsplit_katana', 'END_GAME', 'WEAPON'),
('necron_blade', 'END_GAME', 'WEAPON'),
('shadow_fury', 'END_GAME', 'WEAPON'),
('giants_sword', 'END_GAME', 'WEAPON'),
('dark_claymore', 'END_GAME', 'WEAPON'),
('scylla', 'END_GAME', 'WEAPON'),
('astraea', 'END_GAME', 'WEAPON'),
('valkyrie', 'END_GAME', 'WEAPON'),
('hyperion', 'END_GAME', 'WEAPON'),
('leather_helmet', 'EARLY_GAME', 'ARMOR'),
('leather_chestplate', 'EARLY_GAME', 'ARMOR'),
('leather_leggings', 'EARLY_GAME', 'ARMOR'),
('leather_boots', 'EARLY_GAME', 'ARMOR'),
('chainmail_helmet', 'EARLY_GAME', 'ARMOR'),
('chainmail_chestplate', 'EARLY_GAME', 'ARMOR'),
('chainmail_leggings', 'EARLY_GAME', 'ARMOR'),
('chainmail_boots', 'EARLY_GAME', 'ARMOR'),
('iron_helmet', 'MID_GAME', 'ARMOR'),
('iron_chestplate', 'MID_GAME', 'ARMOR'),
('iron_leggings', 'MID_GAME', 'ARMOR'),
('sponge_helmet', 'MID_GAME', 'ARMOR'),
('sponge_chestplate', 'MID_GAME', 'ARMOR'),
('sponge_leggings', 'MID_GAME', 'ARMOR'),
('sponge_boots', 'MID_GAME', 'ARMOR'),
('hardened_diamond_helmet', 'MID_GAME', 'ARMOR'),
('dragon_leggings', 'LATE_GAME', 'ARMOR'),
('dragon_boots', 'LATE_GAME', 'ARMOR'),
('strong_dragon_helmet', 'LATE_GAME', 'ARMOR'),
('young_dragon_helmet', 'LATE_GAME', 'ARMOR'),
('shadow_assassin_helmet', 'END_GAME', 'ARMOR'),
('shadow_assassin_chestplate', 'END_GAME', 'ARMOR'),
('shadow_assassin_leggings', 'END_GAME', 'ARMOR'),
('shadow_assassin_boots', 'END_GAME', 'ARMOR'),
('goldor_helmet', 'END_GAME', 'ARMOR'),
('goldor_chestplate', 'END_GAME', 'ARMOR'),
('goldor_leggings', 'END_GAME', 'ARMOR'),
('goldor_boots', 'END_GAME', 'ARMOR'),
('necron_helmet', 'END_GAME', 'ARMOR'),
('necron_chestplate', 'END_GAME', 'ARMOR'),
('necron_leggings', 'END_GAME', 'ARMOR'),
('necron_boots', 'END_GAME', 'ARMOR');
