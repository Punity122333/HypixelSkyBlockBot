CREATE TABLE auction_items (
    auction_id INTEGER PRIMARY KEY,
    item_id TEXT NOT NULL,
    amount INTEGER DEFAULT 1,
    metadata TEXT,
    FOREIGN KEY (auction_id) REFERENCES auction_house(id) ON DELETE CASCADE
);

INSERT INTO auction_items (auction_id, item_id, amount, metadata)
SELECT id, item_id, 1, item_data
FROM auction_house;

CREATE TABLE auction_house_new (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    seller_id INTEGER NOT NULL,
    starting_bid INTEGER NOT NULL,
    current_bid INTEGER DEFAULT 0,
    highest_bidder_id INTEGER,
    buy_now_price INTEGER,
    end_time INTEGER NOT NULL,
    bin BOOLEAN DEFAULT 0,
    ended BOOLEAN DEFAULT 0,
    claimed BOOLEAN DEFAULT 0,
    created_at INTEGER NOT NULL,
    FOREIGN KEY (seller_id) REFERENCES players(user_id) ON DELETE CASCADE,
    FOREIGN KEY (highest_bidder_id) REFERENCES players(user_id) ON DELETE SET NULL
);

INSERT INTO auction_house_new 
SELECT id, seller_id, starting_bid, current_bid, highest_bidder_id, 
       buy_now_price, end_time, bin, ended, claimed, created_at
FROM auction_house;

DROP TABLE auction_house;
ALTER TABLE auction_house_new RENAME TO auction_house;

CREATE INDEX idx_auction_house_seller ON auction_house(seller_id);
CREATE INDEX idx_auction_house_status ON auction_house(ended, claimed);
CREATE INDEX idx_auction_house_bin ON auction_house(bin, ended);
CREATE INDEX idx_auction_house_end_time ON auction_house(end_time);
CREATE INDEX idx_auction_items_item ON auction_items(item_id);

CREATE TABLE bazaar_buy_orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    product_id TEXT NOT NULL,
    price REAL NOT NULL,
    amount INTEGER NOT NULL,
    filled INTEGER DEFAULT 0,
    active BOOLEAN DEFAULT 1,
    created_at INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES players(user_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES bazaar_products(product_id) ON DELETE CASCADE
);

CREATE TABLE bazaar_sell_orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    product_id TEXT NOT NULL,
    price REAL NOT NULL,
    amount INTEGER NOT NULL,
    filled INTEGER DEFAULT 0,
    active BOOLEAN DEFAULT 1,
    created_at INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES players(user_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES bazaar_products(product_id) ON DELETE CASCADE
);

INSERT INTO bazaar_buy_orders (id, user_id, product_id, price, amount, filled, active, created_at)
SELECT id, user_id, product_id, price, amount, filled, active, created_at
FROM bazaar_orders WHERE order_type = 'buy';

INSERT INTO bazaar_sell_orders (id, user_id, product_id, price, amount, filled, active, created_at)
SELECT id, user_id, product_id, price, amount, filled, active, created_at
FROM bazaar_orders WHERE order_type = 'sell';

DROP TABLE bazaar_orders;

CREATE INDEX idx_bazaar_buy_orders_user ON bazaar_buy_orders(user_id);
CREATE INDEX idx_bazaar_buy_orders_product ON bazaar_buy_orders(product_id, active);
CREATE INDEX idx_bazaar_sell_orders_user ON bazaar_sell_orders(user_id);
CREATE INDEX idx_bazaar_sell_orders_product ON bazaar_sell_orders(product_id, active);
CREATE INDEX idx_bazaar_products_id ON bazaar_products(product_id);
CREATE INDEX idx_bazaar_transactions_product ON bazaar_transactions(product_id);
CREATE INDEX idx_bazaar_transactions_time ON bazaar_transactions(timestamp);
