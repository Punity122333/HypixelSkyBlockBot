CREATE TABLE player_equipment_new (
    user_id INTEGER PRIMARY KEY,
    helmet_slot INTEGER,
    chestplate_slot INTEGER,
    leggings_slot INTEGER,
    boots_slot INTEGER,
    sword_slot INTEGER,
    bow_slot INTEGER,
    pickaxe_slot INTEGER,
    axe_slot INTEGER,
    hoe_slot INTEGER,
    fishing_rod_slot INTEGER,
    FOREIGN KEY (user_id) REFERENCES players(user_id) ON DELETE CASCADE
);

INSERT INTO player_equipment_new (user_id, helmet_slot, chestplate_slot, leggings_slot, boots_slot, sword_slot, bow_slot, pickaxe_slot, axe_slot, hoe_slot, fishing_rod_slot)
SELECT user_id, helmet_slot, chestplate_slot, leggings_slot, boots_slot, 
       sword_slot,
       bow_slot,
       NULL,
       axe_slot, hoe_slot, fishing_rod_slot
FROM player_equipment;

DROP TABLE player_equipment;
ALTER TABLE player_equipment_new RENAME TO player_equipment;

CREATE INDEX IF NOT EXISTS idx_player_equipment_user ON player_equipment(user_id);
