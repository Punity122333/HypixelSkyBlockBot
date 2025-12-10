ALTER TABLE mayors ADD COLUMN bonuses TEXT DEFAULT '{}';

UPDATE mayors SET bonuses = '{"pet_luck": 50}' WHERE mayor_id = 'diana';
UPDATE mayors SET bonuses = '{"skill_xp_multiplier": 0.5, "shop_price_multiplier": 0.5}' WHERE mayor_id = 'derpy';
UPDATE mayors SET bonuses = '{"shop_discount": 0.1, "minion_slots": 1}' WHERE mayor_id = 'paul';
UPDATE mayors SET bonuses = '{}' WHERE mayor_id = 'jerry';
UPDATE mayors SET bonuses = '{"fishing_xp": 1.0, "sea_creature_chance": 0.2}' WHERE mayor_id = 'marina';
UPDATE mayors SET bonuses = '{"slayer_xp": 1.0}' WHERE mayor_id = 'aatrox';
