# ESPECIFICAÇÃO TÉCNICA: Integração bynx.gg → SLABR

**Versão:** 1.0  
**Status:** DRAFT - Pronto para Revisão Técnica  
**Data:** 14 de Junho de 2026

---

## 1. ARQUITETURA DE INTEGRAÇÃO

### 1.1 Componentes do Sistema

```
┌─────────────────────────────────────────────────────────┐
│                     SLABR Frontend                       │
│  (React / Vue)  - UI Layer                             │
└──────────────┬──────────────────────────────────────────┘
               │
        ┌──────┴──────┐
        │             │
┌───────▼─────┐  ┌───▼────────────┐
│ SLABR API   │  │ Integration     │
│ (Node/Py)   │  │ Service         │
└───────┬─────┘  └───┬────────────┘
        │            │
        │     ┌──────┴─────────┐
        │     │                │
        │  ┌──▼──────┐   ┌────▼─────────┐
        │  │ Bynx    │   │ Cache/Queue  │
        │  │ Sync    │   │ (Redis)      │
        │  │ Service │   │              │
        │  └──┬──────┘   └──────────────┘
        │     │
┌───────▼─────▼────────────────────────┐
│  SLABR Database (PostgreSQL)          │
│  ├── users                            │
│  ├── cards                            │
│  ├── bynx_sync_metadata               │
│  ├── bynx_price_cache                 │
│  └── marketplace_listings             │
└─────────────────────────────────────┘
        │
        │  (API calls)
        │
┌───────▼──────────────────┐
│   BYNX.GG                │
│  ├── /api/cards          │
│  ├── /api/prices         │
│  ├── /api/collections    │
│  └── /api/marketplace    │
└──────────────────────────┘
```

### 1.2 Fluxo de Dados

```
USER ACTION (SLABR):
1. Usuário adiciona carta à coleção
   │
   ├─► Check local SLABR DB
   ├─► Check bynx_price_cache
   └─► If expired: fetch from bynx.gg API
   │
2. Sistema atualiza preço em tempo real
   │
3. Portfolio recalculado automaticamente
   │
4. Mudanças sincronizadas com bynx.gg (se conectado)
```

---

## 2. MODELO DE DADOS

### 2.1 Schema Adicionado ao SLABR (PostgreSQL)

