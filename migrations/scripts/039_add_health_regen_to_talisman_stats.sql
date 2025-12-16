-- Migration: Add health_regen to game_talisman_stats table
-- This ensures talismans can provide health regeneration bonuses

ALTER TABLE game_talisman_stats ADD COLUMN health_regen INTEGER DEFAULT 0;

-- Add some example health regen talismans
UPDATE game_talisman_stats SET health_regen = 3 WHERE talisman_id = 'health_talisman';
UPDATE game_talisman_stats SET health_regen = 5 WHERE talisman_id = 'healing_talisman';
UPDATE game_talisman_stats SET health_regen = 2 WHERE talisman_id = 'village_talisman';

-- Create a dedicated health regen talisman if it doesn't exist
INSERT OR IGNORE INTO game_talisman_stats (
    talisman_id, name, rarity, 
    health, defense, strength, 
    crit_chance, crit_damage, intelligence, 
    speed, attack_speed, sea_creature_chance, 
    magic_find, pet_luck, ferocity, 
    ability_damage, true_defense, 
    mining_speed, mining_fortune, farming_fortune, 
    foraging_fortune, fishing_speed, health_regen
) VALUES
('healing_talisman', 'Healing Talisman', 'UNCOMMON', 10, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 5),
('regeneration_talisman', 'Regeneration Talisman', 'RARE', 20, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8);
