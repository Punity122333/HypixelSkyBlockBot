CREATE TABLE IF NOT EXISTS party_dungeon_floors (
    floor_number INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    min_level INTEGER NOT NULL,
    recommended_level INTEGER NOT NULL,
    gear_score INTEGER NOT NULL
);

INSERT OR REPLACE INTO party_dungeon_floors (floor_number, name, min_level, recommended_level, gear_score) VALUES
(1, 'Floor 1', 0, 5, 50),
(2, 'Floor 2', 3, 10, 100),
(3, 'Floor 3', 7, 15, 150),
(4, 'Floor 4', 10, 20, 250),
(5, 'Floor 5', 15, 25, 400),
(6, 'Floor 6', 20, 30, 600),
(7, 'Floor 7', 25, 35, 900);

CREATE TABLE IF NOT EXISTS dungeon_classes (
    class_name TEXT PRIMARY KEY,
    display_order INTEGER NOT NULL
);

INSERT OR REPLACE INTO dungeon_classes (class_name, display_order) VALUES
('healer', 1),
('mage', 2),
('berserk', 3),
('archer', 4),
('tank', 5);

CREATE TABLE IF NOT EXISTS gathering_requirements (
    activity TEXT PRIMARY KEY,
    min_level INTEGER NOT NULL,
    required_tool TEXT
);

INSERT OR REPLACE INTO gathering_requirements (activity, min_level, required_tool) VALUES
('mine', 0, NULL),
('farm', 0, NULL),
('fish', 0, NULL),
('forage', 0, NULL);

CREATE TABLE IF NOT EXISTS gathering_categories (
    category TEXT PRIMARY KEY,
    tool_types TEXT NOT NULL
);

INSERT OR REPLACE INTO gathering_categories (category, tool_types) VALUES
('mining', '["pickaxe"]'),
('farming', '["hoe"]'),
('foraging', '["axe"]'),
('fishing', '["fishing_rod"]');
