INSERT OR REPLACE INTO game_items (item_id, name, rarity, item_type, stats, lore, special_ability, craft_recipe, npc_sell_price, collection_req, default_bazaar_price)
VALUES
('steel_helmet', 'Steel Helmet', 'UNCOMMON', 'HELMET', '{"defense": 30, "health": 35}', 'Reinforced steel protection', '', '{"enchanted_iron": 8, "iron_ingot": 16}', 150, '{}', 300),
('steel_chestplate', 'Steel Chestplate', 'UNCOMMON', 'CHESTPLATE', '{"defense": 50, "health": 60}', 'Reinforced steel protection', '', '{"enchanted_iron": 16, "iron_ingot": 32}', 250, '{}', 500),
('steel_leggings', 'Steel Leggings', 'UNCOMMON', 'LEGGINGS', '{"defense": 40, "health": 45}', 'Reinforced steel protection', '', '{"enchanted_iron": 12, "iron_ingot": 24}', 200, '{}', 400),
('steel_boots', 'Steel Boots', 'UNCOMMON', 'BOOTS', '{"defense": 25, "health": 30}', 'Reinforced steel protection', '', '{"enchanted_iron": 6, "iron_ingot": 12}', 120, '{}', 240),

('emerald_helmet', 'Emerald Helmet', 'RARE', 'HELMET', '{"defense": 40, "health": 50, "magic_find": 5}', 'Precious emerald armor', '', '{"enchanted_emerald": 16, "emerald": 32}', 500, '{}', 1000),
('emerald_chestplate', 'Emerald Chestplate', 'RARE', 'CHESTPLATE', '{"defense": 70, "health": 80, "magic_find": 10}', 'Precious emerald armor', '', '{"enchanted_emerald": 32, "emerald": 64}', 850, '{}', 1700),
('emerald_leggings', 'Emerald Leggings', 'RARE', 'LEGGINGS', '{"defense": 55, "health": 65, "magic_find": 8}', 'Precious emerald armor', '', '{"enchanted_emerald": 24, "emerald": 48}', 680, '{}', 1360),
('emerald_boots', 'Emerald Boots', 'RARE', 'BOOTS', '{"defense": 35, "health": 45, "magic_find": 5}', 'Precious emerald armor', '', '{"enchanted_emerald": 12, "emerald": 24}', 420, '{}', 840),

('obsidian_helmet', 'Obsidian Helmet', 'RARE', 'HELMET', '{"defense": 60, "health": 70, "true_defense": 5}', 'Hardened obsidian armor', '', '{"enchanted_obsidian": 8, "obsidian": 64}', 800, '{}', 1600),
('obsidian_chestplate', 'Obsidian Chestplate', 'RARE', 'CHESTPLATE', '{"defense": 100, "health": 110, "true_defense": 10}', 'Hardened obsidian armor', '', '{"enchanted_obsidian": 16, "obsidian": 128}', 1400, '{}', 2800),
('obsidian_leggings', 'Obsidian Leggings', 'RARE', 'LEGGINGS', '{"defense": 80, "health": 90, "true_defense": 8}', 'Hardened obsidian armor', '', '{"enchanted_obsidian": 12, "obsidian": 96}', 1100, '{}', 2200),
('obsidian_boots', 'Obsidian Boots', 'RARE', 'BOOTS', '{"defense": 50, "health": 60, "true_defense": 5}', 'Hardened obsidian armor', '', '{"enchanted_obsidian": 6, "obsidian": 48}', 700, '{}', 1400),

('mithril_helmet', 'Mithril Helmet', 'EPIC', 'HELMET', '{"defense": 80, "health": 100, "mining_speed": 20}', 'Lightweight magical ore armor', '', '{"refined_mithril": 4, "mithril": 64}', 2000, '{}', 4000),
('mithril_chestplate', 'Mithril Chestplate', 'EPIC', 'CHESTPLATE', '{"defense": 130, "health": 150, "mining_speed": 35}', 'Lightweight magical ore armor', '', '{"refined_mithril": 8, "mithril": 128}', 3500, '{}', 7000),
('mithril_leggings', 'Mithril Leggings', 'EPIC', 'LEGGINGS', '{"defense": 105, "health": 125, "mining_speed": 28}', 'Lightweight magical ore armor', '', '{"refined_mithril": 6, "mithril": 96}', 2800, '{}', 5600),
('mithril_boots', 'Mithril Boots', 'EPIC', 'BOOTS', '{"defense": 70, "health": 85, "mining_speed": 20}', 'Lightweight magical ore armor', '', '{"refined_mithril": 3, "mithril": 48}', 1800, '{}', 3600),

('titanium_helmet', 'Titanium Helmet', 'EPIC', 'HELMET', '{"defense": 90, "health": 110, "strength": 15}', 'Durable titanium armor', '', '{"refined_titanium": 4, "titanium": 64}', 2500, '{}', 5000),
('titanium_chestplate', 'Titanium Chestplate', 'EPIC', 'CHESTPLATE', '{"defense": 145, "health": 170, "strength": 25}', 'Durable titanium armor', '', '{"refined_titanium": 8, "titanium": 128}', 4200, '{}', 8400),
('titanium_leggings', 'Titanium Leggings', 'EPIC', 'LEGGINGS', '{"defense": 115, "health": 140, "strength": 20}', 'Durable titanium armor', '', '{"refined_titanium": 6, "titanium": 96}', 3400, '{}', 6800),
('titanium_boots', 'Titanium Boots', 'EPIC', 'BOOTS', '{"defense": 80, "health": 95, "strength": 12}', 'Durable titanium armor', '', '{"refined_titanium": 3, "titanium": 48}', 2200, '{}', 4400),

('dragon_helmet', 'Dragon Helmet', 'LEGENDARY', 'HELMET', '{"defense": 120, "health": 150, "strength": 30, "crit_damage": 15}', 'Forged from dragon scales', 'Dragon Fury: +25% damage to all enemies', '{"dragon_scale": 16, "enchanted_diamond_block": 8}', 10000, '{}', 20000),
('dragon_chestplate', 'Dragon Chestplate', 'LEGENDARY', 'CHESTPLATE', '{"defense": 190, "health": 230, "strength": 50, "crit_damage": 25}', 'Forged from dragon scales', 'Dragon Fury: +25% damage to all enemies', '{"dragon_scale": 32, "enchanted_diamond_block": 16}', 17000, '{}', 34000),
('dragon_leggings', 'Dragon Leggings', 'LEGENDARY', 'LEGGINGS', '{"defense": 155, "health": 190, "strength": 40, "crit_damage": 20}', 'Forged from dragon scales', 'Dragon Fury: +25% damage to all enemies', '{"dragon_scale": 24, "enchanted_diamond_block": 12}', 13500, '{}', 27000),
('dragon_boots', 'Dragon Boots', 'LEGENDARY', 'BOOTS', '{"defense": 110, "health": 130, "strength": 25, "crit_damage": 12}', 'Forged from dragon scales', 'Dragon Fury: +25% damage to all enemies', '{"dragon_scale": 12, "enchanted_diamond_block": 6}', 8500, '{}', 17000),

('necromancer_helmet', 'Necromancer Helmet', 'LEGENDARY', 'HELMET', '{"defense": 100, "health": 140, "intelligence": 80, "ability_damage": 15}', 'Channels dark magic', 'Undead Legion: Summon skeleton minions', '{"nether_star": 2, "enchanted_bone": 128}', 12000, '{}', 24000),
('necromancer_chestplate', 'Necromancer Chestplate', 'LEGENDARY', 'CHESTPLATE', '{"defense": 160, "health": 210, "intelligence": 130, "ability_damage": 25}', 'Channels dark magic', 'Undead Legion: Summon skeleton minions', '{"nether_star": 4, "enchanted_bone": 256}', 20000, '{}', 40000),
('necromancer_leggings', 'Necromancer Leggings', 'LEGENDARY', 'LEGGINGS', '{"defense": 130, "health": 175, "intelligence": 105, "ability_damage": 20}', 'Channels dark magic', 'Undead Legion: Summon skeleton minions', '{"nether_star": 3, "enchanted_bone": 192}', 16000, '{}', 32000),
('necromancer_boots', 'Necromancer Boots', 'LEGENDARY', 'BOOTS', '{"defense": 90, "health": 120, "intelligence": 70, "ability_damage": 12}', 'Channels dark magic', 'Undead Legion: Summon skeleton minions', '{"nether_star": 1, "enchanted_bone": 96}', 10000, '{}', 20000),

('blaze_helmet', 'Blaze Helmet', 'EPIC', 'HELMET', '{"defense": 70, "health": 90, "strength": 25, "intelligence": 40}', 'Infused with blaze essence', 'Fire Immunity: Immune to fire damage', '{"enchanted_blaze_rod": 32, "blaze_powder": 64}', 3000, '{}', 6000),
('blaze_chestplate', 'Blaze Chestplate', 'EPIC', 'CHESTPLATE', '{"defense": 115, "health": 140, "strength": 40, "intelligence": 65}', 'Infused with blaze essence', 'Fire Immunity: Immune to fire damage', '{"enchanted_blaze_rod": 64, "blaze_powder": 128}', 5000, '{}', 10000),
('blaze_leggings', 'Blaze Leggings', 'EPIC', 'LEGGINGS', '{"defense": 92, "health": 115, "strength": 32, "intelligence": 52}', 'Infused with blaze essence', 'Fire Immunity: Immune to fire damage', '{"enchanted_blaze_rod": 48, "blaze_powder": 96}', 4000, '{}', 8000),
('blaze_boots', 'Blaze Boots', 'EPIC', 'BOOTS', '{"defense": 65, "health": 80, "strength": 22, "intelligence": 35}', 'Infused with blaze essence', 'Fire Immunity: Immune to fire damage', '{"enchanted_blaze_rod": 24, "blaze_powder": 48}', 2500, '{}', 5000),

