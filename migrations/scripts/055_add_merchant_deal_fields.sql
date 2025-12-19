ALTER TABLE merchant_deals ADD COLUMN npc_name TEXT DEFAULT 'Merchant';
ALTER TABLE merchant_deals ADD COLUMN deal_type TEXT DEFAULT 'sell';

UPDATE merchant_deals SET active = 0 WHERE (created_at + duration) < strftime('%s', 'now');
