CREATE TABLE IF NOT EXISTS mob_stats (
    mob_id TEXT PRIMARY KEY,
    defense INTEGER DEFAULT 0,
    crit_chance INTEGER DEFAULT 0,
    crit_damage INTEGER DEFAULT 0,
    speed INTEGER DEFAULT 100,
    special_abilities TEXT DEFAULT '[]'
);

CREATE INDEX IF NOT EXISTS idx_mob_stats_mob_id ON mob_stats(mob_id);

ALTER TABLE mob_locations ADD COLUMN defense INTEGER DEFAULT 0;

INSERT OR REPLACE INTO mob_stats (mob_id, defense, crit_chance, crit_damage) VALUES
('zombie', 5, 0, 0),
('skeleton', 3, 10, 25),
('spider', 2, 5, 15),
('creeper', 0, 0, 0),
('enderman', 15, 15, 50),
('slime', 0, 0, 0),
('cave_spider', 5, 8, 20),
('zombie_pigman', 20, 5, 30),
('blaze', 10, 12, 40),
('ghast', 8, 10, 35),
('magma_cube', 15, 0, 0),
('wither_skeleton', 25, 15, 60),
('zealot', 40, 20, 80),
('ender_dragon', 200, 25, 100),
('piglin_brute', 30, 10, 45),
('wither', 300, 30, 150),
('lapis_zombie', 8, 0, 0),
('redstone_pigman', 12, 8, 25),
('emerald_slime', 10, 0, 0),
('strong_dragon', 250, 30, 120),
('old_dragon', 180, 20, 90),
('young_dragon', 150, 25, 110),
('superior_dragon', 300, 35, 150),
('wolf', 5, 15, 40),
('mushroom_cow', 3, 0, 0),
('chicken', 0, 0, 0),
('sheep', 2, 0, 0),
('pig', 1, 0, 0);

UPDATE mob_locations SET defense = (SELECT defense FROM mob_stats WHERE mob_stats.mob_id = mob_locations.mob_id) WHERE mob_id IN (SELECT mob_id FROM mob_stats);