('shadow_helmet', 'Shadow Helmet', 'EPIC', 'HELMET', '{"defense": 75, "health": 95, "crit_chance": 8, "speed": 15}', 'Melts into the shadows', 'Shadow Veil: +30% stealth', '{"enchanted_obsidian": 16, "ender_pearl": 64}', 3500, '{}', 7000),
('shadow_chestplate', 'Shadow Chestplate', 'EPIC', 'CHESTPLATE', '{"defense": 120, "health": 145, "crit_chance": 12, "speed": 25}', 'Melts into the shadows', 'Shadow Veil: +30% stealth', '{"enchanted_obsidian": 32, "ender_pearl": 128}', 5800, '{}', 11600),
('shadow_leggings', 'Shadow Leggings', 'EPIC', 'LEGGINGS', '{"defense": 95, "health": 120, "crit_chance": 10, "speed": 20}', 'Melts into the shadows', 'Shadow Veil: +30% stealth', '{"enchanted_obsidian": 24, "ender_pearl": 96}', 4600, '{}', 9200),
('shadow_boots', 'Shadow Boots', 'EPIC', 'BOOTS', '{"defense": 68, "health": 85, "crit_chance": 6, "speed": 12}', 'Melts into the shadows', 'Shadow Veil: +30% stealth', '{"enchanted_obsidian": 12, "ender_pearl": 48}', 3000, '{}', 6000),

('crystal_helmet', 'Crystal Helmet', 'EPIC', 'HELMET', '{"defense": 65, "health": 85, "intelligence": 70, "magic_find": 10}', 'Crystallized perfection', 'Crystal Resonance: +15% XP gain', '{"enchanted_diamond": 32, "enchanted_emerald": 16}', 4000, '{}', 8000),
('crystal_chestplate', 'Crystal Chestplate', 'EPIC', 'CHESTPLATE', '{"defense": 110, "health": 135, "intelligence": 110, "magic_find": 16}', 'Crystallized perfection', 'Crystal Resonance: +15% XP gain', '{"enchanted_diamond": 64, "enchanted_emerald": 32}', 6800, '{}', 13600),
('crystal_leggings', 'Crystal Leggings', 'EPIC', 'LEGGINGS', '{"defense": 88, "health": 110, "intelligence": 90, "magic_find": 13}', 'Crystallized perfection', 'Crystal Resonance: +15% XP gain', '{"enchanted_diamond": 48, "enchanted_emerald": 24}', 5400, '{}', 10800),
('crystal_boots', 'Crystal Boots', 'EPIC', 'BOOTS', '{"defense": 62, "health": 78, "intelligence": 60, "magic_find": 8}', 'Crystallized perfection', 'Crystal Resonance: +15% XP gain', '{"enchanted_diamond": 24, "enchanted_emerald": 12}', 3500, '{}', 7000),

('berserker_helmet', 'Berserker Helmet', 'RARE', 'HELMET', '{"defense": 45, "health": 65, "strength": 35, "crit_damage": 25}', 'Raw offensive power', 'Berserker Rage: +50% damage at low HP', '{"enchanted_iron_block": 8, "enchanted_gold": 16}', 1200, '{}', 2400),
('berserker_chestplate', 'Berserker Chestplate', 'RARE', 'CHESTPLATE', '{"defense": 75, "health": 100, "strength": 55, "crit_damage": 40}', 'Raw offensive power', 'Berserker Rage: +50% damage at low HP', '{"enchanted_iron_block": 16, "enchanted_gold": 32}', 2000, '{}', 4000),
('berserker_leggings', 'Berserker Leggings', 'RARE', 'LEGGINGS', '{"defense": 60, "health": 82, "strength": 45, "crit_damage": 32}', 'Raw offensive power', 'Berserker Rage: +50% damage at low HP', '{"enchanted_iron_block": 12, "enchanted_gold": 24}', 1600, '{}', 3200),
('berserker_boots', 'Berserker Boots', 'RARE', 'BOOTS', '{"defense": 42, "health": 58, "strength": 30, "crit_damage": 20}', 'Raw offensive power', 'Berserker Rage: +50% damage at low HP', '{"enchanted_iron_block": 6, "enchanted_gold": 12}', 1000, '{}', 2000),

('glacial_helmet', 'Glacial Helmet', 'RARE', 'HELMET', '{"defense": 50, "health": 70, "intelligence": 45, "speed": -5}', 'Frozen solid armor', 'Frost Aura: Slows nearby enemies', '{"enchanted_ice": 32, "enchanted_diamond": 8}', 1500, '{}', 3000),
('glacial_chestplate', 'Glacial Chestplate', 'RARE', 'CHESTPLATE', '{"defense": 85, "health": 110, "intelligence": 70, "speed": -8}', 'Frozen solid armor', 'Frost Aura: Slows nearby enemies', '{"enchanted_ice": 64, "enchanted_diamond": 16}', 2500, '{}', 5000),
('glacial_leggings', 'Glacial Leggings', 'RARE', 'LEGGINGS', '{"defense": 68, "health": 90, "intelligence": 58, "speed": -6}', 'Frozen solid armor', 'Frost Aura: Slows nearby enemies', '{"enchanted_ice": 48, "enchanted_diamond": 12}', 2000, '{}', 4000),
('glacial_boots', 'Glacial Boots', 'RARE', 'BOOTS', '{"defense": 48, "health": 65, "intelligence": 40, "speed": -4}', 'Frozen solid armor', 'Frost Aura: Slows nearby enemies', '{"enchanted_ice": 24, "enchanted_diamond": 6}', 1200, '{}', 2400),

('paladin_helmet', 'Paladin Helmet', 'EPIC', 'HELMET', '{"defense": 85, "health": 110, "strength": 20, "true_defense": 8}', 'Holy warrior armor', 'Divine Protection: Heal nearby allies', '{"enchanted_gold_block": 8, "enchanted_diamond": 32}', 4500, '{}', 9000),
('paladin_chestplate', 'Paladin Chestplate', 'EPIC', 'CHESTPLATE', '{"defense": 140, "health": 175, "strength": 32, "true_defense": 12}', 'Holy warrior armor', 'Divine Protection: Heal nearby allies', '{"enchanted_gold_block": 16, "enchanted_diamond": 64}', 7500, '{}', 15000),
('paladin_leggings', 'Paladin Leggings', 'EPIC', 'LEGGINGS', '{"defense": 112, "health": 142, "strength": 26, "true_defense": 10}', 'Holy warrior armor', 'Divine Protection: Heal nearby allies', '{"enchanted_gold_block": 12, "enchanted_diamond": 48}', 6000, '{}', 12000),
('paladin_boots', 'Paladin Boots', 'EPIC', 'BOOTS', '{"defense": 78, "health": 98, "strength": 18, "true_defense": 6}', 'Holy warrior armor', 'Divine Protection: Heal nearby allies', '{"enchanted_gold_block": 6, "enchanted_diamond": 24}', 4000, '{}', 8000),

('hunter_helmet', 'Hunter Helmet', 'RARE', 'HELMET', '{"defense": 40, "health": 60, "crit_chance": 12, "speed": 10}', 'Swift and deadly', 'Hunter Instinct: +20% damage to animals', '{"leather": 64, "enchanted_string": 16}', 900, '{}', 1800),
('hunter_chestplate', 'Hunter Chestplate', 'RARE', 'CHESTPLATE', '{"defense": 68, "health": 95, "crit_chance": 18, "speed": 16}', 'Swift and deadly', 'Hunter Instinct: +20% damage to animals', '{"leather": 128, "enchanted_string": 32}', 1500, '{}', 3000),
('hunter_leggings', 'Hunter Leggings', 'RARE', 'LEGGINGS', '{"defense": 54, "health": 78, "crit_chance": 15, "speed": 13}', 'Swift and deadly', 'Hunter Instinct: +20% damage to animals', '{"leather": 96, "enchanted_string": 24}', 1200, '{}', 2400),
('hunter_boots', 'Hunter Boots', 'RARE', 'BOOTS', '{"defense": 38, "health": 55, "crit_chance": 10, "speed": 8}', 'Swift and deadly', 'Hunter Instinct: +20% damage to animals', '{"leather": 48, "enchanted_string": 12}', 750, '{}', 1500),

