# SLABR Frontend - Guia Completo

## Estrutura de Páginas

```
SLABR 2.0 Frontend
├── home.html          → Landing page / Dashboard inicial
├── app.html           → Aplicação principal (Trading Card Platform)
└── server.py          → Servidor HTTP (não requer Flask)
```

---

## 1️⃣ HOME PAGE (home.html)

**URL:** `http://localhost:5000/`

### Features:
- ✓ Navigation bar com status do sistema
- ✓ Hero section com call-to-action
- ✓ Statistics dashboard (46 endpoints, 18 tabelas, 94% testes)
- ✓ 4 módulos principais com cards informativos
- ✓ Quality Assurance overview
- ✓ Roadmap visual (Fase 1 ✓, Fase 2a ✓, Fase 2b →)
- ✓ Footer com links

### Design:
- Dark theme (Bynx-inspired)
- Color scheme: Gold (#e4c9a0) + Dark Blue
- Responsive (Mobile, Tablet, Desktop)
- Smooth animations
- Status badges em tempo real

### Responsividade:
- ✓ Desktop (1400px+)
- ✓ Tablet (768px - 1399px)
- ✓ Mobile (< 768px)

---

## 2️⃣ APP PAGE (app.html) - MAIN APPLICATION

**URL:** `http://localhost:5000/app`

### Seções Principais:

#### A) HEADER STICKY
- Logo SLABR com emoji 🃏
- Search bar de cartas
- Navigation (Explorar, Portfolio, Marketplace, Tendências)
- Link de conta

#### B) HERO SECTION
- Título: "Descubra Cartas Raras"
- Subtítulo: "A melhor plataforma para colecionadores"
- 2 CTAs: "Começar a Explorar" + "Ver Tendências"

#### C) EXPLORAR CARTAS
- **Filtros por TCG:**
  - Todas, Pokemon, Magic, Yu-Gi-Oh!, One Piece

- **Filtros por Preço:**
  - Menor Preço, Maior Preço, Novos

- **Grid de Cartas (Responsivo):**
  - Desktop: 7 colunas
  - Tablet: 4 colunas
  - Mobile: 2 colunas
  - Aspect ratio: 3:4 (formato real de cartas)

- **Card Item:**
  - Imagem grande (placeholder com emoji)
  - Badge de raridade (top-right)
  - Nome da carta
  - Detalhes (TCG, Set)
  - Preço em R$
  - 2 botões: Comprar + Adicionar à Wishlist

- **Hover Effects:**
  - Border dourada
  - Sombra suave
  - Imagem com zoom (scale 1.05)
  - Elevação visual (-8px)

#### D) MELHORES PREÇOS
- Carousel horizontal com scroll suave
- Cards com preços mais baixos
- Scroll com scrollbar customizado

#### E) TENDÊNCIAS
- Top cards mais buscados
- Grid completo
- Reflex com "Explorar Cartas"

#### F) MEU PORTFOLIO
- **Tabs intercambiáveis:**
  1. **Coleções:**
     - Mostra cartas do usuário
     - Se vazio: "Você não tem cartas"
     - CTA: "Adicionar Cartas"

  2. **Estatísticas:**
     - Total de cartas
     - Valor total do portfolio
     - Maior ganho de valor
     - Cards com borders coloridas

  3. **Alertas de Preço:**
     - Lista de alertas configurados
     - Se vazio: CTA para criar alerta

#### G) MARKETPLACE
- Search e filtros
- Listings de venda/troca
- Grid de cartas para compra
- Informações do vendedor

#### H) MODAL DE DETALHE
- Grid 2 colunas (Desktop) / 1 coluna (Mobile)
- Coluna esquerda: Imagem grande da carta
- Coluna direita: Detalhes
  - Nome
  - TCG e Set
  - Specs: Raridade, Condição, Preço
  - 2 Ações: Comprar + Adicionar ao Portfolio

#### I) FOOTER
- 4 colunas: Sobre, Recursos, Comunidade, Legal
- Copyright
- Email de contato

---

## Design System

### Cores
```css
--dark: #0a0e27           (Background principal)
--dark-2: #141829         (Cards)
--dark-3: #1a1f3a         (Detalhes)
--gold: #e4c9a0           (Destaque/CTA)
--border: #2a3f5f         (Borders)
--text: #a0a9c9           (Texto secundário)
--text-bright: #e0e6ff    (Texto principal)
--success: #51cf66        (Positivo)
--danger: #ff6b6b         (Negativo)
--warning: #ffd93d        (Atenção)
```

### Tipografia
- Font Family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif
- Headings: Bold 700
- Body: Regular 400
- Size scale: 12px, 13px, 14px, 16px, 18px, 24px, 28px, 32px, 48px

### Spacing
- Gaps: 10px, 15px, 20px, 30px, 40px, 60px
- Padding: 8px, 10px, 15px, 20px, 40px

### Borders & Shadows
- Border: 1px solid var(--border)
- Border-radius: 5px, 8px, 10px, 15px, 25px (inputs)
- Box-shadow: 0 15px 40px rgba(228, 201, 160, 0.15)

---

## Componentes Reutilizáveis

### Botões
```html
<!-- Primary -->
<button class="btn btn-primary">Ação Principal</button>

<!-- Secondary -->
<button class="btn btn-secondary">Ação Secundária</button>
```

### Cards
```html
<div class="card-item">
    <div class="card-image placeholder">🔥</div>
    <div class="card-info">
        <div class="card-name">Nome</div>
        <div class="card-details">TCG • Set</div>
        <div class="card-price">R$ 1.500,00</div>
    </div>
</div>
```

### Grid
```css
.cards-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 20px;
}
```

---

## Funcionalidades JavaScript

### 1. Renderização de Cartas
```javascript
renderCards(cards, 'containerId')
```
- Renderiza grid de cartas dinamicamente
- Suporta onclick handlers

### 2. Modal de Detalhe
```javascript
openModal(card)
closeModal()
```
- Mostra detalhe completo da carta
- Fecha ao clicar X ou background

### 3. Filtros
```javascript
filterCards('pokemon')        // Filtra por TCG
sortCards('price-asc')        // Ordena por preço
```

### 4. Ações
```javascript
addToCart(cardId)
addToPortfolio(cardId)
addToWishlist(cardId)
```

### 5. Navegação
```javascript
scrollToSection('explore')
switchTab('portfolio-colecoes')
```

### 6. Search
```javascript
// Input com debounce automático
document.getElementById('searchInput').addEventListener('input', ...)
```

---

## Dados de Exemplo

Inclusos 6 cartas de exemplo:
1. **Charizard** (Pokemon) - R$ 1.500
2. **Pikachu** (Pokemon) - R$ 250
3. **Gyarados** (Pokemon) - R$ 450
4. **Black Lotus** (Magic) - R$ 5.000
5. **Blue-Eyes White Dragon** (Yu-Gi-Oh!) - R$ 800
6. **Luffy SR** (One Piece) - R$ 300

Cada card tem:
- ID único
- Nome
- TCG
- Set
- Preço
- Raridade
- Condição
- Emoji placeholder para imagem

---

## Responsividade

### Desktop (1400px+)
- Header: Logo + Search + Nav
- Cards grid: 7 colunas
- Modal: 2 colunas lado a lado
- Carousel: 4 itens visíveis

### Tablet (768px - 1399px)
- Header: Comprimido
- Cards grid: 4 colunas
- Modal: 2 colunas
- Carousel: 2 itens visíveis

### Mobile (< 768px)
- Header: Logo + Nav (search removido)
- Cards grid: 2 colunas
- Modal: 1 coluna
- Carousel: 1 item visível (scroll)
- Touch-friendly buttons

---

## Acessibilidade

- ✓ Keyboard navigation (Tab, Enter)
- ✓ Color contrast > 4.5:1
- ✓ Semantic HTML
- ✓ ARIA labels onde necessário
- ✓ Touch targets ≥ 44px (mobile)

---

## Performance

- ✓ CSS Grid/Flexbox (layout performático)
- ✓ No dependencies (vanilla JS)
- ✓ Lazy loading ready (imagens não carregam em modal)
- ✓ Smooth scroll behavior
- ✓ Hardware-accelerated animations (transform, opacity)

---

## Integração com API

### Estrutura para integração futura:

```javascript
// Quando API estiver pronta:
async function loadCards() {
    const response = await fetch('/api/marketplace/v2/listings');
    const data = await response.json();
    renderCards(data.listings, 'cardsGrid');
}

// Search
async function searchCards(query) {
    const response = await fetch(`/api/marketplace/v2/listings?card_name=${query}`);
    const data = await response.json();
    renderCards(data.listings, 'cardsGrid');
}

// Filtros
async function filterByTCG(tcgId) {
    const response = await fetch(`/api/marketplace/v2/listings?tcg_id=${tcgId}`);
    const data = await response.json();
    renderCards(data.listings, 'cardsGrid');
}

// Portfolio
async function loadPortfolio() {
    const response = await fetch(`/api/collections/v2/${CURRENT_USER}`);
    const data = await response.json();
    renderCards(data.collections, 'portfolioGrid');
}

// Stats
async function loadStats() {
    const response = await fetch(`/api/collections/v2/stats/${CURRENT_USER}`);
    const data = await response.json();
    updateStatsUI(data);
}
```

---

## URLs Disponíveis

| Página | URL | Descrição |
|--------|-----|-----------|
| Home | http://localhost:5000/ | Landing page |
| App | http://localhost:5000/app | Aplicação principal |
| API Health | http://localhost:5000/api/prices/bynx/health | Status do sistema |

---

## Personalizações Futuras

1. **Imagens Reais:**
   - Integrar com cardknox API
   - Carregar imagens de cards reais
   - Lazy loading de imagens

2. **Dark/Light Mode:**
   - Toggle no header
   - Persistir no localStorage

3. **Animations:**
   - Parallax no hero
   - Card flip ao passar o mouse
   - Loading skeletons

4. **PWA:**
   - Service Worker
   - Offline mode
   - Add to home screen

5. **Real-time:**
   - WebSocket para preços
   - Live marketplace feed
   - Notificações

---

## Estrutura de Arquivos (Frontend)

```
slabr-br/
├── home.html              # Landing page
├── app.html               # Aplicação principal
├── server.py              # Servidor HTTP
├── FRONTEND_GUIDE.md      # Este arquivo
├── CLOUDFLARE_SETUP.md    # Setup público
└── pokemon_catalog.db     # Database (backend)
```

---

*Frontend criado em 2026-06-14*  
*SLABR 2.0 - Trading Card Platform*  
*Pronto para integração com API REST*
