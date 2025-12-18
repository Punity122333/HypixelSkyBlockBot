CREATE TABLE IF NOT EXISTS skill_xp_requirements (
    skill_type TEXT NOT NULL,
    level INTEGER NOT NULL,
    xp_required INTEGER NOT NULL,
    PRIMARY KEY (skill_type, level)
);

INSERT OR IGNORE INTO skill_xp_requirements (skill_type, level, xp_required) VALUES
('standard', 0, 0), ('standard', 1, 50), ('standard', 2, 125), ('standard', 3, 200), ('standard', 4, 300), ('standard', 5, 500),
('standard', 6, 750), ('standard', 7, 1000), ('standard', 8, 1500), ('standard', 9, 2000), ('standard', 10, 3500),
('standard', 11, 5000), ('standard', 12, 7500), ('standard', 13, 10000), ('standard', 14, 15000), ('standard', 15, 20000),
('standard', 16, 30000), ('standard', 17, 50000), ('standard', 18, 75000), ('standard', 19, 100000), ('standard', 20, 200000),
('standard', 21, 300000), ('standard', 22, 400000), ('standard', 23, 500000), ('standard', 24, 600000), ('standard', 25, 700000),
('standard', 26, 800000), ('standard', 27, 900000), ('standard', 28, 1000000), ('standard', 29, 1100000), ('standard', 30, 1200000),
('standard', 31, 1300000), ('standard', 32, 1400000), ('standard', 33, 1500000), ('standard', 34, 1600000), ('standard', 35, 1700000),
('standard', 36, 1800000), ('standard', 37, 1900000), ('standard', 38, 2000000), ('standard', 39, 2100000), ('standard', 40, 2200000),
('standard', 41, 2300000), ('standard', 42, 2400000), ('standard', 43, 2500000), ('standard', 44, 2600000), ('standard', 45, 2750000),
('standard', 46, 2900000), ('standard', 47, 3100000), ('standard', 48, 3400000), ('standard', 49, 3700000), ('standard', 50, 4000000);

INSERT OR IGNORE INTO skill_xp_requirements (skill_type, level, xp_required) VALUES
('runecrafting', 0, 0), ('runecrafting', 1, 50), ('runecrafting', 2, 100), ('runecrafting', 3, 125), ('runecrafting', 4, 160), ('runecrafting', 5, 200),
('runecrafting', 6, 250), ('runecrafting', 7, 315), ('runecrafting', 8, 400), ('runecrafting', 9, 500), ('runecrafting', 10, 625),
('runecrafting', 11, 785), ('runecrafting', 12, 1000), ('runecrafting', 13, 1250), ('runecrafting', 14, 1600), ('runecrafting', 15, 2000),
('runecrafting', 16, 2465), ('runecrafting', 17, 3125), ('runecrafting', 18, 4000), ('runecrafting', 19, 5000), ('runecrafting', 20, 6200),
('runecrafting', 21, 7800), ('runecrafting', 22, 9800), ('runecrafting', 23, 12200), ('runecrafting', 24, 15300), ('runecrafting', 25, 19050);

INSERT OR IGNORE INTO skill_xp_requirements (skill_type, level, xp_required) VALUES
('social', 0, 0), ('social', 1, 50), ('social', 2, 100), ('social', 3, 150), ('social', 4, 250), ('social', 5, 500),
('social', 6, 750), ('social', 7, 1000), ('social', 8, 1250), ('social', 9, 1500), ('social', 10, 2000),
('social', 11, 2500), ('social', 12, 3000), ('social', 13, 3750), ('social', 14, 4500), ('social', 15, 6000),
('social', 16, 8000), ('social', 17, 10000), ('social', 18, 12500), ('social', 19, 15000), ('social', 20, 20000),
('social', 21, 25000), ('social', 22, 30000), ('social', 23, 35000), ('social', 24, 40000), ('social', 25, 50000);