```sql
-- Sincronização bynx.gg
CREATE TABLE bynx_sync_metadata (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    bynx_user_id VARCHAR(255) UNIQUE,
    access_token VARCHAR(1000),
    refresh_token VARCHAR(1000),
    token_expiry TIMESTAMP,
    last_sync TIMESTAMP,
    sync_status VARCHAR(50) DEFAULT 'idle',  -- idle, syncing, error
    error_message TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Cache de preços de bynx
CREATE TABLE bynx_price_cache (
    id UUID PRIMARY KEY,
    card_id VARCHAR(100),  -- referência a cards.id
    variant_type VARCHAR(50),
    price_brl DECIMAL(10, 2),
    fetched_at TIMESTAMP,
    expires_at TIMESTAMP,
    source VARCHAR(100) DEFAULT 'bynx.gg',
    cached_data JSONB,  -- dados completos da API
    created_at TIMESTAMP DEFAULT NOW()
);

-- Histórico de sincronização
CREATE TABLE bynx_sync_log (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    action VARCHAR(50),  -- 'collection_sync', 'price_update', etc
    status VARCHAR(20),  -- 'success', 'error'
    items_processed INTEGER,
    error_message TEXT,
    duration_ms INTEGER,
    timestamp TIMESTAMP DEFAULT NOW()
);

-- Mapeamento de cartas entre SLABR e bynx
CREATE TABLE card_external_mapping (
    id UUID PRIMARY KEY,
    slabr_card_id VARCHAR(100),
    bynx_card_id VARCHAR(100),  -- e.g., "neo4-102"
    bynx_set_id VARCHAR(50),
    bynx_number VARCHAR(20),
    sync_status VARCHAR(50) DEFAULT 'verified',
    verified_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Configurações de sincronização por usuário
CREATE TABLE user_bynx_settings (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id) UNIQUE,
    auto_sync BOOLEAN DEFAULT TRUE,
    sync_interval_minutes INTEGER DEFAULT 60,
    notify_price_changes BOOLEAN DEFAULT TRUE,
    price_change_threshold DECIMAL(5, 2) DEFAULT 10.0,  -- 10%
    public_profile BOOLEAN DEFAULT FALSE,
    last_settings_change TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### 2.2 Estrutura JSONB para Cache Completo

```json
{
  "card": {
    "id": "neo4-102",
    "name": "Pokémon Personality Test",
    "set": {
      "id": "neo4",
      "name": "Neo Destiny",
      "series": "Neo",
      "region": "BR"
    },
    "number": "102",
    "total_in_set": 105,
    "rarity": "Common",
    "type": "Pokémon"
  },
  "images": {
    "small": "https://bynx.gg/images/cards/neo4/102-small.jpg",
    "large": "https://bynx.gg/images/cards/neo4/102-large.jpg"
  },
  "variants": {
    "normal": {
      "price_brl": 5.50,
      "last_price_update": "2026-06-14T10:30:00Z",
      "grade_distribution": {
        "M": { "price": 8.00, "count": 2 },
        "NM": { "price": 6.50, "count": 5 },
        "EX": { "price": 4.50, "count": 3 },
        "GD": { "price": 2.00, "count": 1 }
      }
    },
    "holo": {
      "price_brl": 15.00,
      "last_price_update": "2026-06-14T10:30:00Z"
    },
    "reverse": {
      "price_brl": 12.00,
      "last_price_update": "2026-06-14T10:30:00Z"
    }
  },
  "price_history": [
    { "date": "2026-06-14", "price": 5.50 },
    { "date": "2026-06-13", "price": 5.45 },
    { "date": "2026-06-12", "price": 5.40 }
  ],
  "metadata": {
    "views": 145,
    "listings_count": 23,
    "last_sold": "2026-06-14T08:15:00Z",
    "popularity_rank": 342
  }
}
```

---

## 3. API BYNX - ENDPOINTS ANALISADOS

### 3.1 Cards Endpoints (Inferidos)

```bash
# GET individual card
GET /api/v1/cards/{card_id}
# Response: Card object com variantes e histórico

# Example:
GET /api/v1/cards/neo4-102
Response: {
  "id": "neo4-102",
  "name": "Pokémon Personality Test",
  "set": { "id": "neo4", "name": "Neo Destiny" },
  "number": "102/105",
  "variants": [ ... ],
  "prices": { ... }
}

# Search cards
GET /api/v1/cards/search?q={query}&set={set_id}&type={type}
# Returns: Array of matching cards

# List sets/editions
GET /api/v1/sets
# Returns: Array of all available sets

# Get set details
GET /api/v1/sets/{set_id}
# Returns: Set info + all cards in set

# Get price history
GET /api/v1/cards/{card_id}/prices/history?days=30
# Returns: Array of historical prices
```

### 3.2 Authentication (Hipótese)

```bash
# OAuth 2.0 Flow
POST /api/v1/auth/authorize
Body: {
  "client_id": "slabr_app_id",
  "redirect_uri": "https://slabr.app/oauth/callback",
  "scope": "collection.read collection.write marketplace.read",
  "state": "random_state_string"
}

# Exchange code for token
POST /api/v1/auth/token
Body: {
  "grant_type": "authorization_code",
  "code": "auth_code_from_above",
  "client_id": "slabr_app_id",
  "client_secret": "slabr_secret"
}

Response: {
  "access_token": "eyJhbGc...",
  "token_type": "Bearer",
  "expires_in": 3600,
  "refresh_token": "refresh_token_string"
}

# Refresh token
POST /api/v1/auth/refresh
Body: {
  "refresh_token": "token_string"
}
```

### 3.3 Collection Management (Hipótese)

```bash
# Get user's collection
GET /api/v1/users/me/collection
Headers: Authorization: Bearer {access_token}
Response: Array of cards in user's collection with quantities

