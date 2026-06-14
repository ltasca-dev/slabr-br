# 🚀 SLABR 2.0 - PLANO COMPLETO DE IMPLEMENTAÇÃO

**Data:** 14 de junho de 2026  
**Objetivo:** Clone completo Bynx + Expansão Multi-TCG Global  
**Timeline:** 11 meses  
**Investimento Total:** R$ 1,76M  
**ROI Esperado:** 600-1000% em 24 meses

---

## 📊 VISÃO GERAL

```
SLABR 2.0 = Infraestrutura Completa de Trading Cards Brasil + Global

MODELO A (Semanas 1-4):     Preços Bynx + Integração Leve
MODELO B (Semanas 5-20):    Portfolio Manager + Marketplace Unificado  
MODELO C (Semanas 21+):     Multi-TCG + API Pública + Expansão Global

TOTAL: 11 meses, 3 fases, $1.76M investimento
```

---

## 📈 ROADMAP EXECUTIVO (11 MESES)

### **FASE 0: MVP LEVE (Semanas 1-4) - INICIANDO AGORA**
**Status:** ✅ 90% pronto
**Orçamento:** R$ 42K
**Equipe:** 3 devs + 1 DevOps

#### Entregáveis:
- ✅ Web scraper Bynx (preços)
- ✅ Cache em-memory + TTL
- ✅ Endpoint `/api/prices/bynx/<card_id>`
- ✅ Frontend integrado (mostra preços)
- ✅ Link de referral para Bynx.gg
- ✅ Deploy em staging

#### KPIs:
- Taxa de sucesso scraper: > 80%
- Tempo resposta: < 500ms
- Uptime: > 99%

#### Próximos passos:
1. Deploy para produção hoje
2. Monitorar por 1 semana
3. Feedback de usuários
4. Go/No-Go para Fase 1

---

### **FASE 1: INTEGRAÇÃO PROFUNDA (Semanas 5-20)**
**Orçamento:** R$ 375K
**Equipe:** 6 devs + 1 PM + 1 QA + 1 DevOps
**Timeline:** 16 semanas

#### 1.1 - PORTFOLIO MANAGER (Semanas 5-8)
Permitir usuários importar e gerenciar suas coleções como no Bynx

**Features:**
- [ ] Sistema de autenticação avançado (SSO com Bynx)
- [ ] Importação de coleções (CSV, upload manual, foto)
- [ ] Dashboard de portfolio (valor total, gráficos, tendências)
- [ ] Rastreamento de mudanças de preço
- [ ] Alertas de preço (notificações)
- [ ] Exportar relatórios PDF

**Banco de dados:**
```sql
-- Novas tabelas
CREATE TABLE user_collections (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  card_id VARCHAR,
  quantity INT,
  condition VARCHAR,
  purchase_price DECIMAL,
  current_price DECIMAL,
  purchase_date DATE,
  created_at TIMESTAMP,
  updated_at TIMESTAMP
);

CREATE TABLE portfolio_stats (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  total_value DECIMAL,
  total_cards INT,
  biggest_gains JSON,
  biggest_losses JSON,
  calculated_at TIMESTAMP
);

CREATE TABLE price_alerts (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  card_id VARCHAR,
  threshold_price DECIMAL,
  alert_type VARCHAR, -- 'up', 'down', 'exact'
  is_active BOOLEAN,
  created_at TIMESTAMP
);
```

**API Endpoints:**
```
POST   /api/collections              - Criar coleção
GET    /api/collections/{id}         - Obter coleção
PUT    /api/collections/{id}         - Atualizar
DELETE /api/collections/{id}         - Deletar
POST   /api/collections/{id}/import  - Importar CSV/foto
GET    /api/collections/{id}/stats   - Dashboard stats
GET    /api/collections/{id}/export  - Exportar PDF
POST   /api/alerts                   - Criar alerta de preço
GET    /api/alerts                   - Listar alertas
```

**Frontend:**
- Nova página `/collections` com dashboard
- Gráfico de valor ao longo do tempo
- Cards com preço atual vs. custo
- Botão "adicionar à coleção"
- Filtros por condição, edição, valor

---

#### 1.2 - MARKETPLACE INTEGRADO (Semanas 9-14)
Permitir venda/compra de cartas direto no SLABR com escrow

**Features:**
- [ ] Sistema de anúncios (venda/troca)
- [ ] Matching automático de ofertas
- [ ] Escrow seguro (terceiro confiável)
- [ ] Sistema de pagamento (PIX, cartão, boleto)
- [ ] Histórico de transações
- [ ] Rating/Reviews

