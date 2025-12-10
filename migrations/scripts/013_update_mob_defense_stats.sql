UPDATE mob_stats SET defense = 5 WHERE mob_id = 'zombie';
UPDATE mob_stats SET defense = 8 WHERE mob_id = 'skeleton';
UPDATE mob_stats SET defense = 3 WHERE mob_id = 'spider';
UPDATE mob_stats SET defense = 0 WHERE mob_id = 'creeper';
UPDATE mob_stats SET defense = 25 WHERE mob_id = 'enderman';
UPDATE mob_stats SET defense = 0 WHERE mob_id = 'slime';
UPDATE mob_stats SET defense = 5 WHERE mob_id = 'cave_spider';
UPDATE mob_stats SET defense = 30 WHERE mob_id = 'zombie_pigman';
UPDATE mob_stats SET defense = 15 WHERE mob_id = 'blaze';
UPDATE mob_stats SET defense = 20 WHERE mob_id = 'wither_skeleton';
UPDATE mob_stats SET defense = 0 WHERE mob_id = 'ghast';
UPDATE mob_stats SET defense = 40 WHERE mob_id = 'magma_cube';
UPDATE mob_stats SET defense = 12 WHERE mob_id = 'silverfish';
UPDATE mob_stats SET defense = 50 WHERE mob_id = 'ender_dragon';
UPDATE mob_stats SET defense = 60 WHERE mob_id = 'wither';
UPDATE mob_stats SET defense = 2 WHERE mob_id = 'chicken';
UPDATE mob_stats SET defense = 4 WHERE mob_id = 'sheep';
UPDATE mob_stats SET defense = 3 WHERE mob_id = 'pig';
UPDATE mob_stats SET defense = 6 WHERE mob_id = 'cow';
UPDATE mob_stats SET defense = 10 WHERE mob_id = 'wolf';
UPDATE mob_stats SET defense = 5 WHERE mob_id = 'ocelot';
UPDATE mob_stats SET defense = 45 WHERE mob_id = 'iron_golem';

INSERT OR IGNORE INTO mob_stats (mob_id, defense, crit_chance, crit_damage) VALUES
('emerald_slime', 8, 0, 0),
('sea_guardian', 20, 5, 20),
('sea_witch', 15, 10, 30),
('night_squid', 12, 0, 0),
('revenant', 35, 10, 40),
('tarantula', 28, 15, 50),
('sven', 40, 12, 45),
('voidgloom', 55, 20, 60),
('inferno', 70, 25, 75);
