# IMPLEMENTAÇÃO TÉCNICA: FASE 0 (MVP) — Web Scraper Bynx.gg

**Data:** 14 de junho de 2026  
**Objetivo:** Integrar preços bynx.gg no SLABR (Pokémon TCG)  
**Timeline:** 4 semanas  
**Equipe:** 1 Backend + 1 Frontend + 1 DevOps/QA

---

## 1. ARQUITETURA FASE 0

```
┌──────────────────────────┐
│   SLABR Frontend (React) │
│  [Página da Carta]       │
│  ├─ Nome, Set, Imagem    │
│  ├─ Preço SLABR          │
│  ├─ Preço BYNX (novo!) ← │
│  └─ "Comparar em Bynx"   │
└──────────────┬───────────┘
               │
        ┌──────▼───────┐
        │  SLABR API   │
        │  (Flask)     │
        │              │
        │ GET /api/    │
        │ prices/bynx/ │
        │ {cardId}     │
        └──────┬───────┘
               │
        ┌──────▼──────────────┐
        │  Redis Cache        │
        │  Key: bynx:{cardId} │
        │  TTL: 60 min        │
        └──────┬──────────────┘
               │ (if miss)
        ┌──────▼──────────────────┐
        │  Bynx.gg Scraper        │
        │  (Python + Playwright)  │
        │                         │
        │  1. GET bynx.gg/cards   │
        │  2. Parse HTML/JSON     │
        │  3. Extract price       │
        │  4. Cache 60 min        │
        │  5. Return              │
        └─────────────────────────┘
```

---

## 2. STACK & DEPENDÊNCIAS

### Backend (Python)

```python
# requirements.txt
Flask==2.3.0
Playwright==1.40.0
redis==5.0.0
requests==2.31.0
python-dotenv==1.0.0
psycopg2-binary==2.9.9  # PostgreSQL
SQLAlchemy==2.0.0
```

### Frontend (React)

```javascript
// package.json dependencies
"react": "^18.2.0",
"axios": "^1.6.0",
"react-query": "^3.39.0",
"recharts": "^2.10.0",  // para gráficos de preço
```

---

## 3. BACKEND: WEB SCRAPER (Python)

### 3.1 Estrutura de Pastas

```
slabr-backend/
├── app.py                    # Flask app principal
├── scraper/
│  ├── __init__.py
│  ├── bynx_scraper.py       # Lógica de scraping
│  └── price_parser.py       # Parsing de dados
├── cache/
│  ├── __init__.py
│  └── redis_cache.py        # Interface Redis
├── db/
│  ├── __init__.py
│  └── models.py             # SQLAlchemy models
├── config.py                # Env vars
└── requirements.txt
```

### 3.2 Web Scraper (bynx_scraper.py)