# Add to collection
POST /api/v1/users/me/collection/add
Body: {
  "card_id": "neo4-102",
  "variant": "holo",
  "quantity": 1,
  "condition": "NM",
  "purchase_price": 12.50,
  "purchase_date": "2026-06-14"
}

# Remove from collection
DELETE /api/v1/users/me/collection/{card_id}
Params: variant, quantity

# Get collection stats
GET /api/v1/users/me/collection/stats
Response: {
  "total_cards": 340,
  "total_value_brl": 5400.00,
  "avg_price": 15.88,
  "most_valuable": { ... }
}
```

---

## 4. INTEGRAÇÃO SERVICE - IMPLEMENTAÇÃO

### 4.1 Node.js/TypeScript Service

```typescript
// src/services/bynx-integration.service.ts

import axios, { AxiosInstance } from 'axios';
import redis from 'redis';
import { Logger } from 'winston';

interface BynxConfig {
  baseUrl: string;
  clientId: string;
  clientSecret: string;
  webhookSecret: string;
}

interface CacheOptions {
  ttl: number;  // seconds
  forceRefresh?: boolean;
}

export class BynxIntegrationService {
  private api: AxiosInstance;
  private redis: redis.RedisClient;
  private logger: Logger;

  constructor(config: BynxConfig, redis: redis.RedisClient, logger: Logger) {
    this.api = axios.create({
      baseURL: config.baseUrl,
      timeout: 10000,
    });
    this.redis = redis;
    this.logger = logger;
  }

  // ===== AUTHENTICATION =====
  
  async getAuthorizationUrl(userId: string): Promise<string> {
    const state = generateRandomString(32);
    await this.redis.set(
      `bynx:auth:state:${state}`,
      userId,
      'EX',
      600  // 10 minutes
    );
    
    return `${this.api.defaults.baseURL}/oauth/authorize?` +
      `client_id=${this.config.clientId}` +
      `&redirect_uri=${encodeURIComponent(process.env.SLABR_OAUTH_CALLBACK)}` +
      `&scope=collection.read+collection.write+marketplace.read` +
      `&state=${state}`;
  }

  async exchangeAuthCode(code: string, state: string): Promise<{
    accessToken: string;
    refreshToken: string;
    expiresIn: number;
  }> {
    try {
      const response = await this.api.post('/auth/token', {
        grant_type: 'authorization_code',
        code,
        client_id: this.config.clientId,
        client_secret: this.config.clientSecret,
      });

      return {
        accessToken: response.data.access_token,
        refreshToken: response.data.refresh_token,
        expiresIn: response.data.expires_in,
      };
    } catch (error) {
      this.logger.error('Failed to exchange auth code', error);
      throw error;
    }
  }

  // ===== CARD DATA =====

  async getCard(
    cardId: string,
    options: CacheOptions = { ttl: 3600 }
  ): Promise<any> {
    const cacheKey = `bynx:card:${cardId}`;

    // Check cache first
    if (!options.forceRefresh) {
      const cached = await this.redis.get(cacheKey);
      if (cached) {
        this.logger.debug(`Cache hit for card ${cardId}`);
        return JSON.parse(cached);
      }
    }

    try {
      const response = await this.api.get(`/cards/${cardId}`);
      const cardData = response.data;

      // Cache the result
      await this.redis.set(
        cacheKey,
        JSON.stringify(cardData),
        'EX',
        options.ttl
      );

      return cardData;
    } catch (error) {
      this.logger.error(`Failed to fetch card ${cardId}`, error);
      throw error;
    }
  }

  async searchCards(
    query: string,
    filters: {
      set?: string;
      type?: string;
      rarity?: string;
    } = {}
  ): Promise<any[]> {
    try {
      const response = await this.api.get('/cards/search', {
        params: {
          q: query,
          ...filters,
        },
      });

      return response.data.results;
    } catch (error) {
      this.logger.error('Failed to search cards', error);
      throw error;
    }
  }

