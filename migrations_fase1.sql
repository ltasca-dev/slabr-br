-- FASE 1: Portfolio Manager - Database Schema
-- Execute este script para criar as tabelas necessárias

-- Tabela: user_collections (cartas na coleção do usuário)
CREATE TABLE IF NOT EXISTS user_collections (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    card_id VARCHAR(50) NOT NULL,
    card_name VARCHAR(255),
    quantity INTEGER DEFAULT 1,
    condition VARCHAR(20),
    purchase_price DECIMAL(10,2),
    purchase_date DATE,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, card_id, condition)
);

-- Tabela: portfolio_stats (estatísticas do portfolio)
CREATE TABLE IF NOT EXISTS portfolio_stats (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL UNIQUE,
    total_cards INTEGER DEFAULT 0,
    total_value DECIMAL(12,2) DEFAULT 0,
    total_cost DECIMAL(12,2) DEFAULT 0,
    biggest_gains JSON,
    biggest_losses JSON,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id)
);

-- Tabela: price_alerts (alertas de preço)
CREATE TABLE IF NOT EXISTS price_alerts (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    card_id VARCHAR(50) NOT NULL,
    card_name VARCHAR(255),
    threshold_price DECIMAL(10,2) NOT NULL,
    alert_type VARCHAR(10), -- 'up', 'down', 'exact'
    is_active BOOLEAN DEFAULT TRUE,
    triggered_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id)
);

-- Índices para performance
CREATE INDEX IF NOT EXISTS idx_user_collections_user_id ON user_collections(user_id);
CREATE INDEX IF NOT EXISTS idx_user_collections_card_id ON user_collections(card_id);
CREATE INDEX IF NOT EXISTS idx_portfolio_stats_user_id ON portfolio_stats(user_id);
CREATE INDEX IF NOT EXISTS idx_price_alerts_user_id ON price_alerts(user_id);
CREATE INDEX IF NOT EXISTS idx_price_alerts_card_id ON price_alerts(card_id);
