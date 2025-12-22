ALTER TABLE weapon_stats ADD COLUMN intelligence INTEGER DEFAULT 0;

UPDATE weapon_stats SET intelligence = 350 WHERE item_id = 'hyperion';
UPDATE weapon_stats SET intelligence = 100 WHERE item_id = 'astraea';
UPDATE weapon_stats SET intelligence = 100 WHERE item_id = 'scylla';
UPDATE weapon_stats SET intelligence = 100 WHERE item_id = 'valkyrie';

INSERT OR IGNORE INTO weapon_stats (item_id, damage, strength, crit_chance, crit_damage, attack_speed, intelligence, ability_damage, ferocity) VALUES
('hyperion', 260, 150, 0, 100, 0, 350, 75, 10),
('astraea', 270, 130, 0, 85, 0, 100, 70, 10),
('scylla', 280, 140, 0, 90, 0, 100, 70, 10),
('valkyrie', 290, 135, 0, 95, 0, 100, 70, 10)
ON CONFLICT(item_id) DO UPDATE SET 
    intelligence = excluded.intelligence;
