# SLABR 2.0 - Fase 2b: Global Expansion
**Multi-Currency + Regional Marketplace**  
**Estimated Timeline: 4 weeks (2026-06-17 to 2026-07-08)**

---

## OBJETIVOS

1. **Multi-Currency Support** (USD, EUR, JPY, KRW)
2. **Regional Marketplace** (USA, Europe, Asia)
3. **Shipping Integration** (Cálculos por região)
4. **Payment Gateway** (Stripe Global)
5. **Localization** (5+ idiomas)

---

## ARQUITETURA REGIONAL

```
BRASIL (BRL)
├── Marketplace: Bynx.gg integrado
├── Sellers: Colecionadores locais
├── Shipping: Brasil Post, Sedex
└── Payment: Pix, Boleto, Cartao

USA (USD)
├── Marketplace: TCGPlayer.com
├── Sellers: USA-based sellers
├── Shipping: USPS, UPS, FedEx
└── Payment: Credit Card, PayPal

EUROPA (EUR)
├── Marketplace: Cardmarket.com
├── Sellers: EU-based sellers
├── Shipping: DHL, UPS Europe
└── Payment: Kartenzahlung, SEPA

ASIA (JPY)
├── Marketplace: TCGPlayer JP, Yahoo Auctions
├── Sellers: Japan-based sellers
├── Shipping: Japan Post, Yamato
└── Payment: Credit Card, Bank Transfer

KOREA (KRW)
├── Marketplace: Cario.co.kr
├── Sellers: Korea-based sellers
├── Shipping: CJ Logistics, Korea Post
└── Payment: Credit Card, Naver Pay
```

---

## DATABASE SCHEMA - FASE 2b

