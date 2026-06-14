# -*- coding: utf-8 -*-
import sqlite3
from werkzeug.security import generate_password_hash

db = sqlite3.connect("pokemon_catalog.db")
cursor = db.cursor()

new_password = "demo123"
new_hash = generate_password_hash(new_password)

cursor.execute("UPDATE users SET pw_hash = ? WHERE lower(handle) = ?", (new_hash, "liz"))
db.commit()

# Verifica
cursor.execute("SELECT handle, name FROM users WHERE lower(handle) = ?", ("liz",))
user = cursor.fetchone()

if user:
    print(f"Senha resetada para '{user[0]}'")
    print(f"Nova senha: {new_password}")
else:
    print("Erro: usuário não encontrado")

db.close()