  async getPriceHistory(
    cardId: string,
    days: number = 30
  ): Promise<Array<{ date: string; price: number }>> {
    try {
      const response = await this.api.get(
        `/cards/${cardId}/prices/history`,
        {
          params: { days },
        }
      );

      return response.data.history;
    } catch (error) {
      this.logger.error(`Failed to fetch price history for ${cardId}`, error);
      throw error;
    }
  }

  // ===== COLLECTION SYNC =====

  async syncUserCollection(
    userId: string,
    accessToken: string
  ): Promise<{
    added: number;
    updated: number;
    removed: number;
    duration: number;
  }> {
    const startTime = Date.now();
    const api = this.createAuthorizedApi(accessToken);

    try {
      // Fetch user's bynx collection
      const bynxCollection = await api.get('/users/me/collection');
      const bynxCards = bynxCollection.data.cards;

      // Get SLABR user's current collection
      const slabrCollection = await this.getSlabrUserCollection(userId);

      let added = 0;
      let updated = 0;
      let removed = 0;

      // Process additions and updates
      for (const bynxCard of bynxCards) {
        const slabrCard = slabrCollection.find(
          (c: any) => c.bynxCardId === bynxCard.id
        );

        if (!slabrCard) {
          // New card - add it
          await this.addCardToSlabrCollection(userId, bynxCard);
          added++;
        } else if (this.hasChanged(slabrCard, bynxCard)) {
          // Updated - sync it
          await this.updateSlabrCard(userId, slabrCard.id, bynxCard);
          updated++;
        }
      }

      // Process removals (cards in SLABR but not in bynx anymore)
      for (const slabrCard of slabrCollection) {
        if (!bynxCards.find((c: any) => c.id === slabrCard.bynxCardId)) {
          // Card was removed from bynx - remove from SLABR too
          // (or just mark as not synced)
          removed++;
        }
      }

      const duration = Date.now() - startTime;

      await this.logSync(userId, 'collection_sync', 'success', {
        added,
        updated,
        removed,
      }, duration);

      return { added, updated, removed, duration };
    } catch (error) {
      const duration = Date.now() - startTime;
      await this.logSync(userId, 'collection_sync', 'error', {}, duration);
      this.logger.error(`Collection sync failed for user ${userId}`, error);
      throw error;
    }
  }

  // ===== PRICE UPDATES =====

  async updatePriceCache(cardId: string, forceRefresh: boolean = false): Promise<void> {
    try {
      const card = await this.getCard(cardId, { 
        ttl: 3600,
        forceRefresh 
      });

      // Store in cache with price data
      await this.redis.set(
        `bynx:price_cache:${cardId}`,
        JSON.stringify({
          cardId,
          prices: card.variants,
          fetchedAt: new Date(),
          expiresAt: new Date(Date.now() + 3600 * 1000),
          priceHistory: card.price_history,
        }),
        'EX',
        3600
      );

      // Update in DB as well
      await this.updatePriceCacheInDB(cardId, card);
    } catch (error) {
      this.logger.error(`Failed to update price cache for ${cardId}`, error);
    }
  }

  // ===== WEBHOOKS (optional) =====

  async validateWebhookSignature(
    payload: string,
    signature: string
  ): Promise<boolean> {
    const crypto = require('crypto');
    const hash = crypto
      .createHmac('sha256', this.config.webhookSecret)
      .update(payload)
      .digest('hex');

    return hash === signature;
  }

  async handlePriceChangeWebhook(
    cardId: string,
    oldPrice: number,
    newPrice: number
  ): Promise<void> {
    const percentChange = ((newPrice - oldPrice) / oldPrice) * 100;

    // Notify affected users
    const affectedUsers = await this.getAffectedUsers(cardId);
    
    for (const user of affectedUsers) {
      if (user.priceChangeNotifications && 
          Math.abs(percentChange) >= user.priceChangeThreshold) {
        await this.notifyUser(user.id, {
          type: 'price_change',
          cardId,
          oldPrice,
          newPrice,
          percentChange,
        });
      }
    }
  }

  // ===== HELPERS =====

