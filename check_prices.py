# -*- coding: utf-8 -*-
import sqlite3
import sys
sys.stdout.reconfigure(encoding='utf-8')

db = sqlite3.connect("pokemon_catalog.db")
cursor = db.cursor()

# Verifica tabelas de preço
cursor.execute("SELECT COUNT(*) FROM card_prices")
prices_count = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM price_history")
history_count = cursor.fetchone()[0]

print(f"Registros em card_prices: {prices_count}")
print(f"Registros em price_history: {history_count}")

if prices_count > 0:
    print("\nPrimeiros registros de card_prices:")
    cursor.execute("SELECT card_id, source, currency, market, updated_at FROM card_prices LIMIT 3")
    for row in cursor.fetchall():
        print(f"  {row}")

if history_count > 0:
    print("\nPrimeiros registros de price_history:")
    cursor.execute("SELECT card_id, d, price, currency FROM price_history LIMIT 3")
    for row in cursor.fetchall():
        print(f"  {row}")

db.close()