**Banco de dados:**
```sql
CREATE TABLE listings (
  id UUID PRIMARY KEY,
  seller_id UUID REFERENCES users(id),
  card_id VARCHAR,
  quantity INT,
  price DECIMAL,
  condition VARCHAR,
  listing_type VARCHAR, -- 'sale', 'trade'
  status VARCHAR, -- 'active', 'sold', 'expired'
  created_at TIMESTAMP,
  expires_at TIMESTAMP
);

CREATE TABLE trades (
  id UUID PRIMARY KEY,
  listing_id UUID REFERENCES listings(id),
  buyer_id UUID REFERENCES users(id),
  seller_id UUID REFERENCES users(id),
  amount DECIMAL,
  status VARCHAR, -- 'pending', 'escrow', 'shipped', 'completed'
  escrow_id VARCHAR,
  created_at TIMESTAMP,
  completed_at TIMESTAMP
);

CREATE TABLE reviews (
  id UUID PRIMARY KEY,
  trade_id UUID REFERENCES trades(id),
  reviewer_id UUID REFERENCES users(id),
  rating INT, -- 1-5
  comment TEXT,
  created_at TIMESTAMP
);
```

**API Endpoints:**
```
POST   /api/listings                 - Criar anúncio
GET    /api/listings                 - Listar anúncios
GET    /api/listings/{id}            - Detalhes anúncio
PUT    /api/listings/{id}            - Editar anúncio
DELETE /api/listings/{id}            - Remover anúncio
POST   /api/listings/{id}/buy        - Comprar
POST   /api/trades/{id}/confirm      - Confirmar recebimento
POST   /api/reviews                  - Deixar review
GET    /api/marketplace/trending     - Trending agora
GET    /api/marketplace/deals        - Melhores ofertas
```

**Frontend:**
- Nova página `/marketplace`
- Filtros avançados (preço, condição, edição)
- Carrinho de compras
- Checkout com pagamento
- Página do vendedor (ratings, histórico)

---

#### 1.3 - SINCRONIZAÇÃO COM BYNX (Semanas 15-20)
Conectar contas SLABR com Bynx para sincronizar dados

**Features:**
- [ ] OAuth2 com Bynx.gg
- [ ] Sincronizar coleções bidirecionais
- [ ] Notificações cruzadas
- [ ] Unified portfolio view
- [ ] Cross-sell (vender no Bynx também)

**Fluxo:**
```
1. Usuário clica "Conectar Bynx"
2. Redireciona para login Bynx (OAuth)
3. Autoriza acesso à coleção
4. Coleção sincroniza em tempo real
5. Mudanças em SLABR → refletem em Bynx
6. Vendas em SLABR podem ser publicadas em Bynx
```

**API (para Bynx Integration):**
```
POST   /api/integrations/bynx/connect  - OAuth callback
GET    /api/integrations/bynx/status   - Status sincronização
POST   /api/integrations/bynx/sync     - Forçar sincronização
GET    /api/integrations/bynx/diff     - Ver diferenças
```

---

#### 1.4 - TESTES & OTIMIZAÇÃO (Semanas 20)
- [ ] Testes E2E (100 cenários)
- [ ] Load testing (1000 usuários simultâneos)
- [ ] Security audit (OWASP top 10)
- [ ] Performance optimization
- [ ] Beta com 500 usuários
- [ ] Go/No-Go para Fase 2

---

### **FASE 2: EXPANSÃO MULTI-TCG + GLOBAL (Semanas 21+)**
**Orçamento:** R$ 1.34M
**Equipe:** 12+ devs + 2 PMs + 2 QAs + 2 DevOps
**Timeline:** 24+ semanas (contínua)

#### 2.1 - SUPORTE MULTI-TCG (Semanas 21-28)
Expandir de Pokémon para Magic, Yu-Gi-Oh, One Piece

**Novas bases de dados:**
```
- Magic: The Gathering (15K cartas)
- Yu-Gi-Oh! (10K cartas)
- One Piece TCG (2K cartas - crescendo)
- Digimon (1K cartas)
- Lorcana (1K cartas)
```

**Features:**
- [ ] Parser automático de cartas por TCG
- [ ] Preços por mercado (Bynx, Cardmarket, TCGPlayer)
- [ ] Marketplace unificado (filtra por TCG)
- [ ] Portfolio multi-TCG
- [ ] Analytics por TCG

**Banco de dados:**
```sql
ALTER TABLE cards ADD COLUMN tcg VARCHAR; -- 'pokemon', 'magic', 'yugioh', etc
ALTER TABLE listings ADD COLUMN tcg VARCHAR;
ALTER TABLE user_collections ADD COLUMN tcg VARCHAR;

-- Nova tabela
CREATE TABLE tcg_configs (
  id UUID PRIMARY KEY,
  tcg_name VARCHAR UNIQUE,
  data_source VARCHAR, -- 'bynx', 'cardmarket', 'tcgplayer'
  api_endpoint VARCHAR,
  last_sync TIMESTAMP
);
```