('warlock_helmet', 'Warlock Helmet', 'EPIC', 'HELMET', '{"defense": 60, "health": 80, "intelligence": 100, "ability_damage": 20}', 'Dark sorcery empowerment', 'Mana Regeneration: +50% mana regen', '{"enchanted_obsidian": 16, "nether_star": 1}', 5000, '{}', 10000),
('warlock_chestplate', 'Warlock Chestplate', 'EPIC', 'CHESTPLATE', '{"defense": 100, "health": 125, "intelligence": 160, "ability_damage": 32}', 'Dark sorcery empowerment', 'Mana Regeneration: +50% mana regen', '{"enchanted_obsidian": 32, "nether_star": 2}', 8500, '{}', 17000),
('warlock_leggings', 'Warlock Leggings', 'EPIC', 'LEGGINGS', '{"defense": 80, "health": 102, "intelligence": 130, "ability_damage": 26}', 'Dark sorcery empowerment', 'Mana Regeneration: +50% mana regen', '{"enchanted_obsidian": 24, "nether_star": 1}', 6800, '{}', 13600),
('warlock_boots', 'Warlock Boots', 'EPIC', 'BOOTS', '{"defense": 55, "health": 72, "intelligence": 85, "ability_damage": 16}', 'Dark sorcery empowerment', 'Mana Regeneration: +50% mana regen', '{"enchanted_obsidian": 12, "nether_star": 1}', 4500, '{}', 9000),

('assassin_helmet', 'Assassin Helmet', 'RARE', 'HELMET', '{"defense": 35, "health": 50, "crit_chance": 15, "crit_damage": 30, "speed": 18}', 'Strike from the shadows', 'Critical Strike: Deal double damage on crits', '{"enchanted_string": 32, "ender_pearl": 32}', 1400, '{}', 2800),
('assassin_chestplate', 'Assassin Chestplate', 'RARE', 'CHESTPLATE', '{"defense": 60, "health": 80, "crit_chance": 22, "crit_damage": 48, "speed": 28}', 'Strike from the shadows', 'Critical Strike: Deal double damage on crits', '{"enchanted_string": 64, "ender_pearl": 64}', 2400, '{}', 4800),
('assassin_leggings', 'Assassin Leggings', 'RARE', 'LEGGINGS', '{"defense": 48, "health": 65, "crit_chance": 18, "crit_damage": 38, "speed": 23}', 'Strike from the shadows', 'Critical Strike: Deal double damage on crits', '{"enchanted_string": 48, "ender_pearl": 48}', 1900, '{}', 3800),
('assassin_boots', 'Assassin Boots', 'RARE', 'BOOTS', '{"defense": 32, "health": 45, "crit_chance": 12, "crit_damage": 25, "speed": 15}', 'Strike from the shadows', 'Critical Strike: Deal double damage on crits', '{"enchanted_string": 24, "ender_pearl": 24}', 1200, '{}', 2400),

('tank_helmet', 'Tank Helmet', 'EPIC', 'HELMET', '{"defense": 110, "health": 140, "true_defense": 12}', 'Impenetrable defense', 'Iron Wall: -50% damage taken', '{"enchanted_iron_block": 16, "enchanted_obsidian": 8}', 5500, '{}', 11000),
('tank_chestplate', 'Tank Chestplate', 'EPIC', 'CHESTPLATE', '{"defense": 180, "health": 220, "true_defense": 18}', 'Impenetrable defense', 'Iron Wall: -50% damage taken', '{"enchanted_iron_block": 32, "enchanted_obsidian": 16}', 9000, '{}', 18000),
('tank_leggings', 'Tank Leggings', 'EPIC', 'LEGGINGS', '{"defense": 145, "health": 180, "true_defense": 15}', 'Impenetrable defense', 'Iron Wall: -50% damage taken', '{"enchanted_iron_block": 24, "enchanted_obsidian": 12}', 7200, '{}', 14400),
('tank_boots', 'Tank Boots', 'EPIC', 'BOOTS', '{"defense": 100, "health": 125, "true_defense": 10}', 'Impenetrable defense', 'Iron Wall: -50% damage taken', '{"enchanted_iron_block": 12, "enchanted_obsidian": 6}', 4800, '{}', 9600),

('ender_helmet', 'Ender Helmet', 'EPIC', 'HELMET', '{"defense": 70, "health": 90, "intelligence": 60, "speed": 25}', 'Teleportation mastery', 'Ender Warp: Teleport short distances', '{"enchanted_ender_pearl": 32, "enchanted_eye_of_ender": 16}', 4500, '{}', 9000),
('ender_chestplate', 'Ender Chestplate', 'EPIC', 'CHESTPLATE', '{"defense": 115, "health": 140, "intelligence": 95, "speed": 40}', 'Teleportation mastery', 'Ender Warp: Teleport short distances', '{"enchanted_ender_pearl": 64, "enchanted_eye_of_ender": 32}', 7500, '{}', 15000),
('ender_leggings', 'Ender Leggings', 'EPIC', 'LEGGINGS', '{"defense": 92, "health": 115, "intelligence": 78, "speed": 32}', 'Teleportation mastery', 'Ender Warp: Teleport short distances', '{"enchanted_ender_pearl": 48, "enchanted_eye_of_ender": 24}', 6000, '{}', 12000),
('ender_boots', 'Ender Boots', 'EPIC', 'BOOTS', '{"defense": 65, "health": 80, "intelligence": 52, "speed": 22}', 'Teleportation mastery', 'Ender Warp: Teleport short distances', '{"enchanted_ender_pearl": 24, "enchanted_eye_of_ender": 12}', 4000, '{}', 8000),

('phoenix_helmet', 'Phoenix Helmet', 'LEGENDARY', 'HELMET', '{"defense": 95, "health": 120, "strength": 40, "intelligence": 50}', 'Rise from the ashes', 'Phoenix Rebirth: Revive on death once per hour', '{"enchanted_blaze_rod": 64, "nether_star": 2}', 15000, '{}', 30000),
('phoenix_chestplate', 'Phoenix Chestplate', 'LEGENDARY', 'CHESTPLATE', '{"defense": 155, "health": 190, "strength": 65, "intelligence": 80}', 'Rise from the ashes', 'Phoenix Rebirth: Revive on death once per hour', '{"enchanted_blaze_rod": 128, "nether_star": 4}', 25000, '{}', 50000),
('phoenix_leggings', 'Phoenix Leggings', 'LEGENDARY', 'LEGGINGS', '{"defense": 125, "health": 155, "strength": 52, "intelligence": 65}', 'Rise from the ashes', 'Phoenix Rebirth: Revive on death once per hour', '{"enchanted_blaze_rod": 96, "nether_star": 3}', 20000, '{}', 40000),
('phoenix_boots', 'Phoenix Boots', 'LEGENDARY', 'BOOTS', '{"defense": 88, "health": 110, "strength": 35, "intelligence": 45}', 'Rise from the ashes', 'Phoenix Rebirth: Revive on death once per hour', '{"enchanted_blaze_rod": 48, "nether_star": 1}', 13000, '{}', 26000),

('samurai_helmet', 'Samurai Helmet', 'RARE', 'HELMET', '{"defense": 55, "health": 75, "strength": 28, "crit_chance": 10}', 'Ancient warrior tradition', 'Bushido: +15% damage when below 50% HP', '{"enchanted_iron_block": 12, "enchanted_string": 32}', 2000, '{}', 4000),
('samurai_chestplate', 'Samurai Chestplate', 'RARE', 'CHESTPLATE', '{"defense": 90, "health": 115, "strength": 45, "crit_chance": 15}', 'Ancient warrior tradition', 'Bushido: +15% damage when below 50% HP', '{"enchanted_iron_block": 24, "enchanted_string": 64}', 3500, '{}', 7000),
('samurai_leggings', 'Samurai Leggings', 'RARE', 'LEGGINGS', '{"defense": 72, "health": 95, "strength": 36, "crit_chance": 12}', 'Ancient warrior tradition', 'Bushido: +15% damage when below 50% HP', '{"enchanted_iron_block": 18, "enchanted_string": 48}', 2800, '{}', 5600),
('samurai_boots', 'Samurai Boots', 'RARE', 'BOOTS', '{"defense": 50, "health": 68, "strength": 25, "crit_chance": 8}', 'Ancient warrior tradition', 'Bushido: +15% damage when below 50% HP', '{"enchanted_iron_block": 9, "enchanted_string": 24}', 1800, '{}', 3600),

('void_helmet', 'Void Helmet', 'LEGENDARY', 'HELMET', '{"defense": 105, "health": 130, "intelligence": 90, "true_defense": 10}', 'Embrace the darkness', 'Void Corruption: Deal +30% damage in dark areas', '{"enchanted_obsidian": 32, "enchanted_ender_pearl": 32}', 13000, '{}', 26000),
('void_chestplate', 'Void Chestplate', 'LEGENDARY', 'CHESTPLATE', '{"defense": 170, "health": 205, "intelligence": 145, "true_defense": 16}', 'Embrace the darkness', 'Void Corruption: Deal +30% damage in dark areas', '{"enchanted_obsidian": 64, "enchanted_ender_pearl": 64}', 22000, '{}', 44000),
('void_leggings', 'Void Leggings', 'LEGENDARY', 'LEGGINGS', '{"defense": 138, "health": 168, "intelligence": 118, "true_defense": 13}', 'Embrace the darkness', 'Void Corruption: Deal +30% damage in dark areas', '{"enchanted_obsidian": 48, "enchanted_ender_pearl": 48}', 17500, '{}', 35000),
('void_boots', 'Void Boots', 'LEGENDARY', 'BOOTS', '{"defense": 95, "health": 118, "intelligence": 78, "true_defense": 8}', 'Embrace the darkness', 'Void Corruption: Deal +30% damage in dark areas', '{"enchanted_obsidian": 24, "enchanted_ender_pearl": 24}', 11500, '{}', 23000),