```python
# scraper/bynx_scraper.py

import asyncio
import logging
from playwright.async_api import async_playwright
from typing import Optional, Dict, List
import json
import re

logger = logging.getLogger(__name__)

class BynxScraper:
    def __init__(self, headless=True):
        self.base_url = "https://bynx.gg"
        self.headless = headless
        self.browser = None
        self.page = None
        
    async def init_browser(self):
        """Inicializa navegador Playwright"""
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(
            headless=self.headless,
            args=['--disable-blink-features=AutomationControlled']
        )
        self.page = await self.browser.new_page()
        # Fake user agent (bynx pode bloquear bots)
        await self.page.set_user_agent(
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        logger.info("✓ Browser iniciado")

    async def close_browser(self):
        """Fecha navegador"""
        if self.page:
            await self.page.close()
        if self.browser:
            await self.browser.close()
        logger.info("✓ Browser fechado")

    async def search_card(self, card_name: str, set_id: str) -> Optional[Dict]:
        """
        Busca uma carta em bynx.gg
        
        Args:
            card_name: "Charizard"
            set_id: "base1" ou "base1-4"
            
        Returns:
            {
                "id": "base1-4",
                "name": "Charizard",
                "price_brl": 2500.00,
                "variant": "holo",
                "image_url": "...",
                "source": "bynx.gg"
            }
        """
        try:
            # 1. Acessar página de busca
            search_url = f"{self.base_url}/search?q={card_name}"
            await self.page.goto(search_url, wait_until='networkidle')
            
            # 2. Aguardar resultados carregarem
            await self.page.wait_for_selector('[data-testid="card-listing"]', timeout=5000)
            
            # 3. Extrair primeira correspondência (ou melhor match com set_id)
            cards = await self.page.query_selector_all('[data-testid="card-listing"]')
            
            for card_element in cards:
                # Extrair dados do elemento DOM
                card_data = await card_element.evaluate("""
                    el => {
                        const id = el.getAttribute('data-card-id');
                        const name = el.querySelector('[data-testid="card-name"]')?.innerText;
                        const set = el.querySelector('[data-testid="set-name"]')?.innerText;
                        const priceText = el.querySelector('[data-testid="price"]')?.innerText;
                        const imageUrl = el.querySelector('img')?.src;
                        
                        return { id, name, set, priceText, imageUrl };
                    }
                """)
                
                # Verificar se é a carta certa (set_id)
                if set_id in (card_data.get('id') or ''):
                    price = self._parse_price(card_data.get('priceText', ''))
                    
                    return {
                        'id': card_data['id'],
                        'name': card_data['name'],
                        'set': card_data['set'],
                        'price_brl': price,
                        'image_url': card_data['imageUrl'],
                        'source': 'bynx.gg'
                    }
            
            logger.warning(f"Carta não encontrada: {card_name} ({set_id})")
            return None
            
        except Exception as e:
            logger.error(f"Erro ao buscar {card_name}: {str(e)}")
            return None

    async def get_card_prices(self, card_id: str) -> Optional[Dict]:
        """
        Busca preços de uma carta específica (todas as variantes)
        
        Args:
            card_id: "neo4-102"
            
        Returns:
            {
                "id": "neo4-102",
                "name": "Pokémon Personality Test",
                "variants": {
                    "normal": {"price": 5.50, "listings": 3},
                    "holo": {"price": 15.00, "listings": 8},
                    "reverse": {"price": 12.00, "listings": 2}
                },
                "price_history": [
                    {"date": "2026-06-14", "price": 5.50},
                    {"date": "2026-06-13", "price": 5.45}
                ]
            }
        """
        try:
            card_url = f"{self.base_url}/cards/{card_id}"
            await self.page.goto(card_url, wait_until='networkidle')
            
            # Extrair dados via JavaScript
            card_data = await self.page.evaluate("""
                () => {
                    const name = document.querySelector('[data-testid="card-name"]')?.innerText;
                    const variants = {};
                    
                    // Buscar variantes (Normal, Holo, Reverse, etc)
                    const variantElements = document.querySelectorAll('[data-testid="variant-option"]');
                    
                    for (const el of variantElements) {
                        const variant = el.getAttribute('data-variant');
                        const priceText = el.querySelector('[data-testid="price"]')?.innerText || 'N/A';
                        const listings = el.getAttribute('data-listings') || '0';
                        
                        variants[variant] = {
                            price: parseFloat(priceText.replace('R$', '').replace(',', '.')),
                            listings: parseInt(listings)
                        };
                    }
                    
                    return { name, variants };
                }
            """)
            
            # Tentar extrair histórico de preços (se disponível como gráfico JSON)
            price_history = await self._extract_price_history(card_id)
            
            return {
                'id': card_id,
                'name': card_data.get('name'),
                'variants': card_data.get('variants'),
                'price_history': price_history,
                'fetched_at': self._now_iso()
            }
            
        except Exception as e:
            logger.error(f"Erro ao buscar preços de {card_id}: {str(e)}")
            return None

    async def _extract_price_history(self, card_id: str) -> List[Dict]:
        """Tenta extrair histórico de preços (se gráfico Recharts for visível)"""
        try:
            # Se bynx usar Recharts/Chart.js, tentar extrair data
            history = await self.page.evaluate("""
                () => {
                    // Procura por elemento com classe de gráfico
                    const chartEl = document.querySelector('[data-testid="price-chart"]');
                    if (!chartEl) return [];
                    
                    // Aqui dependeria do formato real do DOM/JSON de bynx
                    // Exemplo hipotético:
                    const points = chartEl.querySelectorAll('[data-point]');
                    return Array.from(points).map(p => ({
                        date: p.getAttribute('data-date'),
                        price: parseFloat(p.getAttribute('data-price'))
                    }));
                }
            """)
            return history or []
        except:
            return []

    @staticmethod
    def _parse_price(price_text: str) -> float:
        """Extrai número de string como 'R$ 2.500,50'"""
        if not price_text:
            return 0.0
        # Remove 'R$', espaços, converte vírgula → ponto
        cleaned = price_text.replace('R$', '').strip()
        cleaned = cleaned.replace('.', '').replace(',', '.')
        try:
            return float(cleaned)
        except ValueError:
            return 0.0

    @staticmethod
    def _now_iso() -> str:
        from datetime import datetime
        return datetime.utcnow().isoformat() + 'Z'


# Uso
async def main():
    scraper = BynxScraper(headless=True)
    await scraper.init_browser()
    
    try:
        # Exemplo 1: Buscar carta específica
        card = await scraper.search_card("Charizard", "base1-4")
        print(f"Encontrado: {card}")
        
        # Exemplo 2: Buscar preços (todas variantes)
        prices = await scraper.get_card_prices("base1-4")
        print(f"Preços: {prices}")
        
    finally:
        await scraper.close_browser()

if __name__ == '__main__':
    asyncio.run(main())
```