  private createAuthorizedApi(accessToken: string): AxiosInstance {
    return axios.create({
      baseURL: this.api.defaults.baseURL,
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
      timeout: 10000,
    });
  }

  private hasChanged(slabrCard: any, bynxCard: any): boolean {
    return (
      slabrCard.quantity !== bynxCard.quantity ||
      slabrCard.condition !== bynxCard.condition ||
      slabrCard.purchasePrice !== bynxCard.purchasePrice
    );
  }

  private async logSync(
    userId: string,
    action: string,
    status: string,
    metadata: any,
    duration: number
  ): Promise<void> {
    // Log to database
    await db.query(
      `INSERT INTO bynx_sync_log 
       (user_id, action, status, items_processed, duration_ms, timestamp)
       VALUES ($1, $2, $3, $4, $5, NOW())`,
      [
        userId,
        action,
        status,
        metadata.total || 0,
        duration,
      ]
    );
  }
}
```

### 4.2 Scheduler para Atualizações Periódicas

```typescript
// src/jobs/bynx-sync.job.ts

import cron from 'node-cron';
import { BynxIntegrationService } from '../services/bynx-integration.service';

export class BynxSyncJob {
  constructor(private bynx: BynxIntegrationService) {}

  startSchedulers() {
    // Update price cache every 30 minutes
    cron.schedule('*/30 * * * *', async () => {
      await this.updateAllPrices();
    });

    // Sync user collections every hour
    cron.schedule('0 * * * *', async () => {
      await this.syncAllUserCollections();
    });

    // Full database refresh daily at 2 AM
    cron.schedule('0 2 * * *', async () => {
      await this.fullDatabaseRefresh();
    });
  }

  private async updateAllPrices(): Promise<void> {
    const cards = await this.getAllTrackedCards();
    
    for (const card of cards) {
      try {
        await this.bynx.updatePriceCache(card.id, false);
      } catch (error) {
        logger.warn(`Failed to update price for ${card.id}`, error);
      }
    }
  }

  private async syncAllUserCollections(): Promise<void> {
    const users = await this.getUsersWithBynxSync();
    
    for (const user of users) {
      if (!user.autoSync || !user.accessToken) continue;
      
      try {
        await this.bynx.syncUserCollection(user.id, user.accessToken);
      } catch (error) {
        logger.warn(`Failed to sync collection for user ${user.id}`, error);
      }
    }
  }

  private async fullDatabaseRefresh(): Promise<void> {
    logger.info('Starting full bynx database refresh');
    // ... implementation
  }
}
```

---

## 5. FRONTEND INTEGRATION

### 5.1 React Component - Price Display

```typescript
// src/components/CardPrice.tsx

import React, { useState, useEffect } from 'react';
import { useBynxPrice } from '../hooks/useBynxPrice';
import { PriceChart } from './PriceChart';

interface CardPriceProps {
  cardId: string;
  onAddToCollection?: () => void;
}

export const CardPrice: React.FC<CardPriceProps> = ({
  cardId,
  onAddToCollection,
}) => {
  const { price, history, loading, error } = useBynxPrice(cardId);

  if (loading) return <div>Carregando preço...</div>;
  if (error) return <div>Erro ao carregar preço</div>;

  return (
    <div className="card-price">
      <div className="price-display">
        <h3>Preço Médio (bynx.gg)</h3>
        <p className="price">R$ {price?.average.toFixed(2)}</p>
        
        <div className="variants">
          {price?.variants.map((variant) => (
            <div key={variant.type} className="variant">
              <span className="type">{variant.type}</span>
              <span className="value">R$ {variant.price.toFixed(2)}</span>
            </div>
          ))}
        </div>

        {history && <PriceChart data={history} />}

        <button onClick={onAddToCollection} className="btn-add">
          Adicionar à Coleção
        </button>
      </div>
    </div>
  );
};
```

### 5.2 Hook para Fetch de Preços

```typescript
// src/hooks/useBynxPrice.ts

import { useState, useEffect } from 'react';
import { api } from '../services/api';