('fairy_helmet', 'Fairy Helmet', 'EPIC', 'HELMET', '{"defense": 55, "health": 75, "intelligence": 55, "speed": 20, "magic_find": 8}', 'Enchanted by nature', 'Fairy Blessing: +10% XP and coins', '{"enchanted_diamond": 16, "enchanted_emerald": 32}', 4000, '{}', 8000),
('fairy_chestplate', 'Fairy Chestplate', 'EPIC', 'CHESTPLATE', '{"defense": 92, "health": 118, "intelligence": 88, "speed": 32, "magic_find": 12}', 'Enchanted by nature', 'Fairy Blessing: +10% XP and coins', '{"enchanted_diamond": 32, "enchanted_emerald": 64}', 6800, '{}', 13600),
('fairy_leggings', 'Fairy Leggings', 'EPIC', 'LEGGINGS', '{"defense": 74, "health": 96, "intelligence": 72, "speed": 26, "magic_find": 10}', 'Enchanted by nature', 'Fairy Blessing: +10% XP and coins', '{"enchanted_diamond": 24, "enchanted_emerald": 48}', 5400, '{}', 10800),
('fairy_boots', 'Fairy Boots', 'EPIC', 'BOOTS', '{"defense": 52, "health": 68, "intelligence": 48, "speed": 18, "magic_find": 6}', 'Enchanted by nature', 'Fairy Blessing: +10% XP and coins', '{"enchanted_diamond": 12, "enchanted_emerald": 24}', 3600, '{}', 7200),

('wither_helmet', 'Wither Helmet', 'LEGENDARY', 'HELMET', '{"defense": 115, "health": 145, "strength": 45, "intelligence": 60}', 'Infused with wither energy', 'Wither Impact: Deal wither damage over time', '{"nether_star": 3, "enchanted_obsidian": 64}', 18000, '{}', 36000),
('wither_chestplate', 'Wither Chestplate', 'LEGENDARY', 'CHESTPLATE', '{"defense": 185, "health": 230, "strength": 72, "intelligence": 95}', 'Infused with wither energy', 'Wither Impact: Deal wither damage over time', '{"nether_star": 6, "enchanted_obsidian": 128}', 30000, '{}', 60000),
('wither_leggings', 'Wither Leggings', 'LEGENDARY', 'LEGGINGS', '{"defense": 150, "health": 188, "strength": 58, "intelligence": 78}', 'Infused with wither energy', 'Wither Impact: Deal wither damage over time', '{"nether_star": 4, "enchanted_obsidian": 96}', 24000, '{}', 48000),
('wither_boots', 'Wither Boots', 'LEGENDARY', 'BOOTS', '{"defense": 105, "health": 132, "strength": 40, "intelligence": 52}', 'Infused with wither energy', 'Wither Impact: Deal wither damage over time', '{"nether_star": 2, "enchanted_obsidian": 48}', 16000, '{}', 32000),

('farmer_helmet', 'Farmer Helmet', 'UNCOMMON', 'HELMET', '{"defense": 25, "health": 40, "farming_fortune": 25}', 'Hardworking farmer gear', 'Green Thumb: +15% crop yield', '{"enchanted_bread": 32, "enchanted_carrot": 16}', 600, '{}', 1200),
('farmer_chestplate', 'Farmer Chestplate', 'UNCOMMON', 'CHESTPLATE', '{"defense": 42, "health": 65, "farming_fortune": 40}', 'Hardworking farmer gear', 'Green Thumb: +15% crop yield', '{"enchanted_bread": 64, "enchanted_carrot": 32}', 1000, '{}', 2000),
('farmer_leggings', 'Farmer Leggings', 'UNCOMMON', 'LEGGINGS', '{"defense": 34, "health": 52, "farming_fortune": 32}', 'Hardworking farmer gear', 'Green Thumb: +15% crop yield', '{"enchanted_bread": 48, "enchanted_carrot": 24}', 800, '{}', 1600),
('farmer_boots', 'Farmer Boots', 'UNCOMMON', 'BOOTS', '{"defense": 22, "health": 35, "farming_fortune": 20}', 'Hardworking farmer gear', 'Green Thumb: +15% crop yield', '{"enchanted_bread": 24, "enchanted_carrot": 12}', 500, '{}', 1000),

('miner_helmet', 'Miner Helmet', 'UNCOMMON', 'HELMET', '{"defense": 28, "health": 42, "mining_fortune": 20, "mining_speed": 15}', 'Dedicated miner equipment', 'Miners Fortune: +10% ore drops', '{"enchanted_cobblestone": 32, "enchanted_coal": 16}', 650, '{}', 1300),
('miner_chestplate', 'Miner Chestplate', 'UNCOMMON', 'CHESTPLATE', '{"defense": 46, "health": 68, "mining_fortune": 32, "mining_speed": 25}', 'Dedicated miner equipment', 'Miners Fortune: +10% ore drops', '{"enchanted_cobblestone": 64, "enchanted_coal": 32}', 1100, '{}', 2200),
('miner_leggings', 'Miner Leggings', 'UNCOMMON', 'LEGGINGS', '{"defense": 37, "health": 55, "mining_fortune": 26, "mining_speed": 20}', 'Dedicated miner equipment', 'Miners Fortune: +10% ore drops', '{"enchanted_cobblestone": 48, "enchanted_coal": 24}', 880, '{}', 1760),
('miner_boots', 'Miner Boots', 'UNCOMMON', 'BOOTS', '{"defense": 25, "health": 38, "mining_fortune": 18, "mining_speed": 12}', 'Dedicated miner equipment', 'Miners Fortune: +10% ore drops', '{"enchanted_cobblestone": 24, "enchanted_coal": 12}', 580, '{}', 1160),

('ranger_helmet', 'Ranger Helmet', 'RARE', 'HELMET', '{"defense": 38, "health": 58, "crit_chance": 11, "speed": 12, "foraging_fortune": 15}', 'Master of the wilderness', 'Eagle Eye: +25% projectile damage', '{"leather": 64, "enchanted_oak_wood": 16}', 1100, '{}', 2200),
('ranger_chestplate', 'Ranger Chestplate', 'RARE', 'CHESTPLATE', '{"defense": 65, "health": 92, "crit_chance": 16, "speed": 18, "foraging_fortune": 24}', 'Master of the wilderness', 'Eagle Eye: +25% projectile damage', '{"leather": 128, "enchanted_oak_wood": 32}', 1800, '{}', 3600),
('ranger_leggings', 'Ranger Leggings', 'RARE', 'LEGGINGS', '{"defense": 52, "health": 75, "crit_chance": 13, "speed": 15, "foraging_fortune": 20}', 'Master of the wilderness', 'Eagle Eye: +25% projectile damage', '{"leather": 96, "enchanted_oak_wood": 24}', 1440, '{}', 2880),
('ranger_boots', 'Ranger Boots', 'RARE', 'BOOTS', '{"defense": 36, "health": 52, "crit_chance": 9, "speed": 10, "foraging_fortune": 12}', 'Master of the wilderness', 'Eagle Eye: +25% projectile damage', '{"leather": 48, "enchanted_oak_wood": 12}', 950, '{}', 1900),

('ancient_helmet', 'Ancient Helmet', 'LEGENDARY', 'HELMET', '{"defense": 100, "health": 130, "strength": 35, "intelligence": 40, "magic_find": 12}', 'Relics of a forgotten age', 'Ancient Wisdom: All stats +5%', '{"enchanted_gold_block": 16, "enchanted_diamond_block": 8}', 14000, '{}', 28000),
('ancient_chestplate', 'Ancient Chestplate', 'LEGENDARY', 'CHESTPLATE', '{"defense": 165, "health": 205, "strength": 58, "intelligence": 65, "magic_find": 18}', 'Relics of a forgotten age', 'Ancient Wisdom: All stats +5%', '{"enchanted_gold_block": 32, "enchanted_diamond_block": 16}', 23500, '{}', 47000),
('ancient_leggings', 'Ancient Leggings', 'LEGENDARY', 'LEGGINGS', '{"defense": 133, "health": 168, "strength": 46, "intelligence": 52, "magic_find": 15}', 'Relics of a forgotten age', 'Ancient Wisdom: All stats +5%', '{"enchanted_gold_block": 24, "enchanted_diamond_block": 12}', 18800, '{}', 37600),
('ancient_boots', 'Ancient Boots', 'LEGENDARY', 'BOOTS', '{"defense": 93, "health": 118, "strength": 32, "intelligence": 36, "magic_find": 10}', 'Relics of a forgotten age', 'Ancient Wisdom: All stats +5%', '{"enchanted_gold_block": 12, "enchanted_diamond_block": 6}', 12500, '{}', 25000),

