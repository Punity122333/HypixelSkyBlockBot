CREATE TABLE IF NOT EXISTS weapon_abilities (
    item_id TEXT PRIMARY KEY,
    ability_name TEXT NOT NULL,
    mana_cost INTEGER NOT NULL DEFAULT 50,
    cooldown REAL NOT NULL DEFAULT 1.0,
    base_damage_multiplier REAL DEFAULT 1.0,
    intelligence_scaling REAL DEFAULT 0.0,
    strength_scaling REAL DEFAULT 0.0,
    ability_damage_scaling REAL DEFAULT 0.0,
    aoe_radius INTEGER DEFAULT 0,
    hits INTEGER DEFAULT 1,
    arrows INTEGER DEFAULT 1,
    piercing BOOLEAN DEFAULT 0,
    wither_effect BOOLEAN DEFAULT 0,
    lifesteal_percent INTEGER DEFAULT 0,
    defense_boost INTEGER DEFAULT 0,
    duration INTEGER DEFAULT 0,
    teleport_distance INTEGER DEFAULT 0,
    coins_scaling REAL DEFAULT 0.0,
    max_bonus_damage INTEGER DEFAULT 0,
    description TEXT,
    FOREIGN KEY (item_id) REFERENCES game_items(item_id) ON DELETE CASCADE
);

INSERT OR REPLACE INTO weapon_abilities (item_id, ability_name, mana_cost, cooldown, base_damage_multiplier, intelligence_scaling, strength_scaling, ability_damage_scaling, aoe_radius, wither_effect, description) VALUES
('hyperion', 'Wither Impact', 150, 2.0, 50.0, 0.08, 0.012, 0.04, 10, 1, 'Deal massive AOE damage based on your intelligence. True destruction.'),
('valkyrie', 'Wither Impact', 150, 2.0, 40.0, 0.065, 0.01, 0.035, 10, 0, 'Deal massive AOE damage based on your intelligence'),
('astraea', 'Wither Impact', 150, 2.0, 35.0, 0.055, 0.008, 0.03, 10, 0, 'Deal massive AOE damage based on your intelligence'),
('scylla', 'Wither Impact', 150, 2.0, 30.0, 0.045, 0.007, 0.025, 10, 0, 'Deal massive AOE damage based on your intelligence'),
('aspect_of_the_dragons', 'Dragon Rage', 100, 1.0, 6.0, 0.0, 0.012, 0.015, 0, 0, 'Shoot a fireball that deals extra damage'),
('shadow_fury', 'Shadow Fury', 150, 1.0, 12.0, 0.0, 0.01, 0.0, 0, 0, 'Strike the enemy 5 times rapidly'),
('livid_dagger', 'Throw', 50, 0.5, 5.5, 0.0, 0.008, 0.0, 0, 0, 'Throw your dagger at an enemy'),
('giants_sword', 'Giants Slam', 100, 3.0, 18.0, 0.0, 0.03, 0.0, 5, 0, 'Slam the ground dealing massive damage to nearby enemies'),
('terminator', 'Termination', 60, 0.0, 8.0, 0.0, 0.01, 0.0, 0, 0, 'Shoot 5 arrows at once'),
('juju_shortbow', 'Triple Shot', 40, 0.0, 4.5, 0.0, 0.008, 0.0, 0, 0, 'Shoot 3 arrows at once'),
('aspect_of_the_end', 'Instant Transmission', 50, 0.0, 0.0, 0.0, 0.0, 0.0, 0, 0, 'Teleport 8 blocks ahead'),
('flower_of_truth', 'Heat-Seeking Rose', 100, 1.0, 7.0, 0.0, 0.01, 0.0, 0, 0, 'Throw a tracking rose that pierces enemies'),
('midas_sword', 'Greed', 0, 0.0, 0.0, 0.0, 0.0, 0.0, 0, 0, 'Deal bonus damage based on coins in purse'),
('reaper_scythe', 'Reap', 120, 2.0, 10.0, 0.02, 0.015, 0.0, 8, 0, 'Deal AOE damage and heal based on damage dealt'),
('yeti_sword', 'Ice Shield', 80, 5.0, 0.0, 0.0, 0.01, 0.0, 0, 0, 'Gain massive defense for 5 seconds'),
('necron_blade', 'Necrons Wrath', 200, 3.0, 22.0, 0.035, 0.015, 0.02, 15, 0, 'Unleash devastating wither power'),
('atomsplit_katana', 'Atomic Split', 180, 2.0, 20.0, 0.0, 0.02, 0.0, 7, 0, 'Split atoms and deal massive damage'),
('dark_claymore', 'Dark Slash', 150, 2.5, 24.0, 0.0, 0.025, 0.0, 0, 0, 'Deal massive damage and heal based on damage dealt');

UPDATE weapon_abilities SET hits = 5 WHERE item_id = 'shadow_fury';
UPDATE weapon_abilities SET arrows = 5 WHERE item_id = 'terminator';
UPDATE weapon_abilities SET arrows = 3 WHERE item_id = 'juju_shortbow';
UPDATE weapon_abilities SET teleport_distance = 8 WHERE item_id = 'aspect_of_the_end';
UPDATE weapon_abilities SET piercing = 1 WHERE item_id = 'flower_of_truth';
UPDATE weapon_abilities SET coins_scaling = 0.00001, max_bonus_damage = 2000 WHERE item_id = 'midas_sword';
UPDATE weapon_abilities SET lifesteal_percent = 50 WHERE item_id = 'reaper_scythe';
UPDATE weapon_abilities SET defense_boost = 300, duration = 5 WHERE item_id = 'yeti_sword';
UPDATE weapon_abilities SET lifesteal_percent = 30 WHERE item_id = 'dark_claymore';
