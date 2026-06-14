# -*- coding: utf-8 -*-
import sqlite3
import sys
sys.stdout.reconfigure(encoding='utf-8')

db = sqlite3.connect("pokemon_catalog.db")
cursor = db.cursor()

# Procura a carta
card_id = "bw2-11"
cursor.execute("SELECT id, name FROM cards WHERE id = ?", (card_id,))
card = cursor.fetchone()

print(f"Carta: {card}")

# Procura todas as instâncias dessa carta
cursor.execute("""
    SELECT cert_id, owner_handle, scan_url_front, public, for_sale, grade, condition, graded
    FROM graded_items
    WHERE card_id = ?
    ORDER BY public DESC, declared_value_cents DESC
""", (card_id,))

items = cursor.fetchall()
print(f"\nInstâncias encontradas: {len(items)}")

for row in items:
    print(f"\n  Cert: {row[0]}")
    print(f"  Owner: {row[1]}")
    print(f"  Scan: {row[2][:50] if row[2] else '(nulo)'}")
    print(f"  Public: {row[3]}, For Sale: {row[4]}")
    print(f"  Grade: {row[5]}, Graded: {row[7]}")

db.close()
