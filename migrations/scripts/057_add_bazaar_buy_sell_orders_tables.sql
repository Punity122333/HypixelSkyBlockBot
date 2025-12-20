CREATE TABLE IF NOT EXISTS bazaar_buy_orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    product_id TEXT NOT NULL,
    price REAL NOT NULL,
    amount INTEGER NOT NULL,
    filled INTEGER DEFAULT 0,
    active BOOLEAN DEFAULT 1,
    created_at INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES players(user_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS bazaar_sell_orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    product_id TEXT NOT NULL,
    price REAL NOT NULL,
    amount INTEGER NOT NULL,
    filled INTEGER DEFAULT 0,
    active BOOLEAN DEFAULT 1,
    created_at INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES players(user_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_bazaar_buy_orders_user ON bazaar_buy_orders(user_id);
CREATE INDEX IF NOT EXISTS idx_bazaar_buy_orders_product ON bazaar_buy_orders(product_id, active);
CREATE INDEX IF NOT EXISTS idx_bazaar_sell_orders_user ON bazaar_sell_orders(user_id);
CREATE INDEX IF NOT EXISTS idx_bazaar_sell_orders_product ON bazaar_sell_orders(product_id, active);
