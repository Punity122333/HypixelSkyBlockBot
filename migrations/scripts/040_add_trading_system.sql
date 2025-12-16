CREATE TABLE IF NOT EXISTS player_trades (
    trade_id INTEGER PRIMARY KEY AUTOINCREMENT,
    initiator_id INTEGER NOT NULL,
    receiver_id INTEGER NOT NULL,
    status TEXT DEFAULT 'pending',
    initiator_coins INTEGER DEFAULT 0,
    receiver_coins INTEGER DEFAULT 0,
    initiator_ready INTEGER DEFAULT 0,
    receiver_ready INTEGER DEFAULT 0,
    created_at INTEGER NOT NULL,
    completed_at INTEGER,
    FOREIGN KEY (initiator_id) REFERENCES players(user_id) ON DELETE CASCADE,
    FOREIGN KEY (receiver_id) REFERENCES players(user_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS trade_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    trade_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    item_id TEXT NOT NULL,
    amount INTEGER DEFAULT 1,
    inventory_item_id INTEGER,
    FOREIGN KEY (trade_id) REFERENCES player_trades(trade_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES players(user_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS trade_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    trade_id INTEGER NOT NULL,
    initiator_id INTEGER NOT NULL,
    receiver_id INTEGER NOT NULL,
    initiator_coins INTEGER DEFAULT 0,
    receiver_coins INTEGER DEFAULT 0,
    completed_at INTEGER NOT NULL,
    FOREIGN KEY (initiator_id) REFERENCES players(user_id) ON DELETE CASCADE,
    FOREIGN KEY (receiver_id) REFERENCES players(user_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS trade_history_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    history_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    item_id TEXT NOT NULL,
    amount INTEGER DEFAULT 1,
    FOREIGN KEY (history_id) REFERENCES trade_history(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES players(user_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_player_trades_initiator ON player_trades(initiator_id);
CREATE INDEX IF NOT EXISTS idx_player_trades_receiver ON player_trades(receiver_id);
CREATE INDEX IF NOT EXISTS idx_player_trades_status ON player_trades(status);
CREATE INDEX IF NOT EXISTS idx_trade_items_trade ON trade_items(trade_id);
CREATE INDEX IF NOT EXISTS idx_trade_history_users ON trade_history(initiator_id, receiver_id);
