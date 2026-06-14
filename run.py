#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Servidor unificado: HTTP estático + Flask API na mesma porta"""

import os
import sys
import sqlite3
from flask import Flask, jsonify, request, session, g

# Importar blueprints
from portfolio_routes import portfolio_bp
from marketplace_routes import marketplace_bp
from bynx_sync_routes import bynx_sync_bp
from multitcg_routes import multitcg_bp

# Criar app Flask
app = Flask(__name__)
app.secret_key = os.environ.get("SLABR_SECRET", "troque-este-segredo-em-producao")

# Banco de dados
DB = os.environ.get("SLABR_DB", "pokemon_catalog.db")

@app.teardown_appcontext
def close_connection(exception):
    db = g.pop("db", None)
    if db is not None:
        db.close()

# Registrar blueprints
app.register_blueprint(portfolio_bp)
app.register_blueprint(marketplace_bp)
app.register_blueprint(bynx_sync_bp)
app.register_blueprint(multitcg_bp)

# CORS
@app.after_request
def cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = request.headers.get("Origin", "*")
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return response

# Health check
@app.route('/api/prices/bynx/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'scraper': 'online', 'test': 'OK'})

# Servir arquivos HTML estáticos
@app.route('/', methods=['GET'])
def home():
    return serve_file('home.html')

@app.route('/app', methods=['GET'])
def app_page():
    return serve_file('app.html')

@app.route('/slabr', methods=['GET'])
@app.route('/dashboard', methods=['GET'])
def slabr_page():
    return serve_file('slabr_complete.html')

def serve_file(filename):
    try:
        filepath = os.path.join(os.path.dirname(__file__), filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read(), 200, {'Content-Type': 'text/html; charset=utf-8'}
    except FileNotFoundError:
        return f"Arquivo {filename} não encontrado", 404
    except Exception as e:
        return f"Erro ao servir arquivo: {str(e)}", 500

if __name__ == '__main__':
    print("=" * 70)
    print("SLABR 2.0 - Servidor Integrado (HTTP + Flask API)")
    print("=" * 70)
    print("\nAcesso local:")
    print("  > http://localhost:5000              (Home)")
    print("  > http://localhost:5000/app          (App - Marketplace Público)")
    print("  > http://localhost:5000/slabr        (SLABR Integrada)")
    print("  > http://localhost:5000/api/         (46+ Endpoints)")
    print("\nPressione CTRL+C para parar\n")

    # Rodar Flask
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=False,
        use_reloader=False
    )