### 3.3 Cache Redis (redis_cache.py)

```python
# cache/redis_cache.py

import redis
import json
import logging
from typing import Optional, Dict
from datetime import timedelta

logger = logging.getLogger(__name__)

class PriceCache:
    def __init__(self, redis_url: str = 'redis://localhost:6379/0'):
        self.redis = redis.from_url(redis_url, decode_responses=True)
        self.ttl = timedelta(minutes=60)  # Cache por 1 hora
        
    def get(self, key: str) -> Optional[Dict]:
        """Busca preço do cache"""
        try:
            data = self.redis.get(f"bynx:{key}")
            if data:
                logger.info(f"✓ Cache hit: {key}")
                return json.loads(data)
            logger.info(f"✗ Cache miss: {key}")
            return None
        except Exception as e:
            logger.error(f"Erro ao ler cache: {str(e)}")
            return None

    def set(self, key: str, data: Dict, ttl: timedelta = None):
        """Armazena preço no cache"""
        try:
            ttl = ttl or self.ttl
            self.redis.setex(
                f"bynx:{key}",
                int(ttl.total_seconds()),
                json.dumps(data)
            )
            logger.info(f"✓ Cache set: {key} (TTL: {ttl.total_seconds()}s)")
        except Exception as e:
            logger.error(f"Erro ao escrever cache: {str(e)}")

    def invalidate(self, key: str):
        """Invalida cache (para refresh manual)"""
        self.redis.delete(f"bynx:{key}")
        logger.info(f"✓ Cache invalidado: {key}")

    def get_all_bynx_keys(self) -> list:
        """Lista todas as chaves bynx em cache"""
        return self.redis.keys("bynx:*")
```

### 3.4 Flask API (app.py)

