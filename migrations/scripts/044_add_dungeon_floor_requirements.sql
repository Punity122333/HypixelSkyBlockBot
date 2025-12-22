CREATE TABLE IF NOT EXISTS dungeon_floor_requirements (
    floor_id TEXT PRIMARY KEY,
    catacombs_level INTEGER NOT NULL,
    gear_score INTEGER NOT NULL
);

INSERT OR IGNORE INTO dungeon_floor_requirements (floor_id, catacombs_level, gear_score) VALUES
('entrance', 0, 0),
('floor1', 3, 50),
('floor2', 5, 100),
('floor3', 7, 150),
('floor4', 9, 250),
('floor5', 11, 400),
('floor6', 13, 600),
('floor7', 15, 900),
('m1', 18, 1200),
('m2', 20, 1500),
('m3', 22, 2000),
('m4', 24, 2500),
('m5', 26, 3000),
('m6', 28, 4000),
('m7', 30, 5000);
