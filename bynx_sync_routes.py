# -*- coding: utf-8 -*-
"""
Bynx Sync Routes - Fase 1 SLABR 2.0
Sincronizar coleções com Bynx.gg via OAuth
"""

from flask import Blueprint, request, jsonify, url_for, redirect
from datetime import datetime
import uuid
import sqlite3
import json

bynx_sync_bp = Blueprint('bynx_sync', __name__, url_prefix='/api/bynx-sync')

def get_db_connection():
    conn = sqlite3.connect('pokemon_catalog.db')
    conn.row_factory = sqlite3.Row
    return conn

# ============================================================================
# OAUTH - Conectar conta com Bynx.gg
# ============================================================================

@bynx_sync_bp.route('/connect', methods=['POST'])
def connect_bynx():
    """Iniciar fluxo OAuth com Bynx.gg"""
    data = request.json
    user_id = data.get('user_id')

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Gerar state para OAuth
        state = str(uuid.uuid4())

        # Salvar estado pendente
        cursor.execute('''
            INSERT OR REPLACE INTO bynx_oauth_state
            (user_id, state, created_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
        ''', (user_id, state))

        conn.commit()
        conn.close()

        # Redirecionar para Bynx OAuth
        bynx_oauth_url = f"https://bynx.gg/oauth/authorize?client_id=slabr&state={state}&redirect_uri=http://localhost:5000/api/bynx-sync/callback"

        return jsonify({
            'status': 'success',
            'oauth_url': bynx_oauth_url,
            'message': 'Redirecione o usuário para Bynx.gg'
        }), 200

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

@bynx_sync_bp.route('/callback', methods=['GET'])
def oauth_callback():
    """Callback de OAuth - Bynx retorna aqui"""
    state = request.args.get('state')
    code = request.args.get('code')
    error = request.args.get('error')

    if error:
        return jsonify({'status': 'error', 'message': f'Erro OAuth: {error}'}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Verificar state
        cursor.execute('SELECT user_id FROM bynx_oauth_state WHERE state = ? AND created_at > datetime("now", "-10 minutes")', (state,))
        row = cursor.fetchone()

        if not row:
            return jsonify({'status': 'error', 'message': 'State inválido ou expirado'}), 400

        user_id = row['user_id']

        # Aqui você faria a troca do code por token
        # Por enquanto, simulamos com um token
        access_token = str(uuid.uuid4())

        # Salvar conexão
        cursor.execute('''
            INSERT OR REPLACE INTO bynx_integrations
            (id, user_id, access_token, status, last_sync)
            VALUES (?, ?, ?, 'connected', CURRENT_TIMESTAMP)
        ''', (str(uuid.uuid4()), user_id, access_token))

        # Limpar state
        cursor.execute('DELETE FROM bynx_oauth_state WHERE state = ?', (state,))

        conn.commit()
        conn.close()

        return jsonify({
            'status': 'success',
            'message': 'Conectado com sucesso ao Bynx.gg'
        }), 200

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

# ============================================================================
# STATUS & SYNC
# ============================================================================

@bynx_sync_bp.route('/status/<user_id>', methods=['GET'])
def get_sync_status(user_id):
    """Obter status de sincronização"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM bynx_integrations WHERE user_id = ?', (user_id,))
        integration = cursor.fetchone()

        if not integration:
            return jsonify({
                'status': 'not_connected',
                'message': 'Nao conectado ao Bynx.gg',
                'connected': False
            }), 200

        # Contar cartas sincronizadas
        cursor.execute('SELECT COUNT(*) as count FROM bynx_sync_log WHERE user_id = ? AND action = "synced"', (user_id,))
        sync_count = cursor.fetchone()['count']

        conn.close()

        return jsonify({
            'status': 'success',
            'connected': True,
            'user_id': user_id,
            'integration_status': integration['status'],
            'last_sync': integration['last_sync'],
            'synced_cards': sync_count
        }), 200

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

@bynx_sync_bp.route('/sync/<user_id>', methods=['POST'])
def sync_collections(user_id):
    """Sincronizar coleção com Bynx.gg"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Verificar se está conectado
        cursor.execute('SELECT * FROM bynx_integrations WHERE user_id = ?', (user_id,))
        integration = cursor.fetchone()

        if not integration or integration['status'] != 'connected':
            return jsonify({'status': 'error', 'message': 'Nao conectado ao Bynx.gg'}), 400

        # Obter cartas SLABR
        cursor.execute('''
            SELECT * FROM user_collections
            WHERE user_id = ?
        ''', (user_id,))

        slabr_cards = [dict(row) for row in cursor.fetchall()]

        # Simular sync com Bynx
        # Em produção, você faria chamadas HTTP para API do Bynx
        synced_count = 0
        errors = []

        for card in slabr_cards:
            try:
                # Log de sincronização
                cursor.execute('''
                    INSERT INTO bynx_sync_log
                    (id, user_id, card_id, action, synced_at)
                    VALUES (?, ?, ?, 'synced', CURRENT_TIMESTAMP)
                ''', (str(uuid.uuid4()), user_id, card['card_id']))
                synced_count += 1
            except Exception as e:
                errors.append(f"Erro ao sincronizar {card['card_name']}: {str(e)}")

        # Atualizar last_sync
        cursor.execute('''
            UPDATE bynx_integrations
            SET last_sync = CURRENT_TIMESTAMP
            WHERE user_id = ?
        ''', (user_id,))

        conn.commit()
        conn.close()

        return jsonify({
            'status': 'success',
            'synced_cards': synced_count,
            'errors': errors,
            'message': f'{synced_count} cartas sincronizadas'
        }), 200

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

# ============================================================================
# NOTIFICACOES & WEBHOOKS
# ============================================================================

@bynx_sync_bp.route('/webhooks/price-change', methods=['POST'])
def webhook_price_change():
    """Webhook - Bynx notifica mudança de preço"""
    data = request.json
    user_id = data.get('user_id')
    card_id = data.get('card_id')
    old_price = data.get('old_price')
    new_price = data.get('new_price')

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Registrar notificação
        cursor.execute('''
            INSERT INTO bynx_notifications
            (id, user_id, card_id, old_price, new_price, event_type)
            VALUES (?, ?, ?, ?, ?, 'price_change')
        ''', (str(uuid.uuid4()), user_id, card_id, old_price, new_price))

        conn.commit()
        conn.close()

        return jsonify({
            'status': 'success',
            'message': 'Notificacao recebida'
        }), 200

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

@bynx_sync_bp.route('/notifications/<user_id>', methods=['GET'])
def get_notifications(user_id):
    """Obter notificações do Bynx"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM bynx_notifications
            WHERE user_id = ?
            ORDER BY created_at DESC
            LIMIT 20
        ''', (user_id,))

        notifications = [dict(row) for row in cursor.fetchall()]
        conn.close()

        return jsonify({
            'status': 'success',
            'count': len(notifications),
            'notifications': notifications
        }), 200

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

# ============================================================================
# DISCONNECT
# ============================================================================

@bynx_sync_bp.route('/disconnect/<user_id>', methods=['POST'])
def disconnect_bynx(user_id):
    """Desconectar conta do Bynx.gg"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('DELETE FROM bynx_integrations WHERE user_id = ?', (user_id,))
        cursor.execute('DELETE FROM bynx_oauth_state WHERE user_id = ?', (user_id,))

        conn.commit()
        conn.close()

        return jsonify({
            'status': 'success',
            'message': 'Desconectado do Bynx.gg'
        }), 200

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400