```python
# app.py

from flask import Flask, jsonify, request, g
from functools import wraps
import asyncio
import logging
import os
from dotenv import load_dotenv

from scraper.bynx_scraper import BynxScraper
from cache.redis_cache import PriceCache
from db.models import db, Card, PriceHistory

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://user:pass@localhost/slabr')
db.init_app(app)

# Inicializar cache e scraper
cache = PriceCache(os.getenv('REDIS_URL', 'redis://localhost:6379/0'))
scraper = None

logger = logging.getLogger(__name__)

@app.before_request
def before_request():
    """Inicializa scraper na primeira request (lazy loading)"""
    global scraper
    if scraper is None:
        scraper = BynxScraper(headless=True)
        asyncio.create_task(scraper.init_browser())

def async_route(f):
    """Decorator para rotas assíncronas"""
    @wraps(f)
    def wrapper(*args, **kwargs):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop.run_until_complete(f(*args, **kwargs))
    return wrapper

# ========== ROTAS ==========

@app.route('/api/v1/prices/bynx/<card_id>', methods=['GET'])
@async_route
async def get_bynx_price(card_id: str):
    """
    Busca preço de uma carta em bynx.gg
    
    GET /api/v1/prices/bynx/base1-4
    
    Response:
    {
        "success": true,
        "data": {
            "id": "base1-4",
            "name": "Charizard",
            "price_brl": 2500.00,
            "variants": { ... },
            "source": "bynx.gg",
            "cached": true,
            "expires_at": "2026-06-14T11:30:00Z"
        }
    }
    """
    try:
        # 1. Tentar cache
        cached_data = cache.get(card_id)
        if cached_data:
            return jsonify({
                'success': True,
                'data': cached_data,
                'cached': True
            }), 200

        # 2. Se não em cache, buscar de bynx
        price_data = await scraper.get_card_prices(card_id)
        
        if not price_data:
            return jsonify({
                'success': False,
                'error': 'Carta não encontrada em bynx.gg'
            }), 404

        # 3. Cachear resultado
        cache.set(card_id, price_data)
        
        # 4. Salvar no banco (histórico)
        _save_price_history(card_id, price_data)

        return jsonify({
            'success': True,
            'data': price_data,
            'cached': False
        }), 200

    except Exception as e:
        logger.error(f"Erro em get_bynx_price: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/v1/prices/bynx/search', methods=['POST'])
@async_route
async def search_bynx_card():
    """
    Busca uma carta por nome/set
    
    POST /api/v1/prices/bynx/search
    Body: { "name": "Charizard", "set_id": "base1" }
    """
    try:
        data = request.get_json()
        name = data.get('name')
        set_id = data.get('set_id')
        
        if not name or not set_id:
            return jsonify({'error': 'name e set_id obrigatórios'}), 400

        # Buscar em bynx
        card = await scraper.search_card(name, set_id)
        
        if not card:
            return jsonify({
                'success': False,
                'error': f'Carta {name} ({set_id}) não encontrada'
            }), 404

        # Cachear e salvar
        cache.set(card['id'], card)
        _save_price_history(card['id'], card)

        return jsonify({
            'success': True,
            'data': card
        }), 200

    except Exception as e:
        logger.error(f"Erro em search_bynx_card: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/v1/prices/bynx/<card_id>/history', methods=['GET'])
def get_price_history(card_id: str):
    """
    Retorna histórico de preços de uma carta
    
    GET /api/v1/prices/bynx/base1-4/history?days=7
    """
    try:
        days = request.args.get('days', 7, type=int)
        
        history = db.session.query(PriceHistory).filter(
            PriceHistory.card_id == card_id,
            PriceHistory.source == 'bynx.gg'
        ).order_by(PriceHistory.date.desc()).limit(days).all()
        
        return jsonify({
            'success': True,
            'data': [
                {
                    'date': h.date.isoformat(),
                    'price': float(h.price_brl),
                    'listings': h.metadata.get('listings', 0) if h.metadata else 0
                }
                for h in history
            ]
        }), 200

    except Exception as e:
        logger.error(f"Erro em get_price_history: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/v1/health', methods=['GET'])
def health_check():
    """Health check para monitoring"""
    return jsonify({
        'status': 'ok',
        'service': 'bynx-price-integration',
        'version': '0.1.0'
    }), 200

# ========== UTILITÁRIOS ==========

def _save_price_history(card_id: str, price_data: Dict):
    """Salva preço no banco para auditoria/trending"""
    try:
        from datetime import datetime
        
        # Extrair preço (usar variante principal)
        variants = price_data.get('variants', {})
        avg_price = sum(v.get('price', 0) for v in variants.values()) / len(variants) if variants else 0
        
        # Salvar
        history = PriceHistory(
            card_id=card_id,
            price_brl=avg_price,
            source='bynx.gg',
            date=datetime.utcnow().date(),
            metadata={'variants': variants}
        )
        db.session.add(history)
        db.session.commit()
        logger.info(f"✓ Preço salvo no banco: {card_id}")
    except Exception as e:
        logger.error(f"Erro ao salvar histórico: {str(e)}")
        db.session.rollback()

# ========== MAIN ==========

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Criar tabelas
    
    app.run(
        host=os.getenv('SLABR_HOST', '0.0.0.0'),
        port=int(os.getenv('SLABR_PORT', 5000)),
        debug=os.getenv('FLASK_ENV') == 'development'
    )
```

