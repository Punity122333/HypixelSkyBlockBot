UPDATE dungeon_floor_requirements SET catacombs_level = 3 WHERE floor_id = 'floor1';
UPDATE dungeon_floor_requirements SET catacombs_level = 5 WHERE floor_id = 'floor2';
UPDATE dungeon_floor_requirements SET catacombs_level = 7 WHERE floor_id = 'floor3';
UPDATE dungeon_floor_requirements SET catacombs_level = 9 WHERE floor_id = 'floor4';
UPDATE dungeon_floor_requirements SET catacombs_level = 11 WHERE floor_id = 'floor5';
UPDATE dungeon_floor_requirements SET catacombs_level = 13 WHERE floor_id = 'floor6';
UPDATE dungeon_floor_requirements SET catacombs_level = 15 WHERE floor_id = 'floor7';
UPDATE dungeon_floor_requirements SET catacombs_level = 18 WHERE floor_id = 'm1';
UPDATE dungeon_floor_requirements SET catacombs_level = 20 WHERE floor_id = 'm2';
UPDATE dungeon_floor_requirements SET catacombs_level = 22 WHERE floor_id = 'm3';
UPDATE dungeon_floor_requirements SET catacombs_level = 24 WHERE floor_id = 'm4';
UPDATE dungeon_floor_requirements SET catacombs_level = 26 WHERE floor_id = 'm5';
UPDATE dungeon_floor_requirements SET catacombs_level = 28 WHERE floor_id = 'm6';
UPDATE dungeon_floor_requirements SET catacombs_level = 30 WHERE floor_id = 'm7';

UPDATE dungeon_unlocks SET min_level = 3 WHERE floor_id = 'floor1';
UPDATE dungeon_unlocks SET min_level = 5 WHERE floor_id = 'floor2';
UPDATE dungeon_unlocks SET min_level = 7 WHERE floor_id = 'floor3';
UPDATE dungeon_unlocks SET min_level = 9 WHERE floor_id = 'floor4';
UPDATE dungeon_unlocks SET min_level = 11 WHERE floor_id = 'floor5';
UPDATE dungeon_unlocks SET min_level = 13 WHERE floor_id = 'floor6';
UPDATE dungeon_unlocks SET min_level = 15 WHERE floor_id = 'floor7';
UPDATE dungeon_unlocks SET min_level = 18 WHERE floor_id = 'm1';
UPDATE dungeon_unlocks SET min_level = 20 WHERE floor_id = 'm2';
UPDATE dungeon_unlocks SET min_level = 22 WHERE floor_id = 'm3';
UPDATE dungeon_unlocks SET min_level = 24 WHERE floor_id = 'm4';
UPDATE dungeon_unlocks SET min_level = 26 WHERE floor_id = 'm5';
UPDATE dungeon_unlocks SET min_level = 28 WHERE floor_id = 'm6';
UPDATE dungeon_unlocks SET min_level = 30 WHERE floor_id = 'm7';

INSERT OR IGNORE INTO combat_drop_xp (item_id, base_xp) VALUES
('wither_essence', 100),
('undead_essence', 80),
('bonzo_staff_fragment', 500),
('scarf_fragment', 600),
('professor_fragment', 700),
('spirit_bone', 800),
('livid_dagger', 2000),
('shadow_fury', 3000),
('giant_sword', 4000),
('necromancer_lord_armor_piece', 1500),
('necron_blade', 5000),
('wither_armor_piece', 2500),
('master_star', 3500),
('claymore', 6000),
('hyperion', 10000),
('skeleton_master_boots', 200),
('skeleton_master_helmet', 300),
('adaptive_helmet', 350),
('adaptive_chestplate', 400),
('zombie_soldier_helmet', 250),
('zombie_soldier_chestplate', 300),
('zombie_knight_helmet', 350),
('skeleton_master_chestplate', 350),
('shadow_assassin_helmet', 800),
('shadow_assassin_chestplate', 900),
('fancy_sword', 600),
('necron_helmet', 1200),
('zombie_lord_helmet', 700),
('necron_chestplate', 1300),
('necron_leggings', 1300),
('necron_boots', 1300),
('astraea', 8000),
('scylla', 8000),
('valkyrie', 8000),
('giants_sword', 5000),
('terminator', 9000),
('wither_blood', 800),
('dark_orb', 1000),
('soul_fragment', 600),
('necromancer_brooch', 1200),
('golden_dragon_fragment', 2000),
('superior_dragon_fragment', 1500),
('wise_dragon_fragment', 800),
('strong_dragon_fragment', 1000),
('young_dragon_fragment', 900),
ON CONFLICT(item_id) DO UPDATE SET base_xp = excluded.base_xp;
