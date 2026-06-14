# -*- coding: utf-8 -*-
"""
Portfolio Manager Routes - Fase 1 SLABR 2.0
Endpoints para gerenciar coleção de cartas do usuário
"""

from flask import Blueprint, request, jsonify
from datetime import datetime
import uuid
import sqlite3
import csv
from io import StringIO

portfolio_bp = Blueprint('portfolio', __name__, url_prefix='/api/portfolio')

# Conexão com database
def get_db_connection():
    conn = sqlite3.connect('pokemon_catalog.db')
    conn.row_factory = sqlite3.Row
    return conn

# ============================================================================
# COLEÇÕES - Create, Read, Update, Delete
# ============================================================================

@portfolio_bp.route('/collections', methods=['POST'])
def create_collection():
    """Criar nova coleção para usuário"""
    data = request.json
    user_id = data.get('user_id')
    card_id = data.get('card_id')
    card_name = data.get('card_name')
    quantity = data.get('quantity', 1)
    condition = data.get('condition', 'NM')
    purchase_price = data.get('purchase_price')

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        collection_id = str(uuid.uuid4())
        cursor.execute('''
            INSERT INTO user_collections
            (id, user_id, card_id, card_name, quantity, condition, purchase_price)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (collection_id, user_id, card_id, card_name, quantity, condition, purchase_price))

        conn.commit()
        conn.close()

        return jsonify({
            'status': 'success',
            'id': collection_id,
            'message': f'Carta {card_name} adicionada à coleção'
        }), 201

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

@portfolio_bp.route('/collections/<user_id>', methods=['GET'])
def get_collections(user_id):
    """Obter todas as cartas da coleção do usuário"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM user_collections
            WHERE user_id = ?
            ORDER BY updated_at DESC
        ''', (user_id,))

        collections = [dict(row) for row in cursor.fetchall()]
        conn.close()

        return jsonify({
            'status': 'success',
            'count': len(collections),
            'collections': collections
        }), 200

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

@portfolio_bp.route('/collections/<collection_id>', methods=['PUT'])
def update_collection(collection_id):
    """Atualizar informações de uma carta na coleção"""
    data = request.json

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        updates = []
        values = []

        if 'quantity' in data:
            updates.append('quantity = ?')
            values.append(data['quantity'])

        if 'condition' in data:
            updates.append('condition = ?')
            values.append(data['condition'])

        if 'purchase_price' in data:
            updates.append('purchase_price = ?')
            values.append(data['purchase_price'])

        if not updates:
            return jsonify({'status': 'error', 'message': 'Nenhum campo para atualizar'}), 400

        updates.append('updated_at = CURRENT_TIMESTAMP')
        values.append(collection_id)

        sql = f"UPDATE user_collections SET {', '.join(updates)} WHERE id = ?"
        cursor.execute(sql, values)
        conn.commit()
        conn.close()

        return jsonify({'status': 'success', 'message': 'Coleção atualizada'}), 200

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