---

## 4. FRONTEND: EXIBIÇÃO DE PREÇOS (React)

### 4.1 Componente PricePanel.jsx

```jsx
// components/PricePanel.jsx

import React, { useState, useEffect } from 'react';
import { useQuery } from 'react-query';
import axios from 'axios';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import './PricePanel.css';

const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:5000/api/v1';

const PricePanel = ({ cardId }) => {
  const [isLoading, setIsLoading] = useState(false);

  // Buscar preços de bynx
  const { data: priceData, error: priceError, refetch } = useQuery(
    ['bynx-price', cardId],
    async () => {
      const response = await axios.get(
        `${API_BASE}/prices/bynx/${cardId}`
      );
      return response.data.data;
    },
    {
      staleTime: 5 * 60 * 1000, // 5 min cache no cliente
      retry: 1,
      enabled: !!cardId
    }
  );

  // Buscar histórico de preços
  const { data: historyData } = useQuery(
    ['bynx-history', cardId],
    async () => {
      const response = await axios.get(
        `${API_BASE}/prices/bynx/${cardId}/history?days=7`
      );
      return response.data.data;
    },
    { staleTime: 1 * 60 * 60 * 1000 } // 1h cache
  );

  const handleRefresh = async () => {
    setIsLoading(true);
    await refetch();
    setIsLoading(false);
  };

  if (priceError) {
    return (
      <div className="price-panel error">
        <p>Não foi possível carregar preço de bynx.gg</p>
        <button onClick={handleRefresh} disabled={isLoading}>
          {isLoading ? 'Carregando...' : 'Tentar novamente'}
        </button>
      </div>
    );
  }

  if (!priceData) {
    return (
      <div className="price-panel loading">
        <div className="spinner"></div>
        <p>Buscando preço em bynx.gg...</p>
      </div>
    );
  }

  const variants = priceData.variants || {};
  const mainVariant = Object.entries(variants)[0] || ['normal', { price: 0 }];
  const [variantName, variantData] = mainVariant;

  return (
    <div className="price-panel bynx">
      <div className="price-header">
        <h3>
          <img src="/icons/bynx-logo.svg" alt="Bynx" className="logo" />
          Preço em Bynx.gg
        </h3>
        <button 
          onClick={handleRefresh} 
          disabled={isLoading}
          title="Atualizar preço"
          className="btn-refresh"
        >
          🔄
        </button>
      </div>

      {/* Preço Principal */}
      <div className="price-main">
        <div className="price-value">
          R$ {variantData.price?.toLocaleString('pt-BR', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
          })}
        </div>
        <div className="variant-badge">{variantName}</div>
      </div>

      {/* Variantes */}
      {Object.keys(variants).length > 1 && (
        <div className="variants">
          <p className="variants-label">Outras variantes:</p>
          <div className="variant-list">
            {Object.entries(variants).map(([variant, data]) => (
              <div key={variant} className="variant-item">
                <span className="variant-name">{variant}</span>
                <span className="variant-price">
                  R$ {data.price.toLocaleString('pt-BR', {
                    minimumFractionDigits: 2
                  })}
                </span>
                <span className="variant-listings">
                  ({data.listings} anúncios)
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Gráfico de Histórico */}
      {historyData && historyData.length > 1 && (
        <div className="price-chart">
          <p className="chart-label">Histórico (últimos 7 dias)</p>
          <ResponsiveContainer width="100%" height={200}>
            <LineChart data={historyData}>
              <XAxis 
                dataKey="date" 
                tick={{ fontSize: 12 }}
                tickFormatter={(date) => new Date(date).toLocaleDateString('pt-BR', {
                  month: 'short',
                  day: 'numeric'
                })}
              />
              <YAxis tick={{ fontSize: 12 }} />
              <Tooltip 
                formatter={(value) => `R$ ${value.toFixed(2)}`}
                labelFormatter={(date) => new Date(date).toLocaleDateString('pt-BR')}
              />
              <Line 
                type="monotone" 
                dataKey="price" 
                stroke="#2563eb" 
                dot={false}
                strokeWidth={2}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Info & CTA */}
      <div className="price-actions">
        <a 
          href={`https://bynx.gg/cards/${cardId}`}
          target="_blank"
          rel="noopener noreferrer"
          className="btn btn-primary"
        >
          Comparar em Bynx.gg →
        </a>
      </div>

      {/* Metadata */}
      <div className="price-meta">
        {priceData.cached && <span className="badge cached">Cache</span>}
        <span className="timestamp">
          Atualizado: {new Date(priceData.fetched_at).toLocaleString('pt-BR')}
        </span>
      </div>
    </div>
  );
};

