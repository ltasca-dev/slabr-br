# -*- coding: utf-8 -*-
"""
Endpoint Flask para integrar preços Bynx.gg no SLABR.br
Adicione este código em api.py
"""

from flask import jsonify, request
from functools import lru_cache
from datetime import datetime, timedelta
import os
import sys

# Import do scraper
sys.path.insert(0, os.path.dirname(__file__))
from scraper_bynx import BynxScraperSync

# Cache simples (melhorar com Redis em produção)
_price_cache = {}
_cache_ttl = 3600  # 1 hora

scraper = BynxScraperSync()

def _get_cache_key(card_id: str) -> str:
    """Gera chave de cache"""
    return f"bynx_price:{card_id}"

def _is_cache_valid(cached_at: datetime) -> bool:
    """Verifica se cache ainda é válido"""
    return (datetime.now() - cached_at).total_seconds() < _cache_ttl

def _get_cached_price(card_id: str) -> dict:
    """Obtém preço do cache se válido"""
    key = _get_cache_key(card_id)
    if key in _price_cache:
        cached = _price_cache[key]
        if _is_cache_valid(cached['timestamp']):
            return cached['data']
    return None

def _set_cache(card_id: str, data: dict):
    """Armazena preço em cache"""
    key = _get_cache_key(card_id)
    _price_cache[key] = {
        'data': data,
        'timestamp': datetime.now()
    }

@app.route("/api/prices/bynx/<card_id>", methods=["GET", "OPTIONS"])
def get_bynx_price(card_id):
    """
    Retorna preço de uma carta em Bynx.gg

    GET /api/prices/bynx/base1-4

    Response:
    {
        "found": true,
        "card_id": "base1-4",
        "name": "Charizard",
        "price_brl": 2500.00,
        "source": "bynx.gg",
        "timestamp": "2026-06-14T10:30:00",
        "cached": false
    }
    """
    if request.method == "OPTIONS":
        return ("", 204)

    try:
        # 1. Verificar cache primeiro
        cached_price = _get_cached_price(card_id)
        if cached_price:
            cached_price['cached'] = True
            return jsonify(cached_price)

        # 2. Buscar carta no banco (para obter nome)
        db_card = db().execute(
            "SELECT id, name FROM cards WHERE id = ?", (card_id,)
        ).fetchone()

        if not db_card:
            return jsonify({"found": False, "error": "Carta não encontrada"}), 404

        # 3. Buscar preço em Bynx
        card_name = db_card["name"]
        bynx_price = scraper.search_card(card_name, card_id)

        if not bynx_price:
            return jsonify({
                "found": False,
                "card_id": card_id,
                "error": "Preço não disponível em Bynx.gg"
            }), 404

        # 4. Armazenar em cache
        response_data = {
            "found": True,
            "card_id": card_id,
            "name": bynx_price.get('name'),
            "price_brl": bynx_price.get('price_brl'),
            "source": "bynx.gg",
            "timestamp": bynx_price.get('timestamp'),
            "cached": False
        }

        _set_cache(card_id, response_data)

        return jsonify(response_data)

    except Exception as e:
        return jsonify({
            "found": False,
            "error": f"Erro ao buscar preço: {str(e)}"
        }), 500

