-- init.sql
CREATE TABLE IF NOT EXISTS transactions (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(100) NOT NULL,
    amount DECIMAL(15,2) NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_fraud BOOLEAN DEFAULT FALSE,
    fraud_score DECIMAL(5,4),
    risk_level VARCHAR(10)
);

INSERT INTO transactions (user_id, amount, is_fraud, fraud_score, risk_level) VALUES
('user_001', 50000.00, false, 0.1, 'LOW'),
('user_002', 15000000.00, true, 0.8, 'HIGH'),
('user_003', 500.00, true, 0.6, 'MEDIUM');