export default PricePanel;
```

### 4.2 CSS (PricePanel.css)

```css
/* components/PricePanel.css */

.price-panel {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  padding: 20px;
  margin: 20px 0;
  color: white;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

.price-panel.error {
  background: #ef4444;
  border: 1px solid #dc2626;
}

.price-panel.loading {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 15px;
  min-height: 100px;
}

.spinner {
  width: 24px;
  height: 24px;
  border: 3px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.price-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
  padding-bottom: 10px;
}

.price-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
}

.price-header .logo {
  width: 20px;
  height: 20px;
}

.btn-refresh {
  background: rgba(255, 255, 255, 0.2);
  border: none;
  color: white;
  font-size: 18px;
  padding: 5px 10px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-refresh:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.3);
}

.btn-refresh:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.price-main {
  text-align: center;
  padding: 20px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
  margin-bottom: 15px;
}

.price-value {
  font-size: 36px;
  font-weight: 700;
  margin-bottom: 8px;
}

.variant-badge {
  display: inline-block;
  background: rgba(255, 255, 255, 0.2);
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
  text-transform: uppercase;
}

.variants {
  margin-bottom: 15px;
}

.variants-label {
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  opacity: 0.8;
  margin: 0 0 10px;
}

.variant-list {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 10px;
}

.variant-item {
  background: rgba(255, 255, 255, 0.1);
  padding: 10px;
  border-radius: 8px;
  font-size: 12px;
  text-align: center;
}

.variant-name {
  display: block;
  font-weight: 600;
  margin-bottom: 4px;
  text-transform: capitalize;
}

.variant-price {
  display: block;
  font-size: 14px;
  font-weight: 700;
  margin-bottom: 3px;
}

.variant-listings {
  display: block;
  font-size: 11px;
  opacity: 0.8;
}

.price-chart {
  margin: 15px 0;
  padding: 15px 0;
  border-top: 1px solid rgba(255, 255, 255, 0.2);
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
}

.chart-label {
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  opacity: 0.8;
  margin: 0 0 10px;
}

/* Customizar Recharts dentro do painel */
.price-chart .recharts-wrapper {
  filter: brightness(1.1);
}

.price-chart .recharts-cartesian-axis-tick text {
  fill: rgba(255, 255, 255, 0.7) !important;
}

.price-actions {
  margin: 15px 0;
}

.btn {
  display: inline-block;
  padding: 10px 16px;
  border: none;
  border-radius: 6px;
  font-weight: 600;
  font-size: 14px;
  text-decoration: none;
  cursor: pointer;
  transition: all 0.2s;
  text-align: center;
}

.btn-primary {
  background: rgba(255, 255, 255, 0.25);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.3);
  width: 100%;
}

.btn-primary:hover {
  background: rgba(255, 255, 255, 0.35);
  border-color: rgba(255, 255, 255, 0.5);
}

.price-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 11px;
  opacity: 0.8;
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.badge {
  display: inline-block;
  background: rgba(255, 255, 255, 0.15);
  padding: 2px 8px;
  border-radius: 12px;
  font-weight: 500;
}

.timestamp {
  text-align: right;
}

/* Responsivo */
@media (max-width: 640px) {
  .price-panel {
    padding: 15px;
  }

  .price-main {
    padding: 15px 0;
  }

  .price-value {
    font-size: 28px;
  }

  .variant-list {
    grid-template-columns: 1fr 1fr;
  }

  .price-chart {
    margin: 10px 0;
  }
}
```

### 4.3 Integração em CardPage.jsx

```jsx
// pages/CardPage.jsx

import React from 'react';
import PricePanel from '../components/PricePanel';
import CardDetails from '../components/CardDetails';

