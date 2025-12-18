CREATE TABLE IF NOT EXISTS skill_bonuses (
    skill_name TEXT PRIMARY KEY,
    stat_type TEXT NOT NULL,
    per_level INTEGER NOT NULL
);

INSERT OR IGNORE INTO skill_bonuses (skill_name, stat_type, per_level) VALUES
('farming', 'health', 4),
('mining', 'defense', 1),
('combat', 'crit_chance', 1),
('foraging', 'strength', 1),
('fishing', 'health', 2),
('enchanting', 'intelligence', 1),
('alchemy', 'intelligence', 1),
('taming', 'pet_luck', 1),
('carpentry', 'none', 0),
('runecrafting', 'none', 0),
('social', 'none', 0);
