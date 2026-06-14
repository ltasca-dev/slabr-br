# -*- coding: utf-8 -*-
import sqlite3
import sys
sys.stdout.reconfigure(encoding='utf-8')

db = sqlite3.connect("pokemon_catalog.db")
cursor = db.cursor()

# Procura a instância
cursor.execute("""
    SELECT cert_id, scan_url_front, LENGTH(scan_url_front) as scan_length
    FROM graded_items
    WHERE card_id = 'bw2-11' AND owner_handle = 'Liz'
""")

row = cursor.fetchone()
if row:
    cert = row[0]
    scan = row[1]
    scan_len = row[2]

    print(f"Cert: {cert}")
    print(f"Tamanho do scan: {scan_len} bytes")
    print(f"\nPrimeiros 200 chars do scan:")
    print(scan[:200] if scan else "(nulo)")
    print(f"\nÚltimos 100 chars do scan:")
    print(scan[-100:] if scan else "(nulo)")

    # Verifica se é base64 válido
    if scan and scan.startswith("data:"):
        print("\n✓ É um Data URL base64")
        if scan.endswith("==") or scan.endswith("="):
            print("✓ Termina com padding válido")
        else:
            print("⚠ Pode estar incompleto (sem padding)")
else:
    print("Nenhuma instância encontrada")

db.close()