---

#### 2.2 - EXPANSÃO GLOBAL (Semanas 29-36)
Lançar SLABR em USA, Europa, Ásia

**Regiões:**
- 🇺🇸 **USA** (mercado maior)
- 🇪🇺 **Europa** (Alemanha, UK, França)
- 🇯🇵 **Ásia** (Japão, Singapura, Hong Kong)

**Features:**
- [ ] Multi-currency (USD, EUR, JPY, etc)
- [ ] Localização (idiomas)
- [ ] Marketplace regional (comprador USA ↔ vendedor USA)
- [ ] Shipping integrado (labels, tracking)
- [ ] Compliance local (impostos, regulações)

**Banco de dados:**
```sql
ALTER TABLE users ADD COLUMN country VARCHAR;
ALTER TABLE listings ADD COLUMN region VARCHAR;

CREATE TABLE shipping_partners (
  id UUID PRIMARY KEY,
  country VARCHAR,
  carrier VARCHAR, -- 'DHL', 'UPS', 'Correios'
  api_key VARCHAR,
  cost_per_kg DECIMAL
);
```

---

#### 2.3 - API PÚBLICA & B2B (Semanas 37-40)
Monetizar dados via API pública

**Endpoints B2B:**
```
GET /api/v1/cards/search              - Buscar cartas (com preços)
GET /api/v1/cards/{id}                - Detalhes carta
GET /api/v1/prices/history/{card_id}  - Histórico de preços
GET /api/v1/market/trends             - Tendências de mercado
GET /api/v1/analytics/popular         - Cartas populares
POST /api/v1/bulk-lookup              - Buscar 100+ cartas
```

**Modelos de receita:**
- Free tier: 100 req/dia
- Pro tier: 10K req/dia (R$ 99/mês)
- Enterprise: ilimitado (custom pricing)

---

#### 2.4 - FEATURES AVANÇADAS (Semanas 41+)
Recursos diferenciados que consolidam SLABR como líder

**Features:**
- [ ] **IA Scan de Cartas** - Foto → reconhecimento automático
- [ ] **Investment Analytics** - ROI, trending, previsões
- [ ] **Mobile App Nativa** - iOS/Android
- [ ] **Webhooks** - Integração com sistemas externos
- [ ] **Community** - Fóruns, streams, trade shows
- [ ] **Grading Partnership** - PSA, BGS, CGC integrado
- [ ] **Vault Físico** - Guarda de cartas

---

## 💰 ORÇAMENTO DETALHADO

### Fase 0 (4 semanas) - R$ 42K
```
Backend (1 dev, 4 sem):         R$ 12K
Frontend (1 dev, 4 sem):        R$ 12K
DevOps (0.5 dev, 4 sem):        R$ 6K
QA/Testes (0.5 dev, 4 sem):     R$ 6K
Infraestrutura (AWS, etc):      R$ 3K
Contingência 10%:               R$ 3K
───────────────────────────────
TOTAL:                          R$ 42K
```

### Fase 1 (16 semanas) - R$ 375K
```
Backend (3 devs, 16 sem):       R$ 192K
Frontend (2 devs, 16 sem):      R$ 128K
DevOps (0.5 dev, 16 sem):       R$ 24K
QA/Testes (1 dev, 16 sem):      R$ 24K
PM/Design (0.5 person, 16 sem): R$ 16K
Infraestrutura:                 R$ 8K
Contingência 10%:               R$ 37.7K
───────────────────────────────
TOTAL:                          R$ 375K
```

### Fase 2 (24+ semanas) - R$ 1.34M
```
Backend (6 devs, 24 sem):       R$ 576K
Frontend (3 devs, 24 sem):      R$ 288K
Mobile (2 devs, 24 sem):        R$ 192K
DevOps (1 dev, 24 sem):         R$ 96K
QA/Testes (2 devs, 24 sem):     R$ 96K
PM/Design (1 person, 24 sem):   R$ 48K
Infraestrutura:                 R$ 48K
Contingência 10%:               R$ 134K
───────────────────────────────
TOTAL:                          R$ 1.34M
```

### **INVESTIMENTO TOTAL: R$ 1.757M** (11 meses)

---

## 📊 PROJEÇÃO DE RECEITA

### Conservadora (Brasil Only, 30% Pokémon penetration)
```
MÊS 4 (Após Fase 1):
├─ Graduações: 500/dia × R$ 50 = R$ 750K/mês
├─ Marketplace: 1000 vendas/dia × R$ 150 × 8% = R$ 360K/mês
├─ Assinatura Premium: 20K × R$ 10 = R$ 200K/mês
├─ Vault/Custódia: 10K × R$ 15 = R$ 150K/mês
└─ Partnerships: R$ 100K/mês
= R$ 1.56M/mês (R$ 18.7M/ano)

PAYBACK: 3.5 meses (Fase 1 investe R$ 375K, ganha R$ 1.56M em mês 4)
```