const CardPage = ({ cardId }) => {
  return (
    <div className="card-page">
      <CardDetails cardId={cardId} />
      
      {/* Novo: Painel de preços de bynx */}
      <div className="card-section">
        <h2>Mercado</h2>
        <PricePanel cardId={cardId} />
      </div>
    </div>
  );
};

export default CardPage;
```

---

## 5. DEPLOYMENT & CI/CD

### 5.1 Docker (Backend)

```dockerfile
# Dockerfile

FROM python:3.11-slim

WORKDIR /app

# Instalar Playwright system dependencies
RUN apt-get update && apt-get install -y \
    libgconf-2-4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libxkbcommon0 \
    libpango-1.0-0 \
    libcairo2 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Instalar browsers Playwright
RUN playwright install

COPY . .

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--timeout", "120", "app:app"]
```

### 5.2 GitHub Actions (CI/CD)

```yaml
# .github/workflows/deploy-phase0.yml

name: Deploy Fase 0 (Bynx Integration)

on:
  push:
    branches: [main]
    paths:
      - 'scraper/**'
      - 'cache/**'
      - 'app.py'
      - 'requirements.txt'
      - 'Dockerfile'

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          playwright install
      
      - name: Run tests
        run: pytest tests/ -v --cov=scraper,cache
      
      - name: Lint
        run: |
          flake8 scraper/ cache/ app.py

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Build Docker image
        run: |
          docker build -t slabr-bynx:${{ github.sha }} .
          docker tag slabr-bynx:${{ github.sha }} slabr-bynx:latest
      
      - name: Push to ECR
        run: |
          aws ecr get-login-password | docker login --username AWS --password-stdin ${{ secrets.AWS_ACCOUNT_ID }}.dkr.ecr.us-east-1.amazonaws.com
          docker tag slabr-bynx:latest ${{ secrets.AWS_ACCOUNT_ID }}.dkr.ecr.us-east-1.amazonaws.com/slabr-bynx:latest
          docker push ${{ secrets.AWS_ACCOUNT_ID }}.dkr.ecr.us-east-1.amazonaws.com/slabr-bynx:latest

  deploy:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to Staging
        run: |
          aws eks update-kubeconfig --region us-east-1 --name slabr-staging
          kubectl set image deployment/bynx-scraper bynx-scraper=${{ secrets.AWS_ACCOUNT_ID }}.dkr.ecr.us-east-1.amazonaws.com/slabr-bynx:latest -n slabr-staging
          kubectl rollout status deployment/bynx-scraper -n slabr-staging
      
      - name: Run smoke tests
        run: |
          curl -f https://staging.slabr.br/api/v1/health || exit 1
```

---

## 6. MONITORAMENTO & ALERTAS

### 6.1 Prometheus Metrics (app.py adição)

```python
# app.py - adicionar ao fim

from prometheus_client import Counter, Histogram, generate_latest
from prometheus_client import REGISTRY

# Métricas
scrape_requests = Counter(
    'bynx_scrape_requests_total',
    'Total de requisições de scraping',
    ['status', 'card_id']
)

scrape_duration = Histogram(
    'bynx_scrape_duration_seconds',
    'Duração das requisições de scraping'
)

cache_hits = Counter(
    'bynx_cache_hits_total',
    'Total de cache hits'
)

cache_misses = Counter(
    'bynx_cache_misses_total',
    'Total de cache misses'
)

@app.route('/metrics', methods=['GET'])
def metrics():
    """Endpoint Prometheus"""
    return generate_latest(REGISTRY)
```

### 6.2 alertas.yml (Alertmanager)

```yaml
# monitoring/alertas.yml

groups:
- name: bynx-integration
  interval: 30s
  rules:
  
  - alert: BynxScraperDown
    expr: up{job="bynx-scraper"} == 0
    for: 5m
    labels:
      severity: critical
    annotations:
      summary: "Bynx scraper está offline"
      description: "Scraper de preços não responde há 5 minutos"
  
  - alert: BynxHighErrorRate
    expr: rate(bynx_scrape_requests_total{status="error"}[5m]) > 0.1
    for: 10m
    labels:
      severity: warning
    annotations:
      summary: "Taxa de erro alta em bynx scraper"
      description: "Mais de 10% das requisições falhando"
  
  - alert: BynxScraperSlow
    expr: histogram_quantile(0.95, rate(bynx_scrape_duration_seconds[5m])) > 10
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "Scraper lento"
      description: "P95 de latência acima de 10 segundos"