### 1. Tabela: regions
```sql
CREATE TABLE regions (
    id TEXT PRIMARY KEY,           -- 'br', 'us', 'eu', 'jp', 'kr'
    name TEXT NOT NULL,            -- 'Brazil', 'United States', etc
    currency TEXT NOT NULL,        -- 'BRL', 'USD', 'EUR', 'JPY', 'KRW'
    country_code TEXT,             -- ISO 3166-1 alpha-2
    language TEXT,                 -- 'pt-BR', 'en-US', 'de-DE', 'ja-JP', 'ko-KR'
    timezone TEXT,                 -- 'America/Sao_Paulo', 'America/New_York', etc
    sales_tax_rate DECIMAL(5,2),   -- USA: 7-10%, EU: 19-25%, JP: 10%, KR: 10%
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 2. Tabela: exchange_rates
```sql
CREATE TABLE exchange_rates (
    id TEXT PRIMARY KEY,
    from_currency TEXT NOT NULL,   -- 'USD', 'EUR', 'JPY', 'KRW'
    to_currency TEXT NOT NULL,     -- 'BRL'
    rate DECIMAL(10,4) NOT NULL,   -- 1 USD = 5.40 BRL
    rate_source TEXT,              -- 'bcb', 'fixer.io', 'openexchangerates'
    updated_at TIMESTAMP,
    UNIQUE(from_currency, to_currency)
);
```

### 3. Tabela: shipping_providers
```sql
CREATE TABLE shipping_providers (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,            -- 'USPS', 'UPS', 'FedEx', 'DHL', 'Japan Post'
    region_id TEXT NOT NULL,
    api_key TEXT,                  -- For real-time quote APIs
    base_cost DECIMAL(10,2),       -- Custo base por envio
    per_kg_cost DECIMAL(10,2),     -- Custo por kg adicional
    delivery_days INT,             -- Dias para entrega
    is_active BOOLEAN DEFAULT 1,
    FOREIGN KEY (region_id) REFERENCES regions(id)
);
```

### 4. Tabela: regional_marketplace_listings
```sql
CREATE TABLE regional_marketplace_listings (
    id TEXT PRIMARY KEY,
    seller_id TEXT NOT NULL,
    region_id TEXT NOT NULL,       -- Onde está o vendedor
    tcg_id TEXT NOT NULL,
    card_id TEXT NOT NULL,
    card_name TEXT NOT NULL,
    quantity INT,
    price DECIMAL(10,2),           -- Preço em moeda local
    currency TEXT,                 -- 'USD', 'EUR', 'JPY', 'KRW'
    condition TEXT,
    listing_type TEXT,             -- 'sale', 'trade'
    status TEXT,                   -- 'active', 'sold', 'expired'
    shipping_included BOOLEAN,
    estimated_shipping DECIMAL(10,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    FOREIGN KEY (region_id) REFERENCES regions(id),
    FOREIGN KEY (tcg_id) REFERENCES tcgs(id),
    FOREIGN KEY (card_id) REFERENCES tcg_cards(id)
);
```

### 5. Tabela: pricing_history
```sql
CREATE TABLE pricing_history (
    id TEXT PRIMARY KEY,
    card_id TEXT NOT NULL,
    tcg_id TEXT NOT NULL,
    region_id TEXT NOT NULL,
    price_usd DECIMAL(10,2),       -- Preço normalizado em USD
    price_local DECIMAL(10,2),     -- Preço em moeda local
    currency TEXT,
    market TEXT,                   -- 'bynx', 'tcgplayer', 'cardmarket', 'cario'
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (card_id) REFERENCES tcg_cards(id),
    FOREIGN KEY (tcg_id) REFERENCES tcgs(id),
    FOREIGN KEY (region_id) REFERENCES regions(id)
);
```

### 6. Tabela: user_regional_preferences
```sql
CREATE TABLE user_regional_preferences (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    preferred_region_id TEXT,      -- Região preferida para compra
    language TEXT,                 -- 'pt-BR', 'en-US', etc
    currency TEXT,                 -- Moeda preferida de exibição
    max_shipping_cost DECIMAL(10,2),
    payment_methods JSON,          -- ['credit_card', 'paypal', 'pix']
    notifications_enabled BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (preferred_region_id) REFERENCES regions(id)
);
```

### 7. Tabela: orders_global
```sql
CREATE TABLE orders_global (
    id TEXT PRIMARY KEY,
    buyer_id TEXT NOT NULL,
    seller_id TEXT NOT NULL,
    listing_id TEXT NOT NULL,
    region_from_id TEXT NOT NULL,  -- Região do vendedor
    region_to_id TEXT NOT NULL,    -- Região do comprador
    currency TEXT,
    price_item DECIMAL(10,2),
    shipping_cost DECIMAL(10,2),
    tax_amount DECIMAL(10,2),      -- Sales tax
    total_price DECIMAL(10,2),
    status TEXT,                   -- 'pending', 'paid', 'shipped', 'delivered'
    tracking_number TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    shipped_at TIMESTAMP,
    delivered_at TIMESTAMP,
    FOREIGN KEY (region_from_id) REFERENCES regions(id),
    FOREIGN KEY (region_to_id) REFERENCES regions(id)
);
```

---

## API ENDPOINTS - FASE 2b

### Regional Management
```
GET    /api/regions              - List all regions
GET    /api/regions/<id>         - Get region details
POST   /api/exchange-rates/sync  - Update exchange rates (cron)
```

### Global Marketplace
```
GET    /api/global/listings
   ?region=us
   &tcg_id=pokemon
   &currency=usd
   &sort=price

POST   /api/global/listings      - Create listing (seller)
GET    /api/global/listings/<id> - Get listing details
DELETE /api/global/listings/<id> - Cancel listing

GET    /api/shipping/quote
   ?from_region=br
   &to_region=us
   &weight=0.5kg
   &provider=usps

GET    /api/pricing/comparison
   ?card_id=base1-4
   &tcg_id=pokemon
   (Returns: BRL, USD, EUR, JPY, KRW prices)
```

### Regional Orders
```
POST   /api/orders/create        - Create global order
GET    /api/orders/<id>          - Get order status
POST   /api/orders/<id>/confirm  - Confirm receipt
```

### User Regional Prefs
```
GET    /api/users/<id>/region-prefs
POST   /api/users/<id>/region-prefs
```

---

## INTEGRAÇÕES EXTERNAS

### 1. Exchange Rate API
**Servicos:** Open Exchange Rates, Fixer.io, BCB (Brasil)

```python
async def update_exchange_rates():
    rates = {
        'USD->BRL': 5.40,
        'EUR->BRL': 5.90,
        'JPY->BRL': 0.037,
        'KRW->BRL': 0.0041
    }
    # Update database daily (via cron)
```

### 2. Shipping APIs
**USPS, UPS, FedEx (USA)**
```python
from fedex.services.ship_service import FedexProcessShipmentRequest

def calculate_shipping(origin, dest, weight):
    # Real-time quote from FedEx API
    pass
```

**DHL (Europe)**
```python
def get_dhl_rate(from_zip, to_zip, weight):
    # DHL API integration
    pass
```

**Japan Post (Japan)**
```python
def get_japan_post_rate(destination, weight):
    # Japan Post API
    pass
```

### 3. Payment Gateway
**Stripe Global / Wise (Transferencias internacionais)**

```python
import stripe

stripe.api_key = "sk_live_..."

def create_global_payment(order):
    intent = stripe.PaymentIntent.create(
        amount=order.total_price_cents,
        currency=order.currency.lower(),
        payment_method_types=['card'],
        metadata={
            'order_id': order.id,
            'seller_region': order.region_from_id,
            'buyer_region': order.region_to_id
        }
    )
    return intent
```

---

## IMPLEMENTATION TIMELINE

### Week 1: Setup (Jun 17-23)
- [ ] Create regional database tables
- [ ] Setup exchange rate API integration
- [ ] Regional marketplace schema
- [ ] Deploy to staging

### Week 2: Marketplace (Jun 24-30)
- [ ] API endpoints for global listings
- [ ] Regional filtering/search
- [ ] Pricing normalization (USD baseline)
- [ ] E2E tests

### Week 3: Payments & Shipping (Jul 1-7)
- [ ] Stripe Global integration
- [ ] Shipping provider APIs
- [ ] Order management system
- [ ] Sales tax calculation

### Week 4: Localization (Jul 8-14)
- [ ] i18n (5 languages)
- [ ] Currency formatting
- [ ] Regional UX customization
- [ ] Production launch

---

## PRICING STRATEGY

### USD Baseline
Todos os precos internos armazenados em USD, convertidos para moeda local:
```
BRL price = USD price × BRL_rate
EUR price = USD price × EUR_rate (adjusted for tax)
JPY price = USD price × JPY_rate
KRW price = USD price × KRW_rate
```

### Tax Handling
```
USA:    Item Price + Sales Tax (7-10%) = Total
EU:     Item Price × (1 + VAT 19-25%) = Total
JP:     Item Price × 1.10 = Total
KR:     Item Price × 1.10 = Total
BR:     Item Price + Shipping = Total (sem ISS em venda B2B)
```

---

## PERFORMANCE TARGETS

| Metr ica | Target | Method |
|---------|--------|--------|
| Global search | <500ms | Cached regional indices |
| Price conversion | <50ms | In-memory rates |
| Shipping quote | <2s | Vendor API calls |
| Order creation | <1s | Transactional DB |

---

## NEXT STEPS

1. Review schema com stakeholders
2. Setup staging environment
3. Begin Week 1 implementation
4. Daily standup on progress
5. Go-live planning

---

*Especificação técnica para SLABR 2.0 Fase 2b*
*Global Expansion com suporte a 5 regioes e 5 moedas*
