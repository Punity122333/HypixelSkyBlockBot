CREATE TABLE IF NOT EXISTS crystal_hollows_zones (
    zone_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    unlock_reputation INTEGER NOT NULL,
    resources TEXT NOT NULL,
    mobs TEXT NOT NULL
);

INSERT OR IGNORE INTO crystal_hollows_zones (zone_id, name, unlock_reputation, resources, mobs) VALUES
('magma_fields', 'Magma Fields', 0, '["magma_cream", "blaze_rod", "netherrack"]', '["magma_cube", "blaze"]'),
('jungle', 'Jungle', 50, '["jungle_wood", "cocoa_beans", "vines"]', '["ocelot", "parrot"]'),
('mithril_deposits', 'Mithril Deposits', 100, '["mithril", "titanium"]', '["yog", "goblin"]'),
('precursor_remnants', 'Precursor Remnants', 200, '["precursor_gear", "ancient_parts"]', '["automaton", "sludge"]'),
('goblin_holdout', 'Goblin Holdout', 150, '["goblin_egg", "amber"]', '["goblin_brute", "goblin_mage"]');