export const useBynxPrice = (cardId: string) => {
  const [price, setPrice] = useState(null);
  const [history, setHistory] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchPrice = async () => {
      try {
        setLoading(true);
        
        // Get current price
        const priceRes = await api.get(`/bynx/cards/${cardId}`);
        setPrice(priceRes.data.price);

        // Get price history
        const historyRes = await api.get(`/bynx/cards/${cardId}/history`);
        setHistory(historyRes.data.history);

        setError(null);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchPrice();
  }, [cardId]);

  return { price, history, loading, error };
};
```

---

## 6. ERROR HANDLING & RETRY LOGIC

### 6.1 Retry Strategy

```typescript
// src/utils/retry.ts

interface RetryOptions {
  maxAttempts: number;
  initialDelayMs: number;
  maxDelayMs: number;
  backoffMultiplier: number;
}

const DEFAULT_OPTIONS: RetryOptions = {
  maxAttempts: 3,
  initialDelayMs: 100,
  maxDelayMs: 10000,
  backoffMultiplier: 2,
};

export async function retryWithBackoff<T>(
  fn: () => Promise<T>,
  options: Partial<RetryOptions> = {}
): Promise<T> {
  const opts = { ...DEFAULT_OPTIONS, ...options };
  let lastError: Error;
  let delay = opts.initialDelayMs;

  for (let attempt = 1; attempt <= opts.maxAttempts; attempt++) {
    try {
      return await fn();
    } catch (error) {
      lastError = error;
      
      if (attempt < opts.maxAttempts) {
        console.warn(
          `Attempt ${attempt} failed, retrying in ${delay}ms...`,
          error
        );
        await sleep(delay);
        delay = Math.min(delay * opts.backoffMultiplier, opts.maxDelayMs);
      }
    }
  }

  throw lastError!;
}
```

### 6.2 Error Codes Handling

```typescript
// src/utils/bynx-errors.ts

export enum BynxErrorCode {
  RATE_LIMITED = 429,
  UNAUTHORIZED = 401,
  NOT_FOUND = 404,
  SERVICE_ERROR = 500,
  TIMEOUT = 'TIMEOUT',
  NETWORK_ERROR = 'NETWORK_ERROR',
}

export function isBynxError(error: any): boolean {
  return error.source === 'bynx' || error.statusCode in BynxErrorCode;
}

export function shouldRetry(errorCode: BynxErrorCode | number): boolean {
  return [
    BynxErrorCode.RATE_LIMITED,
    BynxErrorCode.SERVICE_ERROR,
    BynxErrorCode.TIMEOUT,
    BynxErrorCode.NETWORK_ERROR,
  ].includes(errorCode as any);
}
```

---

## 7. PERFORMANCE OPTIMIZATION

### 7.1 Caching Strategy

```
┌─────────────────────────────────────────────────┐
│           Cache Layer Architecture              │
├─────────────────────────────────────────────────┤
│ L1: Redis (In-Memory)                          │
│     TTL: 30-60 minutes                         │
│     Data: Card details, prices                 │
│                                                 │
│ L2: Database (PostgreSQL)                      │
│     TTL: Permanent                             │
│     Data: Historical data, user data           │
│                                                 │
│ L3: CDN (Optional)                             │
│     TTL: 1-24 hours                            │
│     Data: Card images, static content          │
└─────────────────────────────────────────────────┘
```

### 7.2 Database Indexing

```sql
-- Critical indexes for performance
CREATE INDEX idx_card_id ON cards(id);
CREATE INDEX idx_bynx_card_id ON card_external_mapping(bynx_card_id);
CREATE INDEX idx_user_bynx_sync ON bynx_sync_metadata(user_id);
CREATE INDEX idx_price_cache_expires ON bynx_price_cache(expires_at);
CREATE INDEX idx_user_collection_user ON user_collections(user_id);
CREATE INDEX idx_marketplace_seller ON marketplace_listings(seller_id);
CREATE INDEX idx_marketplace_status ON marketplace_listings(status);

