CREATE TABLE IF NOT EXISTS dungeon_floor_difficulty (
    floor_id TEXT PRIMARY KEY,
    difficulty INTEGER NOT NULL
);

INSERT OR IGNORE INTO dungeon_floor_difficulty (floor_id, difficulty) VALUES
('entrance', 1),
('floor1', 2),
('floor2', 3),
('floor3', 5),
('floor4', 7),
('floor5', 10),
('floor6', 15),
('floor7', 20),
('m1', 25),
('m2', 30),
('m3', 40),
('m4', 50),
('m5', 65),
('m6', 80),
('m7', 100);
