# -*- coding: utf-8 -*-
"""
Marketplace Routes - Fase 1 SLABR 2.0
Sistema de venda, compra e troca de cartas
"""

from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
import uuid
import sqlite3

marketplace_bp = Blueprint('marketplace', __name__, url_prefix='/api/marketplace')

def get_db_connection():
    conn = sqlite3.connect('pokemon_catalog.db')
    conn.row_factory = sqlite3.Row
    return conn

# ============================================================================
# LISTINGS - Criar anúncio de venda/troca
# ============================================================================

@marketplace_bp.route('/listings', methods=['POST'])
def create_listing():
    """Criar novo anúncio de venda ou troca"""
    data = request.json
    seller_id = data.get('seller_id')
    card_id = data.get('card_id')
    card_name = data.get('card_name')
    quantity = data.get('quantity', 1)
    price = data.get('price')
    condition = data.get('condition', 'NM')
    listing_type = data.get('listing_type', 'sale')  # 'sale' ou 'trade'

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        listing_id = str(uuid.uuid4())
        expires_at = datetime.now() + timedelta(days=30)

        cursor.execute('''
            INSERT INTO marketplace_listings
            (id, seller_id, card_id, card_name, quantity, price, condition, listing_type, status, expires_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'active', ?)
        ''', (listing_id, seller_id, card_id, card_name, quantity, price, condition, listing_type, expires_at))

        conn.commit()
        conn.close()

        return jsonify({
            'status': 'success',
            'id': listing_id,
            'message': f'{card_name} anunciada com sucesso'
        }), 201

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

@marketplace_bp.route('/listings', methods=['GET'])
def get_listings():
    """Listar anúncios ativos (com filtros opcionais)"""
    try:
        card_name = request.args.get('card_name', '')
        min_price = request.args.get('min_price')
        max_price = request.args.get('max_price')
        listing_type = request.args.get('type', '')

        conn = get_db_connection()
        cursor = conn.cursor()

        query = 'SELECT * FROM marketplace_listings WHERE status = "active"'
        params = []

        if card_name:
            query += ' AND card_name LIKE ?'
            params.append(f'%{card_name}%')

        if min_price:
            query += ' AND price >= ?'
            params.append(float(min_price))

        if max_price:
            query += ' AND price <= ?'
            params.append(float(max_price))

        if listing_type:
            query += ' AND listing_type = ?'
            params.append(listing_type)

        query += ' ORDER BY created_at DESC LIMIT 100'

        cursor.execute(query, params)
        listings = [dict(row) for row in cursor.fetchall()]
        conn.close()

        return jsonify({
            'status': 'success',
            'count': len(listings),
            'listings': listings
        }), 200

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

@marketplace_bp.route('/listings/<listing_id>', methods=['GET'])
def get_listing(listing_id):
    """Obter detalhes de um anúncio"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM marketplace_listings WHERE id = ?', (listing_id,))
        listing = cursor.fetchone()
        conn.close()

        if not listing:
            return jsonify({'status': 'error', 'message': 'Anúncio não encontrado'}), 404

        return jsonify({
            'status': 'success',
            'listing': dict(listing)
        }), 200

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

@marketplace_bp.route('/listings/<listing_id>', methods=['DELETE'])
def delete_listing(listing_id):
    """Remover anúncio"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('UPDATE marketplace_listings SET status = "cancelled" WHERE id = ?', (listing_id,))
        conn.commit()
        conn.close()

        return jsonify({'status': 'success', 'message': 'Anúncio removido'}), 200

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

# ============================================================================
# TRADES - Compra/Venda/Troca
# ============================================================================

@marketplace_bp.route('/trades', methods=['POST'])
def create_trade():
    """Criar trade (compra/venda/troca)"""
    data = request.json
    listing_id = data.get('listing_id')
    buyer_id = data.get('buyer_id')
    amount = data.get('amount')  # Para venda
    offer_cards = data.get('offer_cards')  # Para troca

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Obter listing
        cursor.execute('SELECT * FROM marketplace_listings WHERE id = ?', (listing_id,))
        listing = cursor.fetchone()

        if not listing:
            return jsonify({'status': 'error', 'message': 'Anúncio não encontrado'}), 404

        if listing['status'] != 'active':
            return jsonify({'status': 'error', 'message': 'Anúncio não está ativo'}), 400

        trade_id = str(uuid.uuid4())

        # Para venda: amount é o preço
        # Para troca: amount é None
        cursor.execute('''
            INSERT INTO marketplace_trades
            (id, listing_id, buyer_id, seller_id, amount, status)
            VALUES (?, ?, ?, ?, ?, 'pending')
        ''', (trade_id, listing_id, buyer_id, listing['seller_id'], amount))

        # Atualizar status do listing
        cursor.execute('UPDATE marketplace_listings SET status = "sold" WHERE id = ?', (listing_id,))

        conn.commit()
        conn.close()

        return jsonify({
            'status': 'success',
            'id': trade_id,
            'message': 'Trade criada com sucesso'
        }), 201

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