```

---

## 7. TESTES

### 7.1 Unit Tests (test_scraper.py)

```python
# tests/test_scraper.py

import pytest
import asyncio
from scraper.bynx_scraper import BynxScraper

@pytest.mark.asyncio
async def test_search_card_found():
    scraper = BynxScraper(headless=True)
    await scraper.init_browser()
    
    try:
        card = await scraper.search_card("Charizard", "base1")
        assert card is not None
        assert 'price_brl' in card
        assert card['price_brl'] > 0
    finally:
        await scraper.close_browser()

@pytest.mark.asyncio
async def test_search_card_not_found():
    scraper = BynxScraper(headless=True)
    await scraper.init_browser()
    
    try:
        card = await scraper.search_card("CardaoXXXInvalido", "fake123")
        assert card is None
    finally:
        await scraper.close_browser()

@pytest.mark.asyncio
async def test_parse_price():
    prices = [
        ("R$ 2.500,50", 2500.50),
        ("R$ 10,99", 10.99),
        ("R$ 1.000.000,00", 1000000.00),
    ]
    
    for price_text, expected in prices:
        result = BynxScraper._parse_price(price_text)
        assert result == expected

def test_cache_get_set():
    from cache.redis_cache import PriceCache
    cache = PriceCache()
    
    data = {"price": 100, "listings": 5}
    cache.set("test-key", data)
    
    retrieved = cache.get("test-key")
    assert retrieved == data
    
    cache.invalidate("test-key")
    assert cache.get("test-key") is None
```

---

## 8. VARIÁVEIS DE AMBIENTE

```bash
# .env (não commitar em git)

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/slabr

# Redis
REDIS_URL=redis://localhost:6379/0

# Flask
FLASK_ENV=development
SLABR_HOST=0.0.0.0
SLABR_PORT=5000

# Bynx Scraper
BYNX_BASE_URL=https://bynx.gg
BYNX_HEADLESS=true
BYNX_TIMEOUT_MS=30000

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/app.log

# Sentry (error tracking)
SENTRY_DSN=https://xxx@sentry.io/xxx
```

---

## 9. ROADMAP DE EXECUÇÃO (4 semanas)

```
SEMANA 1:
├─ Setup repo + Docker + CI/CD
├─ Implementar BynxScraper (básico)
├─ Iniciar testes unitários
└─ Deliverable: Scraper consegue extrair preços

SEMANA 2:
├─ Implementar Redis cache
├─ Criar endpoints Flask
├─ Integrar PostgreSQL (histórico)
├─ Tests de integração
└─ Deliverable: API respondendo em staging

SEMANA 3:
├─ Componente React PricePanel
├─ Integração frontend ↔ backend
├─ Testes E2E (Playwright)
├─ Monitoramento (Prometheus + alerts)
└─ Deliverable: Feature funcional em staging

SEMANA 4:
├─ Performance tunning
├─ Testes de carga
├─ Documentação
├─ Gradual rollout (5% → 100%)
└─ Deliverable: MVP ao vivo em produção
```

---

## 10. CHECKPOINTS (Go/No-Go)

```
CHECKPOINT 1 (Fim Semana 1):
✓ Scraper consegue buscar preços de bynx.gg
✓ Nenhum erro de sintaxe/import
✓ CI/CD pipeline funcionando

CHECKPOINT 2 (Fim Semana 2):
✓ Cache Redis operacional (TTL 60min)
✓ Endpoint /api/v1/prices/bynx/{cardId} retorna 200
✓ Histórico de preços salvando no banco
✓ Uptime scraper >95% por 24h

CHECKPOINT 3 (Fim Semana 3):
✓ UI exibindo preços de bynx
✓ Cliques em "Comparar Bynx" convertendo >5%
✓ NPS de usuários teste >40
✓ Sem crashes/errors críticos

CHECKPOINT 4 (Fim Semana 4):
✓ P95 latência <2s
✓ Uptime 99%+ por 1 semana
✓ Zero production incidents
✓ Ready para Fase 1
```

