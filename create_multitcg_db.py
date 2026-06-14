#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Criar tabelas para suportar multiplos TCGs
Execute: python create_multitcg_db.py
"""

import sqlite3

DB_PATH = 'pokemon_catalog.db'

SQL_MIGRATIONS = """
-- Tabela de TCGs suportados
CREATE TABLE IF NOT EXISTS tcgs (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    display_name TEXT NOT NULL,
    category TEXT, -- 'pokemon', 'magic', 'yugioh', 'onepiece'
    description TEXT,
    official_site TEXT,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de Sets por TCG
CREATE TABLE IF NOT EXISTS tcg_sets (
    id TEXT PRIMARY KEY,
    tcg_id TEXT NOT NULL,
    set_code TEXT NOT NULL,
    set_name TEXT NOT NULL,
    release_date DATE,
    total_cards INT,
    image_url TEXT,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (tcg_id) REFERENCES tcgs(id)
);

-- Tabela de Cartas generica (suporta todos TCGs)
CREATE TABLE IF NOT EXISTS tcg_cards (
    id TEXT PRIMARY KEY, -- unique identifier por TCG
    tcg_id TEXT NOT NULL,
    set_id TEXT NOT NULL,
    card_number TEXT NOT NULL,
    card_name TEXT NOT NULL,
    rarity TEXT, -- common, uncommon, rare, holo, secret
    card_type TEXT, -- Pokemon, Spell, Monster, etc
    description TEXT,
    image_url TEXT,
    is_holo BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (tcg_id) REFERENCES tcgs(id),
    FOREIGN KEY (set_id) REFERENCES tcg_sets(id)
);

-- Tabela de precos por TCG e regiao
CREATE TABLE IF NOT EXISTS tcg_prices (
    id TEXT PRIMARY KEY,
    card_id TEXT NOT NULL,
    tcg_id TEXT NOT NULL,
    currency VARCHAR(3), -- BRL, USD, EUR, JPY
    market VARCHAR(50), -- 'bynx', 'tcgplayer', 'cardmarket'
    price_min DECIMAL(10,2),
    price_avg DECIMAL(10,2),
    price_max DECIMAL(10,2),
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (card_id) REFERENCES tcg_cards(id),
    FOREIGN KEY (tcg_id) REFERENCES tcgs(id)
);

-- Tabela de colecoes do usuario (suporta multiplos TCGs)
CREATE TABLE IF NOT EXISTS user_collections_v2 (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    tcg_id TEXT NOT NULL,
    card_id TEXT NOT NULL,
    card_name TEXT NOT NULL,
    quantity INT DEFAULT 1,
    condition VARCHAR(3), -- NM, LP, MP, HP, DMG
    purchase_price DECIMAL(10,2),
    purchase_date DATE,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (tcg_id) REFERENCES tcgs(id),
    FOREIGN KEY (card_id) REFERENCES tcg_cards(id)
);

-- Tabela de portfolio stats por TCG
CREATE TABLE IF NOT EXISTS user_portfolio_stats_v2 (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    tcg_id TEXT NOT NULL,
    total_cards INT DEFAULT 0,
    total_value DECIMAL(12,2) DEFAULT 0,
    total_cost DECIMAL(12,2) DEFAULT 0,
    biggest_gains JSON,
    biggest_losses JSON,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, tcg_id)
);

-- Tabela de marketplace listings (suporta multiplos TCGs)
CREATE TABLE IF NOT EXISTS marketplace_listings_v2 (
    id TEXT PRIMARY KEY,
    seller_id TEXT NOT NULL,
    tcg_id TEXT NOT NULL,
    card_id TEXT NOT NULL,
    card_name TEXT NOT NULL,
    quantity INT DEFAULT 1,
    price DECIMAL(10,2),
    currency VARCHAR(3), -- BRL, USD, EUR
    condition VARCHAR(3),
    listing_type VARCHAR(20), -- 'sale', 'trade'
    status VARCHAR(20), -- 'active', 'sold', 'cancelled'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    FOREIGN KEY (tcg_id) REFERENCES tcgs(id),
    FOREIGN KEY (card_id) REFERENCES tcg_cards(id)
);

-- Tabela de preferencias de usuario por TCG
CREATE TABLE IF NOT EXISTS user_tcg_preferences (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    tcg_id TEXT NOT NULL,
    favorite BOOLEAN DEFAULT 0,
    language VARCHAR(5), -- pt-BR, en-US, es-ES
    currency VARCHAR(3),
    notifications_enabled BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, tcg_id)
);

-- Indices
CREATE INDEX IF NOT EXISTS idx_tcg_sets_tcg_id ON tcg_sets(tcg_id);
CREATE INDEX IF NOT EXISTS idx_tcg_cards_tcg_id ON tcg_cards(tcg_id);
CREATE INDEX IF NOT EXISTS idx_tcg_prices_card_id ON tcg_prices(card_id);
CREATE INDEX IF NOT EXISTS idx_user_collections_v2_user ON user_collections_v2(user_id);
CREATE INDEX IF NOT EXISTS idx_user_collections_v2_tcg ON user_collections_v2(tcg_id);
CREATE INDEX IF NOT EXISTS idx_marketplace_listings_v2_seller ON marketplace_listings_v2(seller_id);
CREATE INDEX IF NOT EXISTS idx_marketplace_listings_v2_tcg ON marketplace_listings_v2(tcg_id);
CREATE INDEX IF NOT EXISTS idx_user_tcg_preferences_user ON user_tcg_preferences(user_id);
"""

def create_tables():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        for statement in SQL_MIGRATIONS.split(';'):
            statement = statement.strip()
            if statement:
                cursor.execute(statement)
                print(f"[OK] {statement.split('\\n')[0][:50]}...")

        # Insert supported TCGs
        tcgs_data = [
            ('pokemon', 'Pokemon', 'Pokemon Trading Card Game', 'pokemon', 'Colecaveis Pokemon TCG'),
            ('magic', 'Magic: The Gathering', 'Magic: The Gathering', 'magic', 'Cartas Magic TCG'),
            ('yugioh', 'Yu-Gi-Oh!', 'Yu-Gi-Oh! Trading Card Game', 'yugioh', 'Cartas Yu-Gi-Oh TCG'),
            ('onepiece', 'One Piece', 'One Piece Card Game', 'onepiece', 'Cartas One Piece TCG'),
        ]

        cursor.execute("SELECT COUNT(*) FROM tcgs")
        if cursor.fetchone()[0] == 0:
            for tcg_id, name, display_name, category, description in tcgs_data:
                cursor.execute(
                    "INSERT INTO tcgs (id, name, display_name, category, description, is_active) VALUES (?, ?, ?, ?, ?, 1)",
                    (tcg_id, name, display_name, category, description)
                )
                print(f"[OK] TCG inserido: {display_name}")

        conn.commit()
        conn.close()

        print("\n[OK] Tabelas Multi-TCG criadas com sucesso!")
        return True

    except Exception as e:
        print(f"[ERRO] {e}")
        return False

if __name__ == "__main__":
    print("[INICIO] Criando tabelas Multi-TCG...")
    print(f"Banco: {DB_PATH}\n")

    if create_tables():
        print("\n[OK] Multi-TCG pronto para Fase 2!")
    else:
        exit(1)