-- Composite indexes
CREATE INDEX idx_card_variant ON card_variants(card_id, variant_type);
CREATE INDEX idx_sync_log_user_action ON bynx_sync_log(user_id, action);
```

### 7.3 Query Optimization

```typescript
// N+1 Query Prevention
const cards = await db.query(`
  SELECT c.id, c.name, cv.variant_type, cv.current_price_brl
  FROM cards c
  LEFT JOIN card_variants cv ON c.id = cv.card_id
  WHERE c.id = ANY($1)
`, [cardIds]);

// vs (bad - causes N+1)
for (const cardId of cardIds) {
  const card = await db.query('SELECT * FROM cards WHERE id = $1', [cardId]);
  const variants = await db.query('SELECT * FROM card_variants WHERE card_id = $1', [cardId]);
}
```

---

## 8. MONITORAMENTO

### 8.1 Métricas Chave

```typescript
// src/monitoring/metrics.ts

import { prometheus } from 'prom-client';

export const metrics = {
  bynxApiLatency: new prometheus.Histogram({
    name: 'bynx_api_latency_ms',
    help: 'Latency of bynx API calls',
    buckets: [10, 50, 100, 500, 1000, 5000],
    labelNames: ['method', 'endpoint'],
  }),

  bynxApiErrors: new prometheus.Counter({
    name: 'bynx_api_errors_total',
    help: 'Total number of bynx API errors',
    labelNames: ['method', 'endpoint', 'status_code'],
  }),

  cacheMisses: new prometheus.Counter({
    name: 'bynx_cache_misses_total',
    help: 'Total cache misses',
    labelNames: ['cache_type'],
  }),

  syncDuration: new prometheus.Histogram({
    name: 'bynx_sync_duration_ms',
    help: 'Duration of collection sync operations',
    buckets: [100, 500, 1000, 5000, 10000],
  }),

  syncErrors: new prometheus.Counter({
    name: 'bynx_sync_errors_total',
    help: 'Total sync errors',
  }),
};
```

### 8.2 Alertas

```yaml
# prometheus-rules.yaml
groups:
  - name: bynx_integration
    rules:
      - alert: BynxAPIHighErrorRate
        expr: rate(bynx_api_errors_total[5m]) > 0.05
        for: 5m
        annotations:
          summary: "High error rate on bynx API"

      - alert: BynxSyncLatency
        expr: histogram_quantile(0.95, bynx_api_latency_ms) > 5000
        for: 10m
        annotations:
          summary: "bynx API latency is high"

      - alert: BynxSyncFailure
        expr: increase(bynx_sync_errors_total[1h]) > 5
        annotations:
          summary: "Multiple bynx sync failures"
```

---

## 9. ROLLOUT PLAN

### Fase 1: Development (2-3 weeks)

- [ ] Setup development environment
- [ ] Implement core integration service
- [ ] Create mock endpoints for testing
- [ ] Unit tests for all components
- [ ] Integration tests with staging bynx

### Fase 2: Staging (1 week)

- [ ] Deploy to staging environment
- [ ] Load testing
- [ ] Security testing
- [ ] User acceptance testing

### Fase 3: Production Rollout (2 weeks)

```
Week 1:
- 5% traffic → Integration Service
- Monitor metrics
- Fix critical issues

Week 2:
- 25% traffic → Integration Service
- Monitor user feedback
- Performance optimizations

Week 3:
- 50% traffic → Integration Service
- Full monitoring
- Team availability for support

Week 4:
- 100% traffic → Integration Service
- Full feature rollout
- Support continuation
```

---

## 10. DEPENDENCIES

### Backend
```json
{
  "axios": "^1.4.0",
  "redis": "^4.6.0",
  "pg": "^8.11.0",
  "node-cron": "^3.0.0",
  "winston": "^3.8.0",
  "prom-client": "^14.0.0"
}
```

### Frontend
```json
{
  "react": "^18.0.0",
  "axios": "^1.4.0",
  "recharts": "^2.7.0"
}
```

---

**Status:** DRAFT v1.0  
**Próximo Review:** Após aprovação de PM  
**Responsável:** CTO / Tech Lead
