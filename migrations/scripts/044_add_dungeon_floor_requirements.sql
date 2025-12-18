CREATE TABLE IF NOT EXISTS dungeon_floor_requirements (
    floor_id TEXT PRIMARY KEY,
    catacombs_level INTEGER NOT NULL,
    gear_score INTEGER NOT NULL
);

INSERT OR IGNORE INTO dungeon_floor_requirements (floor_id, catacombs_level, gear_score) VALUES
('entrance', 0, 0),
('floor1', 5, 50),
('floor2', 8, 100),
('floor3', 10, 150),
('floor4', 13, 250),
('floor5', 16, 400),
('floor6', 19, 600),
('floor7', 22, 900),
('m1', 25, 1200),
('m2', 28, 1500),
('m3', 30, 2000),
('m4', 33, 2500),
('m5', 36, 3000),
('m6', 39, 4000),
('m7', 42, 5000);
