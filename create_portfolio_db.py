#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Criar tabelas do Portfolio Manager no banco de dados
Execute: python create_portfolio_db.py
"""

import sqlite3
import sys

DB_PATH = 'pokemon_catalog.db'

SQL_MIGRATIONS = """
-- Tabela: user_collections
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

-- Tabela: portfolio_stats
CREATE TABLE IF NOT EXISTS portfolio_stats (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL UNIQUE,
    total_cards INTEGER DEFAULT 0,
    total_value DECIMAL(12,2) DEFAULT 0,
    total_cost DECIMAL(12,2) DEFAULT 0,
    biggest_gains TEXT,
    biggest_losses TEXT,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela: price_alerts
CREATE TABLE IF NOT EXISTS price_alerts (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    card_id VARCHAR(50) NOT NULL,
    card_name VARCHAR(255),
    threshold_price DECIMAL(10,2) NOT NULL,
    alert_type VARCHAR(10),
    is_active BOOLEAN DEFAULT TRUE,
    triggered_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices
CREATE INDEX IF NOT EXISTS idx_user_collections_user_id ON user_collections(user_id);
CREATE INDEX IF NOT EXISTS idx_user_collections_card_id ON user_collections(card_id);
CREATE INDEX IF NOT EXISTS idx_portfolio_stats_user_id ON portfolio_stats(user_id);
CREATE INDEX IF NOT EXISTS idx_price_alerts_user_id ON price_alerts(user_id);
CREATE INDEX IF NOT EXISTS idx_price_alerts_card_id ON price_alerts(card_id);
"""

def create_tables():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Executar cada statement separadamente
        for statement in SQL_MIGRATIONS.split(';'):
            statement = statement.strip()
            if statement:
                cursor.execute(statement)
                print(f"[OK] Executado: {statement[:60]}...")

        conn.commit()
        conn.close()

        print("\n[OK] Tabelas criadas com sucesso!")
        return True

    except Exception as e:
        print(f"[ERRO] Erro ao criar tabelas: {e}")
        return False

if __name__ == "__main__":
    print("[INICIO] Criando tabelas do Portfolio Manager...")
    print(f"Banco de dados: {DB_PATH}\n")

    if create_tables():
        print("\n[OK] Pronto para Fase 1!")
        sys.exit(0)
    else:
        sys.exit(1)
