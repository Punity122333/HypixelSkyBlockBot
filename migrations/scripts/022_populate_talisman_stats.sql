INSERT OR IGNORE INTO game_talisman_stats (
    talisman_id, name, rarity, 
    health, defense, strength, 
    crit_chance, crit_damage, intelligence, 
    speed, attack_speed, sea_creature_chance, 
    magic_find, pet_luck, ferocity, 
    ability_damage, true_defense, 
    mining_speed, mining_fortune, farming_fortune, 
    foraging_fortune, fishing_speed
) VALUES
('strength_talisman', 'Strength Talisman', 'UNCOMMON', 0, 0, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
('health_talisman', 'Health Talisman', 'UNCOMMON', 20, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
('defense_talisman', 'Defense Talisman', 'UNCOMMON', 0, 10, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
('intelligence_talisman', 'Intelligence Talisman', 'RARE', 0, 0, 0, 0, 0, 10, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
('crit_damage_talisman', 'Critical Damage Talisman', 'RARE', 0, 0, 0, 0, 10, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
('crit_chance_talisman', 'Critical Chance Talisman', 'RARE', 0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
('magic_find_talisman', 'Magic Find Talisman', 'EPIC', 0, 0, 0, 0, 0, 0, 0, 0, 0, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0),
('ferocity_talisman', 'Ferocity Talisman', 'EPIC', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 5, 0, 0, 0, 0, 0, 0, 0),
('ability_damage_talisman', 'Ability Damage Talisman', 'LEGENDARY', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 10, 0, 0, 0, 0, 0, 0),
('mining_fortune_talisman', 'Mining Fortune Talisman', 'RARE', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 10, 0, 0, 0),
('farming_fortune_talisman', 'Farming Fortune Talisman', 'RARE', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 10, 0, 0),
('foraging_fortune_talisman', 'Foraging Fortune Talisman', 'RARE', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 10, 0),
('fishing_speed_talisman', 'Fishing Speed Talisman', 'UNCOMMON', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 5),
('pet_luck_talisman', 'Pet Luck Talisman', 'EPIC', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 5, 0, 0, 0, 0, 0, 0, 0, 0),
('sea_creature_chance_talisman', 'Sea Creature Chance Talisman', 'RARE', 0, 0, 0, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
('true_defense_talisman', 'True Defense Talisman', 'EPIC', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 5, 0, 0, 0, 0, 0),
('attack_speed_talisman', 'Attack Speed Talisman', 'RARE', 0, 0, 0, 0, 0, 0, 0, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0);

UPDATE game_talisman_stats SET speed = 5 WHERE talisman_id = 'speed_talisman';
UPDATE game_talisman_stats SET foraging_fortune = 5 WHERE talisman_id = 'wood_talisman';
UPDATE game_talisman_stats SET mining_fortune = 5 WHERE talisman_id = 'mine_talisman';
UPDATE game_talisman_stats SET farming_fortune = 5 WHERE talisman_id = 'farming_talisman';
UPDATE game_talisman_stats SET magic_find = 3 WHERE talisman_id = 'scavenger_talisman';
UPDATE game_talisman_stats SET intelligence = 10 WHERE talisman_id = 'potion_affinity_talisman';
UPDATE game_talisman_stats SET sea_creature_chance = 5 WHERE talisman_id = 'sea_creature_talisman';
UPDATE game_talisman_stats SET speed = 3 WHERE talisman_id = 'feather_talisman';
UPDATE game_talisman_stats SET pet_luck = 3 WHERE talisman_id = 'lynx_talisman';
UPDATE game_talisman_stats SET intelligence = 15 WHERE talisman_id = 'ender_artifact';
