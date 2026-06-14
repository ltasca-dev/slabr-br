# -*- coding: utf-8 -*-
import sqlite3
import sys
sys.stdout.reconfigure(encoding='utf-8')

db = sqlite3.connect("pokemon_catalog.db")
cursor = db.cursor()

# Procura por "liz"
cursor.execute("SELECT handle, name, email, city FROM users WHERE lower(handle) LIKE '%liz%' OR lower(email) LIKE '%liz%'")
users = cursor.fetchall()

if users:
    print("Usuário 'liz' ENCONTRADO no banco:")
    for row in users:
        print(f"  Handle: {row[0]}")
        print(f"  Nome: {row[1]}")
        print(f"  Email: {row[2]}")
        print(f"  Cidade: {row[3]}")
else:
    print("Nenhum usuário 'liz' encontrado")
    print("")
    print("Todos os usuários no banco:")
    cursor.execute("SELECT handle, name, email FROM users")
    for row in cursor.fetchall():
        print(f"  - {row[0]} ({row[2]})")

db.close()