@marketplace_bp.route('/trades/<user_id>', methods=['GET'])
def get_trades(user_id):
    """Obter histórico de trades do usuário"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM marketplace_trades
            WHERE buyer_id = ? OR seller_id = ?
            ORDER BY created_at DESC
            LIMIT 50
        ''', (user_id, user_id))

        trades = [dict(row) for row in cursor.fetchall()]
        conn.close()

        return jsonify({
            'status': 'success',
            'count': len(trades),
            'trades': trades
        }), 200

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

@marketplace_bp.route('/trades/<trade_id>/confirm', methods=['POST'])
def confirm_trade(trade_id):
    """Confirmar recebimento da trade"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE marketplace_trades
            SET status = 'completed', updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (trade_id,))

        conn.commit()
        conn.close()

        return jsonify({
            'status': 'success',
            'message': 'Trade confirmada'
        }), 200

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

# ============================================================================
# REVIEWS - Avaliar comprador/vendedor
# ============================================================================

@marketplace_bp.route('/reviews', methods=['POST'])
def create_review():
    """Deixar avaliação de uma trade"""
    data = request.json
    trade_id = data.get('trade_id')
    reviewer_id = data.get('reviewer_id')
    rating = data.get('rating')  # 1-5
    comment = data.get('comment', '')

    if not (1 <= rating <= 5):
        return jsonify({'status': 'error', 'message': 'Rating deve ser 1-5'}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        review_id = str(uuid.uuid4())
        cursor.execute('''
            INSERT INTO marketplace_reviews
            (id, trade_id, reviewer_id, rating, comment)
            VALUES (?, ?, ?, ?, ?)
        ''', (review_id, trade_id, reviewer_id, rating, comment))

        conn.commit()
        conn.close()

        return jsonify({
            'status': 'success',
            'id': review_id,
            'message': 'Avaliacao registrada'
        }), 201

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

@marketplace_bp.route('/reviews/<user_id>', methods=['GET'])
def get_user_reviews(user_id):
    """Obter avaliações de um usuário"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Buscar trades onde user_id foi seller
        cursor.execute('''
            SELECT r.*, t.id as trade_id
            FROM marketplace_reviews r
            JOIN marketplace_trades t ON r.trade_id = t.id
            WHERE t.seller_id = ?
            ORDER BY r.created_at DESC
            LIMIT 20
        ''', (user_id,))

        reviews = [dict(row) for row in cursor.fetchall()]

        # Calcular rating médio
        if reviews:
            avg_rating = sum(r['rating'] for r in reviews) / len(reviews)
        else:
            avg_rating = 0

        conn.close()

        return jsonify({
            'status': 'success',
            'user_id': user_id,
            'average_rating': round(avg_rating, 2),
            'total_reviews': len(reviews),
            'reviews': reviews
        }), 200

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

# ============================================================================
# MARKET STATS
# ============================================================================

@marketplace_bp.route('/trending', methods=['GET'])
def get_trending():
    """Obter cartas trending (mais anúncios, preço médio)"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT
                card_name,
                card_id,
                COUNT(*) as listing_count,
                AVG(price) as avg_price,
                MIN(price) as min_price,
                MAX(price) as max_price
            FROM marketplace_listings
            WHERE status = 'active'
            GROUP BY card_id
            ORDER BY listing_count DESC
            LIMIT 20
        ''')

        trending = [dict(row) for row in cursor.fetchall()]
        conn.close()

        return jsonify({
            'status': 'success',
            'count': len(trending),
            'trending': trending
        }), 200

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

@marketplace_bp.route('/deals', methods=['GET'])
def get_deals():
    """Obter melhores ofertas (preço mais baixo por carta)"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT
                card_name,
                card_id,
                MIN(price) as best_price,
                condition,
                id as listing_id
            FROM marketplace_listings
            WHERE status = 'active' AND listing_type = 'sale'
            GROUP BY card_id, condition
            ORDER BY best_price ASC
            LIMIT 20
        ''')

        deals = [dict(row) for row in cursor.fetchall()]
        conn.close()

        return jsonify({
            'status': 'success',
            'count': len(deals),
            'deals': deals
        }), 200

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400