('reaper_helmet', 'Reaper Helmet', 'LEGENDARY', 'HELMET', '{"defense": 92, "health": 125, "strength": 50, "crit_damage": 40, "intelligence": 50}', 'Harbinger of death', 'Soul Reaper: Gain strength from kills', '{"enchanted_bone": 128, "nether_star": 2}', 14500, '{}', 29000),
('reaper_chestplate', 'Reaper Chestplate', 'LEGENDARY', 'CHESTPLATE', '{"defense": 152, "health": 198, "strength": 82, "crit_damage": 65, "intelligence": 82}', 'Harbinger of death', 'Soul Reaper: Gain strength from kills', '{"enchanted_bone": 256, "nether_star": 4}', 24500, '{}', 49000),
('reaper_leggings', 'Reaper Leggings', 'LEGENDARY', 'LEGGINGS', '{"defense": 122, "health": 162, "strength": 66, "crit_damage": 52, "intelligence": 66}', 'Harbinger of death', 'Soul Reaper: Gain strength from kills', '{"enchanted_bone": 192, "nether_star": 3}', 19600, '{}', 39200),
('reaper_boots', 'Reaper Boots', 'LEGENDARY', 'BOOTS', '{"defense": 85, "health": 114, "strength": 46, "crit_damage": 35, "intelligence": 46}', 'Harbinger of death', 'Soul Reaper: Gain strength from kills', '{"enchanted_bone": 96, "nether_star": 1}', 13000, '{}', 26000),

('holy_helmet', 'Holy Helmet', 'EPIC', 'HELMET', '{"defense": 72, "health": 95, "intelligence": 65, "true_defense": 8, "pet_luck": 5}', 'Blessed by divine light', 'Divine Shield: Absorb 20% damage taken', '{"enchanted_gold_block": 12, "enchanted_emerald_block": 6}', 5500, '{}', 11000),
('holy_chestplate', 'Holy Chestplate', 'EPIC', 'CHESTPLATE', '{"defense": 118, "health": 152, "intelligence": 105, "true_defense": 12, "pet_luck": 8}', 'Blessed by divine light', 'Divine Shield: Absorb 20% damage taken', '{"enchanted_gold_block": 24, "enchanted_emerald_block": 12}', 9200, '{}', 18400),
('holy_leggings', 'Holy Leggings', 'EPIC', 'LEGGINGS', '{"defense": 95, "health": 124, "intelligence": 86, "true_defense": 10, "pet_luck": 6}', 'Blessed by divine light', 'Divine Shield: Absorb 20% damage taken', '{"enchanted_gold_block": 18, "enchanted_emerald_block": 9}', 7400, '{}', 14800),
('holy_boots', 'Holy Boots', 'EPIC', 'BOOTS', '{"defense": 66, "health": 87, "intelligence": 57, "true_defense": 6, "pet_luck": 4}', 'Blessed by divine light', 'Divine Shield: Absorb 20% damage taken', '{"enchanted_gold_block": 9, "enchanted_emerald_block": 4}', 4900, '{}', 9800),

('storm_helmet', 'Storm Helmet', 'EPIC', 'HELMET', '{"defense": 68, "health": 88, "intelligence": 85, "speed": 15}', 'Command the lightning', 'Chain Lightning: Lightning strikes nearby enemies', '{"enchanted_diamond": 32, "enchanted_lapis_block": 16}', 5200, '{}', 10400),
('storm_chestplate', 'Storm Chestplate', 'EPIC', 'CHESTPLATE', '{"defense": 112, "health": 140, "intelligence": 138, "speed": 24}', 'Command the lightning', 'Chain Lightning: Lightning strikes nearby enemies', '{"enchanted_diamond": 64, "enchanted_lapis_block": 32}', 8800, '{}', 17600),
('storm_leggings', 'Storm Leggings', 'EPIC', 'LEGGINGS', '{"defense": 90, "health": 114, "intelligence": 112, "speed": 19}', 'Command the lightning', 'Chain Lightning: Lightning strikes nearby enemies', '{"enchanted_diamond": 48, "enchanted_lapis_block": 24}', 7000, '{}', 14000),
('storm_boots', 'Storm Boots', 'EPIC', 'BOOTS', '{"defense": 63, "health": 80, "intelligence": 75, "speed": 13}', 'Command the lightning', 'Chain Lightning: Lightning strikes nearby enemies', '{"enchanted_diamond": 24, "enchanted_lapis_block": 12}', 4700, '{}', 9400),

('demon_helmet', 'Demon Helmet', 'LEGENDARY', 'HELMET', '{"defense": 88, "health": 115, "strength": 55, "crit_damage": 45, "ferocity": 8}', 'Embrace demonic power', 'Demonic Rage: Gain ferocity on hit', '{"enchanted_blaze_rod": 64, "enchanted_magma_cream": 32}', 16000, '{}', 32000),
('demon_chestplate', 'Demon Chestplate', 'LEGENDARY', 'CHESTPLATE', '{"defense": 145, "health": 182, "strength": 90, "crit_damage": 72, "ferocity": 13}', 'Embrace demonic power', 'Demonic Rage: Gain ferocity on hit', '{"enchanted_blaze_rod": 128, "enchanted_magma_cream": 64}', 27000, '{}', 54000),
('demon_leggings', 'Demon Leggings', 'LEGENDARY', 'LEGGINGS', '{"defense": 117, "health": 149, "strength": 73, "crit_damage": 58, "ferocity": 10}', 'Embrace demonic power', 'Demonic Rage: Gain ferocity on hit', '{"enchanted_blaze_rod": 96, "enchanted_magma_cream": 48}', 21600, '{}', 43200),
('demon_boots', 'Demon Boots', 'LEGENDARY', 'BOOTS', '{"defense": 82, "health": 105, "strength": 50, "crit_damage": 40, "ferocity": 7}', 'Embrace demonic power', 'Demonic Rage: Gain ferocity on hit', '{"enchanted_blaze_rod": 48, "enchanted_magma_cream": 24}', 14400, '{}', 28800),

('celestial_helmet', 'Celestial Helmet', 'MYTHIC', 'HELMET', '{"defense": 125, "health": 160, "strength": 50, "intelligence": 80, "crit_damage": 35, "magic_find": 15}', 'Forged in the stars', 'Celestial Blessing: All stats +10%', '{"nether_star": 4, "enchanted_diamond_block": 16}', 25000, '{}', 50000),
('celestial_chestplate', 'Celestial Chestplate', 'MYTHIC', 'CHESTPLATE', '{"defense": 205, "health": 255, "strength": 82, "intelligence": 130, "crit_damage": 58, "magic_find": 24}', 'Forged in the stars', 'Celestial Blessing: All stats +10%', '{"nether_star": 8, "enchanted_diamond_block": 32}', 42000, '{}', 84000),
('celestial_leggings', 'Celestial Leggings', 'MYTHIC', 'LEGGINGS', '{"defense": 165, "health": 208, "strength": 66, "intelligence": 106, "crit_damage": 46, "magic_find": 19}', 'Forged in the stars', 'Celestial Blessing: All stats +10%', '{"nether_star": 6, "enchanted_diamond_block": 24}', 33600, '{}', 67200),
('celestial_boots', 'Celestial Boots', 'MYTHIC', 'BOOTS', '{"defense": 115, "health": 146, "strength": 46, "intelligence": 74, "crit_damage": 32, "magic_find": 13}', 'Forged in the stars', 'Celestial Blessing: All stats +10%', '{"nether_star": 3, "enchanted_diamond_block": 12}', 22400, '{}', 44800);

INSERT OR REPLACE INTO armor_stats (item_id, defense, health, strength, crit_chance, crit_damage, intelligence, speed, magic_find, pet_luck, true_defense)
VALUES
('steel_helmet', 30, 35, 0, 0, 0, 0, 0, 0, 0, 0),
('steel_chestplate', 50, 60, 0, 0, 0, 0, 0, 0, 0, 0),
('steel_leggings', 40, 45, 0, 0, 0, 0, 0, 0, 0, 0),
('steel_boots', 25, 30, 0, 0, 0, 0, 0, 0, 0, 0),

('emerald_helmet', 40, 50, 0, 0, 0, 0, 0, 5, 0, 0),
('emerald_chestplate', 70, 80, 0, 0, 0, 0, 0, 10, 0, 0),
('emerald_leggings', 55, 65, 0, 0, 0, 0, 0, 8, 0, 0),
('emerald_boots', 35, 45, 0, 0, 0, 0, 0, 5, 0, 0),

('obsidian_helmet', 60, 70, 0, 0, 0, 0, 0, 0, 0, 5),
('obsidian_chestplate', 100, 110, 0, 0, 0, 0, 0, 0, 0, 10),
('obsidian_leggings', 80, 90, 0, 0, 0, 0, 0, 0, 0, 8),
('obsidian_boots', 50, 60, 0, 0, 0, 0, 0, 0, 0, 5),

('mithril_helmet', 80, 100, 0, 0, 0, 0, 0, 0, 0, 0),
('mithril_chestplate', 130, 150, 0, 0, 0, 0, 0, 0, 0, 0),
('mithril_leggings', 105, 125, 0, 0, 0, 0, 0, 0, 0, 0),
('mithril_boots', 70, 85, 0, 0, 0, 0, 0, 0, 0, 0),

('titanium_helmet', 90, 110, 15, 0, 0, 0, 0, 0, 0, 0),
('titanium_chestplate', 145, 170, 25, 0, 0, 0, 0, 0, 0, 0),
('titanium_leggings', 115, 140, 20, 0, 0, 0, 0, 0, 0, 0),
('titanium_boots', 80, 95, 12, 0, 0, 0, 0, 0, 0, 0),