@portfolio_bp.route('/collections/<collection_id>', methods=['DELETE'])
def delete_collection(collection_id):
    """Remover carta da coleção"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('DELETE FROM user_collections WHERE id = ?', (collection_id,))
        conn.commit()
        conn.close()

        return jsonify({'status': 'success', 'message': 'Carta removida da coleção'}), 200

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

# ============================================================================
# IMPORT - Importar coleção via CSV
# ============================================================================

@portfolio_bp.route('/collections/<user_id>/import', methods=['POST'])
def import_csv(user_id):
    """Importar coleção a partir de arquivo CSV"""

    if 'file' not in request.files:
        return jsonify({'status': 'error', 'message': 'Nenhum arquivo enviado'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'status': 'error', 'message': 'Arquivo vazio'}), 400

    if not file.filename.endswith('.csv'):
        return jsonify({'status': 'error', 'message': 'Apenas arquivos CSV permitidos'}), 400

    try:
        stream = StringIO(file.stream.read().decode('utf-8'))
        csv_reader = csv.DictReader(stream)

        conn = get_db_connection()
        cursor = conn.cursor()

        imported_count = 0
        errors = []

        for row in csv_reader:
            try:
                collection_id = str(uuid.uuid4())
                cursor.execute('''
                    INSERT INTO user_collections
                    (id, user_id, card_id, card_name, quantity, condition, purchase_price)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    collection_id,
                    user_id,
                    row.get('card_id', ''),
                    row.get('card_name', ''),
                    int(row.get('quantity', 1)),
                    row.get('condition', 'NM'),
                    float(row.get('purchase_price', 0))
                ))
                imported_count += 1
            except Exception as e:
                errors.append(f"Linha {imported_count + 1}: {str(e)}")

        conn.commit()
        conn.close()

        return jsonify({
            'status': 'success',
            'imported': imported_count,
            'errors': errors,
            'message': f'{imported_count} cartas importadas'
        }), 200

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

# ============================================================================
# DASHBOARD - Estatísticas do portfolio
# ============================================================================

@portfolio_bp.route('/stats/<user_id>', methods=['GET'])
def get_portfolio_stats(user_id):
    """Obter estatísticas do portfolio (valor total, gráficos, etc)"""

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Obter todas as cartas
        cursor.execute('''
            SELECT *
            FROM user_collections
            WHERE user_id = ?
        ''', (user_id,))

        collections = [dict(row) for row in cursor.fetchall()]

        # Calcular estatísticas
        total_cards = len(collections)
        total_cost = sum(float(c.get('purchase_price', 0)) or 0 for c in collections)
        total_value = sum(float(c.get('price_brl', 0)) or 0 for c in collections)

        gain_loss = total_value - total_cost
        gain_loss_pct = (gain_loss / total_cost * 100) if total_cost > 0 else 0

        # Encontrar maiores ganhos/perdas (para agora, sem preço atual)
        biggest_gains = []
        biggest_losses = []

        conn.close()

        return jsonify({
            'status': 'success',
            'user_id': user_id,
            'total_cards': total_cards,
            'total_cost': round(total_cost, 2),
            'total_value': round(total_value, 2),
            'gain_loss': round(gain_loss, 2),
            'gain_loss_pct': round(gain_loss_pct, 2),
            'biggest_gains': biggest_gains,
            'biggest_losses': biggest_losses
        }), 200

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

# ============================================================================
# PRICE ALERTS - Alertas de preço
# ============================================================================

@portfolio_bp.route('/alerts', methods=['POST'])
def create_alert():
    """Criar alerta de preço"""
    data = request.json
    user_id = data.get('user_id')
    card_id = data.get('card_id')
    card_name = data.get('card_name')
    threshold_price = data.get('threshold_price')
    alert_type = data.get('alert_type', 'up')

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        alert_id = str(uuid.uuid4())
        cursor.execute('''
            INSERT INTO price_alerts
            (id, user_id, card_id, card_name, threshold_price, alert_type)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (alert_id, user_id, card_id, card_name, threshold_price, alert_type))

        conn.commit()
        conn.close()

        return jsonify({
            'status': 'success',
            'id': alert_id,
            'message': f'Alerta criado para {card_name}'
        }), 201

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

@portfolio_bp.route('/alerts/<user_id>', methods=['GET'])
def get_alerts(user_id):
    """Obter alertas de preço do usuário"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM price_alerts
            WHERE user_id = ? AND is_active = TRUE
            ORDER BY created_at DESC
        ''', (user_id,))

        alerts = [dict(row) for row in cursor.fetchall()]
        conn.close()

        return jsonify({
            'status': 'success',
            'count': len(alerts),
            'alerts': alerts
        }), 200

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

@portfolio_bp.route('/alerts/<alert_id>', methods=['DELETE'])
def delete_alert(alert_id):
    """Remover alerta de preço"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('UPDATE price_alerts SET is_active = FALSE WHERE id = ?', (alert_id,))
        conn.commit()
        conn.close()

        return jsonify({'status': 'success', 'message': 'Alerta removido'}), 200

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400
