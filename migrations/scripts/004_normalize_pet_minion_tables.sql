CREATE TABLE pet_stats (
    pet_id INTEGER PRIMARY KEY,
    stats TEXT NOT NULL,
    FOREIGN KEY (pet_id) REFERENCES pets(id) ON DELETE CASCADE
);

CREATE TABLE pet_abilities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pet_id INTEGER NOT NULL,
    ability_name TEXT NOT NULL,
    ability_description TEXT,
    FOREIGN KEY (pet_id) REFERENCES pets(id) ON DELETE CASCADE
);

CREATE TABLE minion_storage (
    minion_id INTEGER PRIMARY KEY,
    slot1_item TEXT,
    slot1_amount INTEGER DEFAULT 0,
    slot2_item TEXT,
    slot2_amount INTEGER DEFAULT 0,
    slot3_item TEXT,
    slot3_amount INTEGER DEFAULT 0,
    slot4_item TEXT,
    slot4_amount INTEGER DEFAULT 0,
    slot5_item TEXT,
    slot5_amount INTEGER DEFAULT 0,
    FOREIGN KEY (minion_id) REFERENCES minions(id) ON DELETE CASCADE
);

CREATE TABLE minion_upgrades (
    minion_id INTEGER NOT NULL,
    upgrade_type TEXT NOT NULL,
    upgrade_level INTEGER DEFAULT 1,
    PRIMARY KEY (minion_id, upgrade_type),
    FOREIGN KEY (minion_id) REFERENCES minions(id) ON DELETE CASCADE
);

CREATE INDEX idx_pets_user ON pets(user_id);
CREATE INDEX idx_pets_active ON pets(user_id, active);
CREATE INDEX idx_minions_user ON minions(user_id);
CREATE INDEX idx_minions_location ON minions(user_id, island_slot);