### Agressiva (Multi-TCG + Global, Semana 40+)
```
MÊS 9 (Após Fase 2, multi-TCG global):
├─ Brasil Pokémon: R$ 750K/mês
├─ Brasil Multi-TCG: R$ 500K/mês
├─ USA Marketplace: R$ 1.5M/mês (5x Brasil)
├─ Europa: R$ 900K/mês (3x Brasil)
├─ Ásia: R$ 600K/mês (2x Brasil)
├─ API/B2B: R$ 300K/mês
└─ Mobile/Premium: R$ 500K/mês
= R$ 5.05M/mês (R$ 60.6M/ano)

PAYBACK: 2.5 meses (do total investido R$ 1.757M)
```

---

## 🎯 KPIs & MÉTRICAS

### Fase 0
| Métrica | Target | Como Medir |
|---------|--------|-----------|
| Taxa scraper | > 80% | Logs / requests |
| Response time | < 500ms | APM (New Relic) |
| Uptime | > 99% | Monitoring |
| Usuários testando | > 1000 | Analytics |
| NPS | > 20 | Survey |

### Fase 1
| Métrica | Target | Como Medir |
|---------|--------|-----------|
| Usuários ativos | > 50K | DAU/MAU |
| Coleções importadas | > 10K | DB count |
| Marketplace GMV | > R$ 500K/mês | Dashboard |
| CTR marketplace | > 2% | Analytics |
| Retention 30d | > 40% | Cohort |
| NPS | > 40 | Survey |

### Fase 2
| Métrica | Target | Como Medir |
|---------|--------|-----------|
| Usuários globais | > 150K | DAU/MAU |
| GMV mensal | > R$ 5M | Dashboard |
| Países ativos | > 15 | Geo data |
| Multi-TCG penetration | > 30% | Analytics |
| API calls/dia | > 1M | API logs |
| Revenue/user | > R$ 150/mês | Cohort |

---

## 🚀 PLANO DE EXECUÇÃO (próximos 30 dias)

### Semana 1 (14-20 junho)
- [ ] Deploy Fase 0 em produção (HOJE)
- [ ] Monitorar scraper Bynx
- [ ] Coletar feedback usuários
- [ ] Briefing com time Bynx (contato)
- [ ] Planejamento Sprint 1 Fase 1

### Semana 2 (21-27 junho)
- [ ] Backend Fase 1: scaffolding + modelos
- [ ] Frontend Fase 1: layout dashboard
- [ ] Infrastructure as Code (Terraform)
- [ ] Database migrations
- [ ] Sprint 1 review

### Semana 3 (28-4 julho)
- [ ] Portfolio manager v0.1
- [ ] Importação CSV
- [ ] Dashboard básico
- [ ] Price tracking
- [ ] Beta com 100 usuários

### Semana 4 (5-11 julho)
- [ ] Testes portfolio manager
- [ ] Bug fixes
- [ ] Otimizações performance
- [ ] Go/No-Go decision
- [ ] Planejamento marketplace

---

## 🔐 RISCOS & MITIGAÇÕES

| Risco | Probabilidade | Impacto | Mitigação |
|-------|--------------|--------|-----------|
| Bynx bloqueia scraper | Alta | Médio | Negociar API/partnership |
| Atraso Fase 1 | Médio | Médio | Hiring paralelo, MVP scope |
| Competição (Cardmarket Brasil) | Médio | Alto | Speed to market, features únicas |
| Mudanças regulação (loot boxes) | Baixo | Alto | Compliance desde início |
| Churn de usuários Bynx | Médio | Médio | Value prop clara, zero downtime |
| Segurança/fraude | Médio | Alto | Audit, 2FA, anti-fraud layer |

---

## ✅ PRÓXIMOS PASSOS

### HOJE (14 junho)
1. ✅ Aprovar este plano
2. ✅ Deploy Fase 0 → produção
3. ✅ Designar PM para Fase 1
4. ✅ Iniciar hiring (3 devs)

### SEMANA 1
1. Monitorar Fase 0
2. Coletar feedback
3. Contato oficial com Bynx
4. Kick-off Fase 1
5. Sprint planning

### SEMANA 4
1. Go/No-Go decision
2. Beta Fase 1 com 500 usuários
3. Roadmap Fase 2

---

**Documento preparado em:** 14 de junho de 2026  
**Status:** Pronto para aprovação e execução  
**Próxima revisão:** Após semana 4 (Go/No-Go decision)