('dragon_helmet', 120, 150, 30, 0, 15, 0, 0, 0, 0, 0),
('dragon_chestplate', 190, 230, 50, 0, 25, 0, 0, 0, 0, 0),
('dragon_leggings', 155, 190, 40, 0, 20, 0, 0, 0, 0, 0),
('dragon_boots', 110, 130, 25, 0, 12, 0, 0, 0, 0, 0),

('necromancer_helmet', 100, 140, 0, 0, 0, 80, 0, 0, 0, 0),
('necromancer_chestplate', 160, 210, 0, 0, 0, 130, 0, 0, 0, 0),
('necromancer_leggings', 130, 175, 0, 0, 0, 105, 0, 0, 0, 0),
('necromancer_boots', 90, 120, 0, 0, 0, 70, 0, 0, 0, 0),

('blaze_helmet', 70, 90, 25, 0, 0, 40, 0, 0, 0, 0),
('blaze_chestplate', 115, 140, 40, 0, 0, 65, 0, 0, 0, 0),
('blaze_leggings', 92, 115, 32, 0, 0, 52, 0, 0, 0, 0),
('blaze_boots', 65, 80, 22, 0, 0, 35, 0, 0, 0, 0),

('shadow_helmet', 75, 95, 0, 8, 0, 0, 15, 0, 0, 0),
('shadow_chestplate', 120, 145, 0, 12, 0, 0, 25, 0, 0, 0),
('shadow_leggings', 95, 120, 0, 10, 0, 0, 20, 0, 0, 0),
('shadow_boots', 68, 85, 0, 6, 0, 0, 12, 0, 0, 0),

('crystal_helmet', 65, 85, 0, 0, 0, 70, 0, 10, 0, 0),
('crystal_chestplate', 110, 135, 0, 0, 0, 110, 0, 16, 0, 0),
('crystal_leggings', 88, 110, 0, 0, 0, 90, 0, 13, 0, 0),
('crystal_boots', 62, 78, 0, 0, 0, 60, 0, 8, 0, 0),

('berserker_helmet', 45, 65, 35, 0, 25, 0, 0, 0, 0, 0),
('berserker_chestplate', 75, 100, 55, 0, 40, 0, 0, 0, 0, 0),
('berserker_leggings', 60, 82, 45, 0, 32, 0, 0, 0, 0, 0),
('berserker_boots', 42, 58, 30, 0, 20, 0, 0, 0, 0, 0),

('glacial_helmet', 50, 70, 0, 0, 0, 45, -5, 0, 0, 0),
('glacial_chestplate', 85, 110, 0, 0, 0, 70, -8, 0, 0, 0),
('glacial_leggings', 68, 90, 0, 0, 0, 58, -6, 0, 0, 0),
('glacial_boots', 48, 65, 0, 0, 0, 40, -4, 0, 0, 0),

('paladin_helmet', 85, 110, 20, 0, 0, 0, 0, 0, 0, 8),
('paladin_chestplate', 140, 175, 32, 0, 0, 0, 0, 0, 0, 12),
('paladin_leggings', 112, 142, 26, 0, 0, 0, 0, 0, 0, 10),
('paladin_boots', 78, 98, 18, 0, 0, 0, 0, 0, 0, 6),

('hunter_helmet', 40, 60, 0, 12, 0, 0, 10, 0, 0, 0),
('hunter_chestplate', 68, 95, 0, 18, 0, 0, 16, 0, 0, 0),
('hunter_leggings', 54, 78, 0, 15, 0, 0, 13, 0, 0, 0),
('hunter_boots', 38, 55, 0, 10, 0, 0, 8, 0, 0, 0),

('warlock_helmet', 60, 80, 0, 0, 0, 100, 0, 0, 0, 0),
('warlock_chestplate', 100, 125, 0, 0, 0, 160, 0, 0, 0, 0),
('warlock_leggings', 80, 102, 0, 0, 0, 130, 0, 0, 0, 0),
('warlock_boots', 55, 72, 0, 0, 0, 85, 0, 0, 0, 0),

('assassin_helmet', 35, 50, 0, 15, 30, 0, 18, 0, 0, 0),
('assassin_chestplate', 60, 80, 0, 22, 48, 0, 28, 0, 0, 0),
('assassin_leggings', 48, 65, 0, 18, 38, 0, 23, 0, 0, 0),
('assassin_boots', 32, 45, 0, 12, 25, 0, 15, 0, 0, 0),

('tank_helmet', 110, 140, 0, 0, 0, 0, 0, 0, 0, 12),
('tank_chestplate', 180, 220, 0, 0, 0, 0, 0, 0, 0, 18),
('tank_leggings', 145, 180, 0, 0, 0, 0, 0, 0, 0, 15),
('tank_boots', 100, 125, 0, 0, 0, 0, 0, 0, 0, 10),

('ender_helmet', 70, 90, 0, 0, 0, 60, 25, 0, 0, 0),
('ender_chestplate', 115, 140, 0, 0, 0, 95, 40, 0, 0, 0),
('ender_leggings', 92, 115, 0, 0, 0, 78, 32, 0, 0, 0),
('ender_boots', 65, 80, 0, 0, 0, 52, 22, 0, 0, 0),

('phoenix_helmet', 95, 120, 40, 0, 0, 50, 0, 0, 0, 0),
('phoenix_chestplate', 155, 190, 65, 0, 0, 80, 0, 0, 0, 0),
('phoenix_leggings', 125, 155, 52, 0, 0, 65, 0, 0, 0, 0),
('phoenix_boots', 88, 110, 35, 0, 0, 45, 0, 0, 0, 0),

('samurai_helmet', 55, 75, 28, 10, 0, 0, 0, 0, 0, 0),
('samurai_chestplate', 90, 115, 45, 15, 0, 0, 0, 0, 0, 0),
('samurai_leggings', 72, 95, 36, 12, 0, 0, 0, 0, 0, 0),
('samurai_boots', 50, 68, 25, 8, 0, 0, 0, 0, 0, 0),

('void_helmet', 105, 130, 0, 0, 0, 90, 0, 0, 0, 10),
('void_chestplate', 170, 205, 0, 0, 0, 145, 0, 0, 0, 16),
('void_leggings', 138, 168, 0, 0, 0, 118, 0, 0, 0, 13),
('void_boots', 95, 118, 0, 0, 0, 78, 0, 0, 0, 8),

('fairy_helmet', 55, 75, 0, 0, 0, 55, 20, 8, 0, 0),
('fairy_chestplate', 92, 118, 0, 0, 0, 88, 32, 12, 0, 0),
('fairy_leggings', 74, 96, 0, 0, 0, 72, 26, 10, 0, 0),
('fairy_boots', 52, 68, 0, 0, 0, 48, 18, 6, 0, 0),

('wither_helmet', 115, 145, 45, 0, 0, 60, 0, 0, 0, 0),
('wither_chestplate', 185, 230, 72, 0, 0, 95, 0, 0, 0, 0),
('wither_leggings', 150, 188, 58, 0, 0, 78, 0, 0, 0, 0),
('wither_boots', 105, 132, 40, 0, 0, 52, 0, 0, 0, 0),

('farmer_helmet', 25, 40, 0, 0, 0, 0, 0, 0, 0, 0),
('farmer_chestplate', 42, 65, 0, 0, 0, 0, 0, 0, 0, 0),
('farmer_leggings', 34, 52, 0, 0, 0, 0, 0, 0, 0, 0),
('farmer_boots', 22, 35, 0, 0, 0, 0, 0, 0, 0, 0),

('miner_helmet', 28, 42, 0, 0, 0, 0, 0, 0, 0, 0),
('miner_chestplate', 46, 68, 0, 0, 0, 0, 0, 0, 0, 0),
('miner_leggings', 37, 55, 0, 0, 0, 0, 0, 0, 0, 0),
('miner_boots', 25, 38, 0, 0, 0, 0, 0, 0, 0, 0),

('ranger_helmet', 38, 58, 0, 11, 0, 0, 12, 0, 0, 0),
('ranger_chestplate', 65, 92, 0, 16, 0, 0, 18, 0, 0, 0),
('ranger_leggings', 52, 75, 0, 13, 0, 0, 15, 0, 0, 0),
('ranger_boots', 36, 52, 0, 9, 0, 0, 10, 0, 0, 0),

('ancient_helmet', 100, 130, 35, 0, 0, 40, 0, 12, 0, 0),
('ancient_chestplate', 165, 205, 58, 0, 0, 65, 0, 18, 0, 0),
('ancient_leggings', 133, 168, 46, 0, 0, 52, 0, 15, 0, 0),
('ancient_boots', 93, 118, 32, 0, 0, 36, 0, 10, 0, 0),

('reaper_helmet', 92, 125, 50, 0, 40, 50, 0, 0, 0, 0),
('reaper_chestplate', 152, 198, 82, 0, 65, 82, 0, 0, 0, 0),
('reaper_leggings', 122, 162, 66, 0, 52, 66, 0, 0, 0, 0),
('reaper_boots', 85, 114, 46, 0, 35, 46, 0, 0, 0, 0),

('holy_helmet', 72, 95, 0, 0, 0, 65, 0, 0, 5, 8),
('holy_chestplate', 118, 152, 0, 0, 0, 105, 0, 0, 8, 12),
('holy_leggings', 95, 124, 0, 0, 0, 86, 0, 0, 6, 10),
('holy_boots', 66, 87, 0, 0, 0, 57, 0, 0, 4, 6),

