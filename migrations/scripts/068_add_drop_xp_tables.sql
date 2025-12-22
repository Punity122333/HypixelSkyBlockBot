-- Resetting to make sure the new scaling is clean
DROP TABLE IF EXISTS combat_drop_xp;
DROP TABLE IF EXISTS gathering_drop_xp;

CREATE TABLE combat_drop_xp (
    item_id TEXT PRIMARY KEY,
    base_xp INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE gathering_drop_xp (
    item_id TEXT PRIMARY KEY,
    base_xp INTEGER NOT NULL DEFAULT 0
);

-- Combat XP scaled to match the new 15-20 XP "basic" floor
INSERT INTO combat_drop_xp (item_id, base_xp) VALUES
('rotten_flesh', 15),
('bone', 18),
('string', 16),
('spider_eye', 25),
('gunpowder', 30),
('ender_pearl', 75),
('slime_ball', 20),
('magma_cream', 50),
('blaze_rod', 100),
('ghast_tear', 120),
('wither_skeleton_skull', 400),
('dragon_fragment', 1500),
('summoning_eye', 800),
('revenant_flesh', 150),
('tarantula_web', 160),
('wolf_tooth', 180),
('iron_ingot', 20), -- Matched to your mining map
('gold_ingot', 30), -- Matched to your mining map
('diamond', 50),    -- Matched to your mining map
('emerald', 45),
('enchanted_rotten_flesh', 150),
('enchanted_bone', 180),
('enchanted_string', 160),
('enchanted_spider_eye', 250),
('enchanted_gunpowder', 300),
('enchanted_ender_pearl', 750),
('enchanted_slime_ball', 200),
('enchanted_magma_cream', 500),
('enchanted_blaze_rod', 700),
('enchanted_ghast_tear', 800),
('enchanted_wither_skeleton_skull', 2000),
('enchanted_dragon_fragment', 3000),
('enchanted_summoning_eye', 1800),
('enchanted_revenant_flesh', 250),
('enchanted_tarantula_web', 260),
('enchanted_wolf_tooth', 280),
('enchanted_gold', 300),
('enchanted_iron', 200),
('enchanted_diamond', 500),
('enchanted_emerald', 450),
('zombie_heart', 200),
('skeleton_master_fragment', 250),
('spider_catalyst', 300),
('creeper_essence', 200),
('enderman_cortex', 500),
('slime_essence', 100),
('cave_spider_venom', 180),
('pigman_blade', 600),
('blaze_heart', 800),
('ghast_core', 1000),
('magma_chunk', 400),
('wither_bone', 1200),
('zealot_fragment', 900),
('dragon_scale', 2500),
('piglin_tusk', 650),
('arrow', 2),
('flint', 3),
('feather', 3),
('hamster_wheel', 40),
('beheaded_horror', 250),
('fly_swatter', 180),
('aspect_of_the_end', 500),
('zombie_sword', 150),
('skeleton_master_helmet', 300),
('tarantula_helmet', 400),
('scorpion_foil', 450),
('overflux_capacitor', 600),
('blaze_helmet', 400),
('revenant_catalyst', 350),
('snake_rune', 500),
('scythe_blade', 800),
('toxic_arrow_poison', 200),
('null_sphere', 400),
('void_conqueror_enderman_skin', 500),
('judgement_core', 1000),
('endersnake_rune', 800),
('couture_rune', 800),
('grizzly_bait', 250),
('golden_tooth', 180),
('spirit_bone', 300),
('wither_blood', 800),
('enchanted_eye_of_ender', 600),
('aspect_of_the_dragons', 1200),
('ender_dragon_pet', 2000),
('fire_stone', 250),
('molten_cube', 400),
('infernal_kuudra_key', 1500),
('golden_carrot', 60),
('enchanted_baked_potato', 250);

-- Gathering XP scaled using your Mining/Farming/Foraging anchors
INSERT INTO gathering_drop_xp (item_id, base_xp) VALUES
('cobblestone', 10), -- Anchor
('coal', 15),        -- Anchor
('iron_ingot', 20),  -- Anchor
('gold_ingot', 30),  -- Anchor
('diamond', 50),     -- Anchor
('iron_ore', 25),    -- Scaled slightly higher than ingots for mining effort
('gold_ore', 35),
('diamond_ore', 65),
('emerald_ore', 60),
('emerald', 45),
('lapis_lazuli', 15),
('redstone', 12),
('enchanted_cobblestone', 100),
('enchanted_coal', 150),
('enchanted_iron', 200),
('enchanted_gold', 300),
('enchanted_diamond', 500),
('enchanted_emerald', 450),
('enchanted_lapis', 150),
('enchanted_redstone', 120),
('wheat', 15),       -- Anchor
('carrot', 15),      -- Anchor
('potato', 20),      -- Anchor
('sugar_cane', 25),  -- Anchor
('pumpkin', 30),     -- Anchor
('melon', 40),       -- Anchor
('cactus', 20),
('nether_wart', 25),
('enchanted_wheat', 150),
('enchanted_carrot', 150),
('enchanted_potato', 200),
('enchanted_sugar_cane', 250),
('enchanted_pumpkin', 300),
('enchanted_melon', 400),
('enchanted_cactus', 200),
('hay_bale', 135),
('enchanted_hay_bale', 1350),
('oak_wood', 20),      -- Anchor
('jungle_wood', 30),   -- Anchor
('dark_oak_wood', 40), -- Anchor
('spruce_wood', 25),
('birch_wood', 20),
('acacia_wood', 35),
('enchanted_oak_wood', 200),
('enchanted_spruce_wood', 250),
('enchanted_birch_wood', 200),
('enchanted_jungle_wood', 300),
('enchanted_acacia_wood', 350),
('enchanted_dark_oak_wood', 400),
('stick', 5),
('raw_fish', 30),
('raw_salmon', 40),
('clownfish', 80),
('pufferfish', 120),
('tropical_fish', 100),
('enchanted_raw_fish', 300),
('enchanted_salmon', 400),
('enchanted_clownfish', 800),
('enchanted_pufferfish', 1200),
('prismarine_shard', 60),
('prismarine_crystals', 80),
('sponge', 250),
('lily_pad', 40),
('sea_lantern', 150),
('ink_sac', 25),
('enchanted_ink_sac', 250);

INSERT INTO combat_drop_xp (item_id, base_xp) VALUES
('wither_essence', 100),
('undead_essence', 80),
('bonzo_staff_fragment', 500),
('scarf_fragment', 600),
('professor_fragment', 700),
('spirit_bone', 800),
('livid_dagger', 2000),
('shadow_fury', 3000),
('giant_sword', 4000),
('necromancer_lord_armor_piece', 1500),
('necron_blade', 5000),
('wither_armor_piece', 2500),
('master_star', 3500),
('claymore', 6000),
('hyperion', 10000)
ON CONFLICT(item_id) DO UPDATE SET base_xp = excluded.base_xp;