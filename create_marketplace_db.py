#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Criar tabelas do Marketplace no banco de dados
Execute: python create_marketplace_db.py
"""

import sqlite3

DB_PATH = 'pokemon_catalog.db'

SQL_MIGRATIONS = """
-- Tabela: marketplace_listings
CREATE TABLE IF NOT EXISTS marketplace_listings (
    id TEXT PRIMARY KEY,
    seller_id TEXT NOT NULL,
    card_id VARCHAR(50) NOT NULL,
    card_name VARCHAR(255),
    quantity INTEGER DEFAULT 1,
    price DECIMAL(10,2),
    condition VARCHAR(20),
    listing_type VARCHAR(20), -- 'sale' ou 'trade'
    status VARCHAR(20), -- 'active', 'sold', 'cancelled', 'expired'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP
);

-- Tabela: marketplace_trades
CREATE TABLE IF NOT EXISTS marketplace_trades (
    id TEXT PRIMARY KEY,
    listing_id TEXT NOT NULL,
    buyer_id TEXT NOT NULL,
    seller_id TEXT NOT NULL,
    amount DECIMAL(10,2),
    status VARCHAR(20), -- 'pending', 'escrow', 'shipped', 'completed', 'cancelled'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(listing_id) REFERENCES marketplace_listings(id)
);

-- Tabela: marketplace_reviews
CREATE TABLE IF NOT EXISTS marketplace_reviews (
    id TEXT PRIMARY KEY,
    trade_id TEXT NOT NULL,
    reviewer_id TEXT NOT NULL,
    rating INTEGER, -- 1-5
    comment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(trade_id) REFERENCES marketplace_trades(id)
);

-- Indice
CREATE INDEX IF NOT EXISTS idx_listings_seller_id ON marketplace_listings(seller_id);
CREATE INDEX IF NOT EXISTS idx_listings_card_id ON marketplace_listings(card_id);
CREATE INDEX IF NOT EXISTS idx_listings_status ON marketplace_listings(status);
CREATE INDEX IF NOT EXISTS idx_trades_buyer_id ON marketplace_trades(buyer_id);
CREATE INDEX IF NOT EXISTS idx_trades_seller_id ON marketplace_trades(seller_id);
CREATE INDEX IF NOT EXISTS idx_trades_status ON marketplace_trades(status);
CREATE INDEX IF NOT EXISTS idx_reviews_trade_id ON marketplace_reviews(trade_id);
"""

def create_tables():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        for statement in SQL_MIGRATIONS.split(';'):
            statement = statement.strip()
            if statement:
                cursor.execute(statement)
                print(f"[OK] {statement[:50]}...")

        conn.commit()
        conn.close()

        print("\n[OK] Tabelas do Marketplace criadas com sucesso!")
        return True

    except Exception as e:
        print(f"[ERRO] {e}")
        return False

if __name__ == "__main__":
    print("[INICIO] Criando tabelas do Marketplace...")
    print(f"Banco: {DB_PATH}\n")

    if create_tables():
        print("\n[OK] Marketplace pronto!")
    else:
        exit(1)
