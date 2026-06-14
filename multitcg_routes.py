#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Multi-TCG Support Routes
Integrar Pokemon, Magic, Yu-Gi-Oh, One Piece
"""

from flask import Blueprint, request, jsonify
import sqlite3
import uuid
from datetime import datetime

DB_PATH = 'pokemon_catalog.db'

multitcg_bp = Blueprint('multitcg', __name__)

# ============================================================================
# TCG Management
# ============================================================================

@multitcg_bp.route('/api/tcg/list', methods=['GET'])
def get_tcgs():
    """Listar TCGs suportados"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM tcgs WHERE is_active = 1 ORDER BY name")
        tcgs = [dict(row) for row in cursor.fetchall()]
        conn.close()

        return jsonify({
            'status': 'success',
            'count': len(tcgs),
            'tcgs': tcgs
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@multitcg_bp.route('/api/tcg/<tcg_id>/sets', methods=['GET'])
def get_tcg_sets(tcg_id):
    """Listar sets de um TCG"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM tcg_sets WHERE tcg_id = ? AND is_active = 1 ORDER BY release_date DESC",
            (tcg_id,)
        )
        sets = [dict(row) for row in cursor.fetchall()]
        conn.close()

        return jsonify({
            'status': 'success',
            'tcg_id': tcg_id,
            'count': len(sets),
            'sets': sets
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@multitcg_bp.route('/api/tcg/<tcg_id>/cards', methods=['GET'])
def get_tcg_cards(tcg_id):
    """Buscar cartas de um TCG"""
    try:
        search = request.args.get('search', '')
        set_id = request.args.get('set_id', '')
        limit = request.args.get('limit', 50, type=int)

        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        query = "SELECT * FROM tcg_cards WHERE tcg_id = ?"
        params = [tcg_id]

        if set_id:
            query += " AND set_id = ?"
            params.append(set_id)

        if search:
            query += " AND card_name LIKE ?"
            params.append(f"%{search}%")

        query += " LIMIT ?"
        params.append(limit)

        cursor.execute(query, params)
        cards = [dict(row) for row in cursor.fetchall()]
        conn.close()

        return jsonify({
            'status': 'success',
            'tcg_id': tcg_id,
            'count': len(cards),
            'cards': cards
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# ============================================================================
# Multi-TCG Collection Management
# ============================================================================

@multitcg_bp.route('/api/collections/v2', methods=['POST'])
def add_card_v2():
    """Adicionar carta em qualquer TCG"""
    try:
        data = request.get_json()
        required = ['user_id', 'tcg_id', 'card_id', 'card_name']

        if not all(k in data for k in required):
            return jsonify({'status': 'error', 'message': 'Missing required fields'}), 400

        user_id = data['user_id']
        tcg_id = data['tcg_id']
        card_id = data['card_id']
        card_name = data['card_name']
        quantity = data.get('quantity', 1)
        condition = data.get('condition', 'NM')
        purchase_price = data.get('purchase_price', 0)

        collection_id = str(uuid.uuid4())

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute(
            """INSERT INTO user_collections_v2
               (id, user_id, tcg_id, card_id, card_name, quantity, condition, purchase_price)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (collection_id, user_id, tcg_id, card_id, card_name, quantity, condition, purchase_price)
        )
        conn.commit()
        conn.close()

        return jsonify({
            'status': 'success',
            'id': collection_id,
            'message': f'{card_name} adicionado a colecao {tcg_id}'
        }), 201
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@multitcg_bp.route('/api/collections/v2/<user_id>', methods=['GET'])
def get_collections_v2(user_id):
    """Listar colecoes do usuario (todos TCGs)"""
    try:
        tcg_id = request.args.get('tcg_id')

        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        if tcg_id:
            cursor.execute(
                "SELECT * FROM user_collections_v2 WHERE user_id = ? AND tcg_id = ? ORDER BY updated_at DESC",
                (user_id, tcg_id)
            )
        else:
            cursor.execute(
                "SELECT * FROM user_collections_v2 WHERE user_id = ? ORDER BY tcg_id, updated_at DESC",
                (user_id,)
            )

        collections = [dict(row) for row in cursor.fetchall()]
        conn.close()

        return jsonify({
            'status': 'success',
            'user_id': user_id,
            'count': len(collections),
            'collections': collections
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@multitcg_bp.route('/api/collections/v2/stats/<user_id>', methods=['GET'])
def get_portfolio_stats_v2(user_id):
    """Obter estatisticas de portfolio (todos TCGs)"""
    try:
        tcg_id = request.args.get('tcg_id')

        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        if tcg_id:
            cursor.execute(
                "SELECT * FROM user_portfolio_stats_v2 WHERE user_id = ? AND tcg_id = ?",
                (user_id, tcg_id)
            )
            stats = cursor.fetchone()
        else:
            cursor.execute(
                "SELECT * FROM user_portfolio_stats_v2 WHERE user_id = ? ORDER BY tcg_id",
                (user_id,)
            )
            stats = cursor.fetchall()

        conn.close()

        if tcg_id:
            return jsonify({
                'status': 'success',
                'stats': dict(stats) if stats else None
            })
        else:
            return jsonify({
                'status': 'success',
                'stats': [dict(row) for row in stats] if stats else []
            })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# ============================================================================
# Multi-TCG Marketplace
# ============================================================================

@multitcg_bp.route('/api/marketplace/v2/listings', methods=['POST'])
def create_listing_v2():
    """Criar anuncio em qualquer TCG"""
    try:
        data = request.get_json()
        required = ['seller_id', 'tcg_id', 'card_id', 'card_name', 'price']

        if not all(k in data for k in required):
            return jsonify({'status': 'error', 'message': 'Missing required fields'}), 400

        listing_id = str(uuid.uuid4())
        seller_id = data['seller_id']
        tcg_id = data['tcg_id']
        card_id = data['card_id']
        card_name = data['card_name']
        quantity = data.get('quantity', 1)
        price = data['price']
        currency = data.get('currency', 'BRL')
        condition = data.get('condition', 'NM')
        listing_type = data.get('listing_type', 'sale')

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute(
            """INSERT INTO marketplace_listings_v2
               (id, seller_id, tcg_id, card_id, card_name, quantity, price, currency, condition, listing_type, status)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'active')""",
            (listing_id, seller_id, tcg_id, card_id, card_name, quantity, price, currency, condition, listing_type)
        )
        conn.commit()
        conn.close()

        return jsonify({
            'status': 'success',
            'id': listing_id,
            'message': f'Anuncio criado para {card_name} ({tcg_id})'
        }), 201
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@multitcg_bp.route('/api/marketplace/v2/listings', methods=['GET'])
def get_listings_v2():
    """Buscar anuncios (todos TCGs)"""
    try:
        tcg_id = request.args.get('tcg_id')
        card_name = request.args.get('card_name')
        currency = request.args.get('currency', 'BRL')
        limit = request.args.get('limit', 50, type=int)

        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        query = "SELECT * FROM marketplace_listings_v2 WHERE status = 'active' AND currency = ?"
        params = [currency]

        if tcg_id:
            query += " AND tcg_id = ?"
            params.append(tcg_id)

        if card_name:
            query += " AND card_name LIKE ?"
            params.append(f"%{card_name}%")

        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)

        cursor.execute(query, params)
        listings = [dict(row) for row in cursor.fetchall()]
        conn.close()

        return jsonify({
            'status': 'success',
            'count': len(listings),
            'listings': listings
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# ============================================================================
# User TCG Preferences
# ============================================================================

@multitcg_bp.route('/api/users/<user_id>/preferences', methods=['GET', 'POST'])
def user_preferences(user_id):
    """Obter ou atualizar preferencias de TCG do usuario"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        if request.method == 'GET':
            cursor.execute(
                "SELECT * FROM user_tcg_preferences WHERE user_id = ? ORDER BY created_at",
                (user_id,)
            )
            preferences = [dict(row) for row in cursor.fetchall()]
            conn.close()

            return jsonify({
                'status': 'success',
                'user_id': user_id,
                'preferences': preferences
            })

        else:  # POST
            data = request.get_json()
            tcg_id = data.get('tcg_id')
            currency = data.get('currency', 'BRL')
            language = data.get('language', 'pt-BR')
            favorite = data.get('favorite', False)

            pref_id = str(uuid.uuid4())

            cursor.execute(
                """INSERT OR REPLACE INTO user_tcg_preferences
                   (id, user_id, tcg_id, currency, language, favorite)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (pref_id, user_id, tcg_id, currency, language, favorite)
            )
            conn.commit()
            conn.close()

            return jsonify({
                'status': 'success',
                'message': f'Preferencias atualizadas para {tcg_id}'
            }), 201
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# ============================================================================
# Global Marketplace (Multi-Currency)
# ============================================================================

@multitcg_bp.route('/api/marketplace/v2/global', methods=['GET'])
def global_marketplace():
    """Buscar anuncios globalmente (todas regioes)"""
    try:
        card_name = request.args.get('card_name')
        tcg_id = request.args.get('tcg_id')
        limit = request.args.get('limit', 100, type=int)

        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        query = "SELECT * FROM marketplace_listings_v2 WHERE status = 'active'"
        params = []

        if tcg_id:
            query += " AND tcg_id = ?"
            params.append(tcg_id)

        if card_name:
            query += " AND card_name LIKE ?"
            params.append(f"%{card_name}%")

        query += " ORDER BY price ASC LIMIT ?"
        params.append(limit)

        cursor.execute(query, params)
        listings = [dict(row) for row in cursor.fetchall()]

        # Agrupar por currency e TCG
        grouped = {}
        for listing in listings:
            key = f"{listing['tcg_id']}_{listing['currency']}"
            if key not in grouped:
                grouped[key] = {'tcg': listing['tcg_id'], 'currency': listing['currency'], 'listings': []}
            grouped[key]['listings'].append(listing)

        conn.close()

        return jsonify({
            'status': 'success',
            'total': len(listings),
            'markets': grouped
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