@app.route("/api/prices/bynx/compare/<card_id>", methods=["GET"])
def compare_prices(card_id):
    """
    Compara preço SLABR vs Bynx.gg

    GET /api/prices/bynx/compare/base1-4

    Response:
    {
        "card_id": "base1-4",
        "name": "Charizard",
        "slabr_price": 3500.00,
        "bynx_price": 2500.00,
        "difference": 1000.00,
        "difference_pct": 40.0,
        "more_expensive_in": "slabr"
    }
    """
    try:
        # 1. Buscar preço SLABR (primeira oferta)
        slabr_offer = db().execute(
            "SELECT declared_value_cents FROM graded_items WHERE card_id = ? AND public = 1 ORDER BY declared_value_cents LIMIT 1",
            (card_id,)
        ).fetchone()

        slabr_price = (slabr_offer['declared_value_cents'] / 100) if slabr_offer else None

        # 2. Buscar preço Bynx
        bynx_response = get_bynx_price(card_id)
        bynx_data = bynx_response[0].get_json()
        bynx_price = bynx_data.get('price_brl') if bynx_data.get('found') else None

        # 3. Buscar nome da carta
        card = db().execute("SELECT name FROM cards WHERE id = ?", (card_id,)).fetchone()

        if not card:
            return jsonify({"error": "Carta não encontrada"}), 404

        # 4. Calcular diferença
        result = {
            "card_id": card_id,
            "name": card["name"],
            "slabr_price": slabr_price,
            "bynx_price": bynx_price,
            "difference": None,
            "difference_pct": None,
            "more_expensive_in": None
        }

        if slabr_price and bynx_price:
            diff = slabr_price - bynx_price
            diff_pct = (diff / bynx_price) * 100

            result["difference"] = diff
            result["difference_pct"] = round(diff_pct, 2)
            result["more_expensive_in"] = "slabr" if diff > 0 else "bynx"

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/prices/bynx/bulk", methods=["POST"])
def get_bulk_bynx_prices():
    """
    Busca preços em lote para múltiplas cartas

    POST /api/prices/bynx/bulk
    Body: {"card_ids": ["base1-4", "base1-1", "base2-11"]}

    Response:
    {
        "results": [
            {"card_id": "base1-4", "found": true, "price_brl": 2500.00, ...},
            {"card_id": "base1-1", "found": false, "error": "..."},
            ...
        ],
        "success_count": 2,
        "total_count": 3
    }
    """
    try:
        data = request.get_json(force=True) or {}
        card_ids = data.get('card_ids', [])

        if not card_ids:
            return jsonify({"error": "card_ids obrigatório"}), 400

        results = []
        for card_id in card_ids[:50]:  # Limitar a 50 cartas
            response = get_bynx_price(card_id)
            price_data = response[0].get_json() if isinstance(response, tuple) else response.get_json()
            results.append(price_data)

        return jsonify({
            "results": results,
            "success_count": sum(1 for r in results if r.get('found')),
            "total_count": len(results)
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/prices/bynx/health", methods=["GET"])
def bynx_health_check():
    """Health check do scraper Bynx"""
    try:
        # Tenta buscar uma carta conhecida
        test_result = scraper.search_card("Charizard", "base1-4")

        if test_result:
            return jsonify({
                "status": "healthy",
                "scraper": "online",
                "last_test": datetime.now().isoformat(),
                "test_result": "Charizard found"
            })
        else:
            return jsonify({
                "status": "degraded",
                "scraper": "online_but_no_data",
                "last_test": datetime.now().isoformat()
            }), 503

    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "error": str(e)
        }), 503

# ==============================================================
# INSTRUÇÕES DE INTEGRAÇÃO
# ==============================================================
"""
Para integrar no SLABR.br, adicione este código no api.py:

1. No início do arquivo, importe:
   ```python
   from scraper_bynx import BynxScraperSync
   scraper = BynxScraperSync()
   ```

2. Adicione as rotas acima (GET /api/prices/bynx/*)

3. No frontend React, adicione no componente de detalhe da carta:
   ```javascript
   const [bynxPrice, setBynxPrice] = useState(null);

   useEffect(() => {
     fetch(`/api/prices/bynx/${cardId}`)
       .then(r => r.json())
       .then(data => setBynxPrice(data));
   }, [cardId]);

   // Render:
   {bynxPrice && bynxPrice.found && (
     <div className="bynx-price">
       <span>Preço em Bynx: R$ {bynxPrice.price_brl.toLocaleString('pt-BR')}</span>
       <a href={`https://bynx.gg/search?q=${cardId}`} target="_blank">
         Ver em Bynx →
       </a>
     </div>
   )}
   ```

4. Instale dependências:
   ```
   pip install playwright requests
   python -m playwright install chromium
   ```

5. Teste:
   ```
   curl http://localhost:5000/api/prices/bynx/base1-4
   ```
"""
