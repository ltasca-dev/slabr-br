#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Criar tabelas de sincronizacao com Bynx.gg
Execute: python create_bynx_sync_db.py
"""

import sqlite3

DB_PATH = 'pokemon_catalog.db'

SQL_MIGRATIONS = """
-- OAuth State (temporario, para validar flow)
CREATE TABLE IF NOT EXISTS bynx_oauth_state (
    user_id TEXT PRIMARY KEY,
    state TEXT NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Integracoes (conexoes ativas com Bynx)
CREATE TABLE IF NOT EXISTS bynx_integrations (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL UNIQUE,
    access_token TEXT NOT NULL,
    refresh_token TEXT,
    status VARCHAR(20), -- 'connected', 'expired', 'revoked'
    last_sync TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Log de sincronizacoes
CREATE TABLE IF NOT EXISTS bynx_sync_log (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    card_id VARCHAR(50),
    action VARCHAR(50), -- 'synced', 'uploaded', 'updated'
    synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Notificacoes do Bynx
CREATE TABLE IF NOT EXISTS bynx_notifications (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    card_id VARCHAR(50),
    old_price DECIMAL(10,2),
    new_price DECIMAL(10,2),
    event_type VARCHAR(50), -- 'price_change', 'listing_sold', 'trade_completed'
    read_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indices
CREATE INDEX IF NOT EXISTS idx_bynx_integrations_user_id ON bynx_integrations(user_id);
CREATE INDEX IF NOT EXISTS idx_bynx_sync_log_user_id ON bynx_sync_log(user_id);
CREATE INDEX IF NOT EXISTS idx_bynx_notifications_user_id ON bynx_notifications(user_id);
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

        print("\n[OK] Tabelas Bynx Sync criadas com sucesso!")
        return True

    except Exception as e:
        print(f"[ERRO] {e}")
        return False

if __name__ == "__main__":
    print("[INICIO] Criando tabelas Bynx Sync...")
    print(f"Banco: {DB_PATH}\n")

    if create_tables():
        print("\n[OK] Bynx Sync pronto!")
    else:
        exit(1)