('storm_helmet', 68, 88, 0, 0, 0, 85, 15, 0, 0, 0),
('storm_chestplate', 112, 140, 0, 0, 0, 138, 24, 0, 0, 0),
('storm_leggings', 90, 114, 0, 0, 0, 112, 19, 0, 0, 0),
('storm_boots', 63, 80, 0, 0, 0, 75, 13, 0, 0, 0),

('demon_helmet', 88, 115, 55, 0, 45, 0, 0, 0, 0, 0),
('demon_chestplate', 145, 182, 90, 0, 72, 0, 0, 0, 0, 0),
('demon_leggings', 117, 149, 73, 0, 58, 0, 0, 0, 0, 0),
('demon_boots', 82, 105, 50, 0, 40, 0, 0, 0, 0, 0),

('celestial_helmet', 125, 160, 50, 0, 35, 80, 0, 15, 0, 0),
('celestial_chestplate', 205, 255, 82, 0, 58, 130, 0, 24, 0, 0),
('celestial_leggings', 165, 208, 66, 0, 46, 106, 0, 19, 0, 0),
('celestial_boots', 115, 146, 46, 0, 32, 74, 0, 13, 0, 0);

INSERT OR IGNORE INTO crafting_recipes (recipe_id, output_item, ingredients, output_amount)
VALUES
('steel_helmet_recipe', 'steel_helmet', '{"enchanted_iron": 8, "iron_ingot": 16}', 1),
('steel_chestplate_recipe', 'steel_chestplate', '{"enchanted_iron": 16, "iron_ingot": 32}', 1),
('steel_leggings_recipe', 'steel_leggings', '{"enchanted_iron": 12, "iron_ingot": 24}', 1),
('steel_boots_recipe', 'steel_boots', '{"enchanted_iron": 6, "iron_ingot": 12}', 1),

('emerald_helmet_recipe', 'emerald_helmet', '{"enchanted_emerald": 16, "emerald": 32}', 1),
('emerald_chestplate_recipe', 'emerald_chestplate', '{"enchanted_emerald": 32, "emerald": 64}', 1),
('emerald_leggings_recipe', 'emerald_leggings', '{"enchanted_emerald": 24, "emerald": 48}', 1),
('emerald_boots_recipe', 'emerald_boots', '{"enchanted_emerald": 12, "emerald": 24}', 1),

('obsidian_helmet_recipe', 'obsidian_helmet', '{"enchanted_obsidian": 8, "obsidian": 64}', 1),
('obsidian_chestplate_recipe', 'obsidian_chestplate', '{"enchanted_obsidian": 16, "obsidian": 128}', 1),
('obsidian_leggings_recipe', 'obsidian_leggings', '{"enchanted_obsidian": 12, "obsidian": 96}', 1),
('obsidian_boots_recipe', 'obsidian_boots', '{"enchanted_obsidian": 6, "obsidian": 48}', 1),

('mithril_helmet_recipe', 'mithril_helmet', '{"refined_mithril": 4, "mithril": 64}', 1),
('mithril_chestplate_recipe', 'mithril_chestplate', '{"refined_mithril": 8, "mithril": 128}', 1),
('mithril_leggings_recipe', 'mithril_leggings', '{"refined_mithril": 6, "mithril": 96}', 1),
('mithril_boots_recipe', 'mithril_boots', '{"refined_mithril": 3, "mithril": 48}', 1),

('titanium_helmet_recipe', 'titanium_helmet', '{"refined_titanium": 4, "titanium": 64}', 1),
('titanium_chestplate_recipe', 'titanium_chestplate', '{"refined_titanium": 8, "titanium": 128}', 1),
('titanium_leggings_recipe', 'titanium_leggings', '{"refined_titanium": 6, "titanium": 96}', 1),
('titanium_boots_recipe', 'titanium_boots', '{"refined_titanium": 3, "titanium": 48}', 1),

('dragon_helmet_recipe', 'dragon_helmet', '{"dragon_scale": 16, "enchanted_diamond_block": 8}', 1),
('dragon_chestplate_recipe', 'dragon_chestplate', '{"dragon_scale": 32, "enchanted_diamond_block": 16}', 1),
('dragon_leggings_recipe', 'dragon_leggings', '{"dragon_scale": 24, "enchanted_diamond_block": 12}', 1),
('dragon_boots_recipe', 'dragon_boots', '{"dragon_scale": 12, "enchanted_diamond_block": 6}', 1),

('necromancer_helmet_recipe', 'necromancer_helmet', '{"nether_star": 2, "enchanted_bone": 128}', 1),
('necromancer_chestplate_recipe', 'necromancer_chestplate', '{"nether_star": 4, "enchanted_bone": 256}', 1),
('necromancer_leggings_recipe', 'necromancer_leggings', '{"nether_star": 3, "enchanted_bone": 192}', 1),
('necromancer_boots_recipe', 'necromancer_boots', '{"nether_star": 1, "enchanted_bone": 96}', 1),

('blaze_helmet_recipe', 'blaze_helmet', '{"enchanted_blaze_rod": 32, "blaze_powder": 64}', 1),
('blaze_chestplate_recipe', 'blaze_chestplate', '{"enchanted_blaze_rod": 64, "blaze_powder": 128}', 1),
('blaze_leggings_recipe', 'blaze_leggings', '{"enchanted_blaze_rod": 48, "blaze_powder": 96}', 1),
('blaze_boots_recipe', 'blaze_boots', '{"enchanted_blaze_rod": 24, "blaze_powder": 48}', 1),

('shadow_helmet_recipe', 'shadow_helmet', '{"enchanted_obsidian": 16, "ender_pearl": 64}', 1),
('shadow_chestplate_recipe', 'shadow_chestplate', '{"enchanted_obsidian": 32, "ender_pearl": 128}', 1),
('shadow_leggings_recipe', 'shadow_leggings', '{"enchanted_obsidian": 24, "ender_pearl": 96}', 1),
('shadow_boots_recipe', 'shadow_boots', '{"enchanted_obsidian": 12, "ender_pearl": 48}', 1),

('crystal_helmet_recipe', 'crystal_helmet', '{"enchanted_diamond": 32, "enchanted_emerald": 16}', 1),
('crystal_chestplate_recipe', 'crystal_chestplate', '{"enchanted_diamond": 64, "enchanted_emerald": 32}', 1),
('crystal_leggings_recipe', 'crystal_leggings', '{"enchanted_diamond": 48, "enchanted_emerald": 24}', 1),
('crystal_boots_recipe', 'crystal_boots', '{"enchanted_diamond": 24, "enchanted_emerald": 12}', 1),

('berserker_helmet_recipe', 'berserker_helmet', '{"enchanted_iron_block": 8, "enchanted_gold": 16}', 1),
('berserker_chestplate_recipe', 'berserker_chestplate', '{"enchanted_iron_block": 16, "enchanted_gold": 32}', 1),
('berserker_leggings_recipe', 'berserker_leggings', '{"enchanted_iron_block": 12, "enchanted_gold": 24}', 1),
('berserker_boots_recipe', 'berserker_boots', '{"enchanted_iron_block": 6, "enchanted_gold": 12}', 1),

('glacial_helmet_recipe', 'glacial_helmet', '{"enchanted_ice": 32, "enchanted_diamond": 8}', 1),
('glacial_chestplate_recipe', 'glacial_chestplate', '{"enchanted_ice": 64, "enchanted_diamond": 16}', 1),
('glacial_leggings_recipe', 'glacial_leggings', '{"enchanted_ice": 48, "enchanted_diamond": 12}', 1),
('glacial_boots_recipe', 'glacial_boots', '{"enchanted_ice": 24, "enchanted_diamond": 6}', 1),

('paladin_helmet_recipe', 'paladin_helmet', '{"enchanted_gold_block": 8, "enchanted_diamond": 32}', 1),
('paladin_chestplate_recipe', 'paladin_chestplate', '{"enchanted_gold_block": 16, "enchanted_diamond": 64}', 1),
('paladin_leggings_recipe', 'paladin_leggings', '{"enchanted_gold_block": 12, "enchanted_diamond": 48}', 1),
('paladin_boots_recipe', 'paladin_boots', '{"enchanted_gold_block": 6, "enchanted_diamond": 24}', 1),

('hunter_helmet_recipe', 'hunter_helmet', '{"leather": 64, "enchanted_string": 16}', 1),
('hunter_chestplate_recipe', 'hunter_chestplate', '{"leather": 128, "enchanted_string": 32}', 1),
('hunter_leggings_recipe', 'hunter_leggings', '{"leather": 96, "enchanted_string": 24}', 1),
('hunter_boots_recipe', 'hunter_boots', '{"leather": 48, "enchanted_string": 12}', 1),

('warlock_helmet_recipe', 'warlock_helmet', '{"enchanted_obsidian": 16, "nether_star": 1}', 1),
('warlock_chestplate_recipe', 'warlock_chestplate', '{"enchanted_obsidian": 32, "nether_star": 2}', 1),
('warlock_leggings_recipe', 'warlock_leggings', '{"enchanted_obsidian": 24, "nether_star": 1}', 1),
('warlock_boots_recipe', 'warlock_boots', '{"enchanted_obsidian": 12, "nether_star": 1}', 1),

