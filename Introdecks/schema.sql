PRAGMA foreign_keys = ON;

CREATE TABLE policyholders (
    holder_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    phone TEXT,
    email TEXT,
    city TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE policies (
    policy_id INTEGER PRIMARY KEY AUTOINCREMENT,
    holder_id INTEGER NOT NULL,
    policy_type TEXT NOT NULL,
    sum_insured REAL NOT NULL CHECK(sum_insured > 0),
    risk_level TEXT NOT NULL,
    premium REAL NOT NULL,
    policy_status TEXT NOT NULL DEFAULT 'Active',
    start_date TEXT NOT NULL,
    FOREIGN KEY(holder_id) REFERENCES policyholders(holder_id)
);

CREATE TABLE claims (
    claim_id INTEGER PRIMARY KEY AUTOINCREMENT,
    policy_id INTEGER NOT NULL,
    claim_amount REAL NOT NULL CHECK(claim_amount > 0),
    claim_reason TEXT,
    claim_status TEXT NOT NULL DEFAULT 'Pending',
    claim_date TEXT NOT NULL,
    FOREIGN KEY(policy_id) REFERENCES policies(policy_id)
);

CREATE TABLE payments (
    payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    policy_id INTEGER NOT NULL,
    amount REAL NOT NULL CHECK(amount > 0),
    payment_method TEXT NOT NULL,
    payment_date TEXT NOT NULL,
    payment_status TEXT NOT NULL DEFAULT 'Paid',
    FOREIGN KEY(policy_id) REFERENCES policies(policy_id)
);

-- Sample records are inserted automatically by app.py on first launch.