('assassin_helmet_recipe', 'assassin_helmet', '{"enchanted_string": 32, "ender_pearl": 32}', 1),
('assassin_chestplate_recipe', 'assassin_chestplate', '{"enchanted_string": 64, "ender_pearl": 64}', 1),
('assassin_leggings_recipe', 'assassin_leggings', '{"enchanted_string": 48, "ender_pearl": 48}', 1),
('assassin_boots_recipe', 'assassin_boots', '{"enchanted_string": 24, "ender_pearl": 24}', 1),

('tank_helmet_recipe', 'tank_helmet', '{"enchanted_iron_block": 16, "enchanted_obsidian": 8}', 1),
('tank_chestplate_recipe', 'tank_chestplate', '{"enchanted_iron_block": 32, "enchanted_obsidian": 16}', 1),
('tank_leggings_recipe', 'tank_leggings', '{"enchanted_iron_block": 24, "enchanted_obsidian": 12}', 1),
('tank_boots_recipe', 'tank_boots', '{"enchanted_iron_block": 12, "enchanted_obsidian": 6}', 1),

('ender_helmet_recipe', 'ender_helmet', '{"enchanted_ender_pearl": 32, "enchanted_eye_of_ender": 16}', 1),
('ender_chestplate_recipe', 'ender_chestplate', '{"enchanted_ender_pearl": 64, "enchanted_eye_of_ender": 32}', 1),
('ender_leggings_recipe', 'ender_leggings', '{"enchanted_ender_pearl": 48, "enchanted_eye_of_ender": 24}', 1),
('ender_boots_recipe', 'ender_boots', '{"enchanted_ender_pearl": 24, "enchanted_eye_of_ender": 12}', 1),

('phoenix_helmet_recipe', 'phoenix_helmet', '{"enchanted_blaze_rod": 64, "nether_star": 2}', 1),
('phoenix_chestplate_recipe', 'phoenix_chestplate', '{"enchanted_blaze_rod": 128, "nether_star": 4}', 1),
('phoenix_leggings_recipe', 'phoenix_leggings', '{"enchanted_blaze_rod": 96, "nether_star": 3}', 1),
('phoenix_boots_recipe', 'phoenix_boots', '{"enchanted_blaze_rod": 48, "nether_star": 1}', 1),

('samurai_helmet_recipe', 'samurai_helmet', '{"enchanted_iron_block": 12, "enchanted_string": 32}', 1),
('samurai_chestplate_recipe', 'samurai_chestplate', '{"enchanted_iron_block": 24, "enchanted_string": 64}', 1),
('samurai_leggings_recipe', 'samurai_leggings', '{"enchanted_iron_block": 18, "enchanted_string": 48}', 1),
('samurai_boots_recipe', 'samurai_boots', '{"enchanted_iron_block": 9, "enchanted_string": 24}', 1),

('void_helmet_recipe', 'void_helmet', '{"enchanted_obsidian": 32, "enchanted_ender_pearl": 32}', 1),
('void_chestplate_recipe', 'void_chestplate', '{"enchanted_obsidian": 64, "enchanted_ender_pearl": 64}', 1),
('void_leggings_recipe', 'void_leggings', '{"enchanted_obsidian": 48, "enchanted_ender_pearl": 48}', 1),
('void_boots_recipe', 'void_boots', '{"enchanted_obsidian": 24, "enchanted_ender_pearl": 24}', 1),

('fairy_helmet_recipe', 'fairy_helmet', '{"enchanted_diamond": 16, "enchanted_emerald": 32}', 1),
('fairy_chestplate_recipe', 'fairy_chestplate', '{"enchanted_diamond": 32, "enchanted_emerald": 64}', 1),
('fairy_leggings_recipe', 'fairy_leggings', '{"enchanted_diamond": 24, "enchanted_emerald": 48}', 1),
('fairy_boots_recipe', 'fairy_boots', '{"enchanted_diamond": 12, "enchanted_emerald": 24}', 1),

('wither_helmet_recipe', 'wither_helmet', '{"nether_star": 3, "enchanted_obsidian": 64}', 1),
('wither_chestplate_recipe', 'wither_chestplate', '{"nether_star": 6, "enchanted_obsidian": 128}', 1),
('wither_leggings_recipe', 'wither_leggings', '{"nether_star": 4, "enchanted_obsidian": 96}', 1),
('wither_boots_recipe', 'wither_boots', '{"nether_star": 2, "enchanted_obsidian": 48}', 1),

('farmer_helmet_recipe', 'farmer_helmet', '{"enchanted_bread": 32, "enchanted_carrot": 16}', 1),
('farmer_chestplate_recipe', 'farmer_chestplate', '{"enchanted_bread": 64, "enchanted_carrot": 32}', 1),
('farmer_leggings_recipe', 'farmer_leggings', '{"enchanted_bread": 48, "enchanted_carrot": 24}', 1),
('farmer_boots_recipe', 'farmer_boots', '{"enchanted_bread": 24, "enchanted_carrot": 12}', 1),

('miner_helmet_recipe', 'miner_helmet', '{"enchanted_cobblestone": 32, "enchanted_coal": 16}', 1),
('miner_chestplate_recipe', 'miner_chestplate', '{"enchanted_cobblestone": 64, "enchanted_coal": 32}', 1),
('miner_leggings_recipe', 'miner_leggings', '{"enchanted_cobblestone": 48, "enchanted_coal": 24}', 1),
('miner_boots_recipe', 'miner_boots', '{"enchanted_cobblestone": 24, "enchanted_coal": 12}', 1),

('ranger_helmet_recipe', 'ranger_helmet', '{"leather": 64, "enchanted_oak_wood": 16}', 1),
('ranger_chestplate_recipe', 'ranger_chestplate', '{"leather": 128, "enchanted_oak_wood": 32}', 1),
('ranger_leggings_recipe', 'ranger_leggings', '{"leather": 96, "enchanted_oak_wood": 24}', 1),
('ranger_boots_recipe', 'ranger_boots', '{"leather": 48, "enchanted_oak_wood": 12}', 1),

('ancient_helmet_recipe', 'ancient_helmet', '{"enchanted_gold_block": 16, "enchanted_diamond_block": 8}', 1),
('ancient_chestplate_recipe', 'ancient_chestplate', '{"enchanted_gold_block": 32, "enchanted_diamond_block": 16}', 1),
('ancient_leggings_recipe', 'ancient_leggings', '{"enchanted_gold_block": 24, "enchanted_diamond_block": 12}', 1),
('ancient_boots_recipe', 'ancient_boots', '{"enchanted_gold_block": 12, "enchanted_diamond_block": 6}', 1),

('reaper_helmet_recipe', 'reaper_helmet', '{"enchanted_bone": 128, "nether_star": 2}', 1),
('reaper_chestplate_recipe', 'reaper_chestplate', '{"enchanted_bone": 256, "nether_star": 4}', 1),
('reaper_leggings_recipe', 'reaper_leggings', '{"enchanted_bone": 192, "nether_star": 3}', 1),
('reaper_boots_recipe', 'reaper_boots', '{"enchanted_bone": 96, "nether_star": 1}', 1),

('holy_helmet_recipe', 'holy_helmet', '{"enchanted_gold_block": 12, "enchanted_emerald_block": 6}', 1),
('holy_chestplate_recipe', 'holy_chestplate', '{"enchanted_gold_block": 24, "enchanted_emerald_block": 12}', 1),
('holy_leggings_recipe', 'holy_leggings', '{"enchanted_gold_block": 18, "enchanted_emerald_block": 9}', 1),
('holy_boots_recipe', 'holy_boots', '{"enchanted_gold_block": 9, "enchanted_emerald_block": 4}', 1),

('storm_helmet_recipe', 'storm_helmet', '{"enchanted_diamond": 32, "enchanted_lapis_block": 16}', 1),
('storm_chestplate_recipe', 'storm_chestplate', '{"enchanted_diamond": 64, "enchanted_lapis_block": 32}', 1),
('storm_leggings_recipe', 'storm_leggings', '{"enchanted_diamond": 48, "enchanted_lapis_block": 24}', 1),
('storm_boots_recipe', 'storm_boots', '{"enchanted_diamond": 24, "enchanted_lapis_block": 12}', 1),

('demon_helmet_recipe', 'demon_helmet', '{"enchanted_blaze_rod": 64, "enchanted_magma_cream": 32}', 1),
('demon_chestplate_recipe', 'demon_chestplate', '{"enchanted_blaze_rod": 128, "enchanted_magma_cream": 64}', 1),
('demon_leggings_recipe', 'demon_leggings', '{"enchanted_blaze_rod": 96, "enchanted_magma_cream": 48}', 1),
('demon_boots_recipe', 'demon_boots', '{"enchanted_blaze_rod": 48, "enchanted_magma_cream": 24}', 1),

('celestial_helmet_recipe', 'celestial_helmet', '{"nether_star": 4, "enchanted_diamond_block": 16}', 1),
('celestial_chestplate_recipe', 'celestial_chestplate', '{"nether_star": 8, "enchanted_diamond_block": 32}', 1),
('celestial_leggings_recipe', 'celestial_leggings', '{"nether_star": 6, "enchanted_diamond_block": 24}', 1),
('celestial_boots_recipe', 'celestial_boots', '{"nether_star": 3, "enchanted_diamond_block": 12}', 1);
