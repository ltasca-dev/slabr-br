# Análise Profunda do Site Bynx.gg

**Data da Análise:** 14 de Junho de 2026  
**Site Analisado:** https://bynx.gg/  
**Foco:** Plataforma brasileira de gerenciamento de coleções Pokémon TCG

---

## RESUMO EXECUTIVO

**O que é o Bynx.gg:**

Bynx é uma plataforma web/mobile brasileira (100% focada no Brasil) que permite colecionadores de Pokémon Trading Card Game (TCG) gerenciar, valorizar e comercializar suas coleções. A proposta de valor central é **resolver a incerteza sobre preços reais de cartas** através de um catálogo atualizado diariamente com preços em BRL, permitindo que colecionadores saibam exatamente quanto vale sua coleção.

**Público-alvo:**
- Colecionadores casuais (conhecem poucos preços)
- Investidores/Colecionadores sérios (ROI tracking)
- Colecionadores competitivos (tracking de performance)
- Lojistas físicos e online (precificação e análise de estoque)
- Veteranos que buscam contexto de mercado

**Diferencial principal:** Combinação de IA para scanning, dashboard financeiro inteligente, marketplace descentralizado (via WhatsApp) e guia de lojas brasileiras.

---

## 1. ARQUITETURA GERAL DO SITE

### 1.1 Estrutura de Navegação

```
Homepage (/)
├── Como funciona (/como-funciona) - 404 [PROTEGIDA?]
├── Planos (/planos) - 404 [PROTEGIDA?]
├── Guia de Lojas (/guia-de-lojas) - 404 [PROTEGIDA?]
├── Colecionadores (/colecionadores) - ACESSÍVEL (perfis públicos)
├── Pokédex (/pokedex) - ACESSÍVEL (com filtros, carregamento dinâmico)
├── Scan IA (/scan-ia) - ACESSÍVEL (descrição e CTA)
├── Separadores (/separadores) - ACESSÍVEL (com filtros por geração)
├── Ranking (/ranking) - ACESSÍVEL (ranking mensal de indicações)
├── Para lojistas (/para-lojistas) - ACESSÍVEL (planos e benefícios)
│
├── [AUTENTICADO - 404]
│   ├── /login
│   ├── /signup
│   ├── /conta
│   ├── /minha-colecao
│   ├── /dashboard
│   ├── /marketplace
│   ├── /negociacoes
│   └── /dashboard-financeiro
│
└── Footer
    ├── /faq - ACESSÍVEL
    ├── /privacidade - ACESSÍVEL
    ├── /termos - ACESSÍVEL
    └── Fale conosco (formulário)
```

### 1.2 Padrão de Roteamento
- **URLs públicas:** Informativas, SEO-otimizadas, carregamento via JavaScript
- **URLs autenticadas:** Retornam 404 (spa-based, protegidas com redirecionamento)
- **Dinâmicas:** `/perfil/[username]` para perfis de colecionadores

---

## 2. FUNCIONALIDADES PRINCIPAIS POR CATEGORIA

### 2.1 AUTENTICAÇÃO E CONTA

**Status:** Protegida (endpoints retornam 404, sugerindo redirecionamento via SPA)

**Campos de Cadastro (deduzido de política de privacidade):**
- Nome completo
- Email
- CPF
- Data de nascimento
- Cidade
- WhatsApp (opcional)

**Recursos de Segurança:**
- Criptografia bcrypt para senhas
- HTTPS/TLS obrigatório
- Não armazena dados de cartão (Stripe)
- Controle de acesso baseado em função (RBAC)
- Monitoramento de acessos

**Recuperação de Senha:**
- Mencionada em FAQ como suportada
- Resposta em até 48h úteis via suporte@bynx.gg

**Autenticação:**
- Email/Senha (padrão)
- Sem OAuth social explicitamente mencionado
- Foco em privacidade (não usa dados de terceiros)

---

### 2.2 CATÁLOGO/POKÉDEX

**Tamanho do Catálogo:**
- 22.000+ cartas catalogadas
- 240+ sets/coleções cobertos
- Atualização diária de preços

**Busca e Filtros:**
- **Por geração:** Gen I até Gen IX (Kanto, Johto, Hoenn, Sinnoh, Unova, Kalos, Alola, Galar, Paldea)
- **Por tipo:** Fire, Water, Grass, Lightning, Psychic, Fighting, Darkness, Metal, Dragon, Colorless, Fairy
- **Por raridade:** Implied (não detalhado)
- **Autocomplete inteligente:** "Em 2 cliques tá na coleção"
- **Busca por nome:** Funcionalidade principal

**Informações por Carta:**
- Nome (português)
- Número
- Set/Coleção
- Imagem oficial (API Pokemon TCG)
- Variantes disponíveis

**Variantes Suportadas:**
- Normal
- Holo (Holofoil)
- Reverse Holo
- Foil/Full Art
- Promo
- Secret Rare (mencionado em exemplo "Charizard Rare Secret")
- Special Illustration (mencionado em exemplos)

**Preços por Variante:**
- Mínimo (minimum market price)
- Médio (average price)
- Máximo (maximum market price)
- Em BRL, atualizados diariamente
- Fontes: "Marketplaces brasileiros"

**Histórico de Preços:**
- Gráfico temporal de últimos 6 meses
- Visualização de tendências
- Exemplo: "Charizard ex — Performance +13,6%"

---

### 2.3 SCAN IA (FEATURE DIFERENCIAL)

**Como Funciona:**
1. Usuário aponta câmera do celular para 1-8 cartas
2. Sistema Claude Opus 4.5 (Anthropic) processa imagem
3. IA identifica: nome, número, set, raridade, idioma
4. Cruza com banco de 22.861 cartas Bynx
5. Exibe variante e preço médio em reais
6. Usuário confirma e adiciona à coleção

**Performance:**
- **Acurácia:** 97-99% (conforme exemplos demonstrados)
- **Tempo:** 3-6 segundos por foto (até 8 segundos máximo)
- **Detecção:** Até 8 cartas por imagem

**Requisitos:**
- Conexão de internet (funciona em 4G)
- Câmera traseira ou fotos da galeria
- **Tolerante:** Funciona em luz baixa e ângulos diagonais

**Limitações:**
- Feature Pro (requer assinatura)
- Provavelmente com créditos/limite mensal (não especificado)

**Integração:**
- Automaticamente atualiza coleção, patrimônio e marketplace

---

### 2.4 MARKETPLACE (DESCENTRALIZADO)

**Modelo:**
- Peer-to-peer (P2P)
- Contato via WhatsApp (não intermediado)
- Bynx **não** processa pagamentos nem intermedia transações
- Moderação ativa contra fraudes e preços abusivos

**Funcionalidades de Listing:**
- **Botão:** "+ Anunciar carta"
- **Campos:** Variante, preço, localização/estado, foto
- **Status:** Disponível, Reservado, Enviado, Concluído

**Filtros de Busca:**
- "Mais recentes primeiro"
- "Menor preço primeiro"
- "Maior preço primeiro"
- "Maior desconto vs mercado" (comparação com preço Bynx)
- "+ Filtros" (avançados não detalhados)

**Preços de Referência:**
- Exibe preço médio Bynx como comparação
- Vendedor define preço livremente

**Limites por Plano:**
- **Grátis:** 3 anúncios ativos
- **Pro Mensal/Anual:** Anúncios ilimitados

**Avaliação e Reputação:**
- Ambas as partes deixam avaliações públicas após conclusão
- Sistema de reputação não detalhado

**Segurança:**
- Moderação remove anúncios falsos, fraudulentos ou com "preços abusivos"
- Responsabilidade: "Transações entre usuários — Bynx oferece no estado em que se encontra"

---

### 2.5 PERFIS DE COLECIONADORES / COMUNIDADE

**Perfis Públicos:**
- URL: `/perfil/[username]`
- Customizável para compartilhamento em redes sociais

**Informações Exibidas:**
- Nome do colecionador
- Localização (cidade/estado)
- Quantidade total de cartas
- Cards principais (imagens destacadas)
- Tags/Categorias (ex: "Charizard fan", "Eeveelutions", "Vintage 1999")
- Badge de Status: "PRO" ou "verificado"
- Patrimônio total com histórico de variação

**Features Sociais (Detectadas):**
- Link WhatsApp direto no perfil (para negociações)
- Compatilhamento em redes sociais
- Perfil público/indexável

**Features NÃO Encontradas:**
- Sistema de seguir/seguidores
- Chat privado integrado
- Comentários públicos no perfil
- Comunidade organizada (fórums, grupos)
- Discord ou Telegram integrado

---

### 2.6 RANKING / GAMIFICAÇÃO

**Tipo de Ranking:**
- **Ranking de Indicações Mensal**
- Premia os colecionadores que mais indicam amigos

**Sistema de Premiação:**
- 🥇 1º lugar: R$ 200
- 🥈 2º lugar: R$ 100
- 🥉 3º lugar: R$ 50
- Distribuição mensal

**Métrica:**
- Quantidade de amigos/usuários indicados
- Provavelmente com código de referência

**Observações:**
- Página exibe "Carregando ranking..." (conteúdo dinâmico)
- Sem filtros de período ou busca avançada visível

**Gamificação Adicional:**
- Badge "PRO" no perfil
- Barra de progresso por set (mencionada em testimonial: "87%")
- Titles/Tags de colecionador

---

### 2.7 DASHBOARD FINANCEIRO

**Informações Principais:**
- **Patrimônio Total:** Soma do valor de todas as cartas
- **Valor Mínimo, Médio, Máximo:** Range de valorização
- **Performance:** Percentual de ganho/perda (ex: "+13,6%")
- **Histórico Mensal:** Acompanhamento de variação

**Exemplo Demonstrado:**
- Mínimo: R$ 29.009,50
- Médio: R$ 29.565,36
- Máximo: R$ 52.879,20

**Funcionalidades:**
- Cálculo automático de ROI por carta
- Gráficos de performance
- Exportação em CSV (para plano Grátis)
- Análise temporal (últimos 6 meses)

---

### 2.8 GUIA DE LOJAS

**O que é:**
- Diretório de lojas físicas e online brasileiras de TCG
- Filtrado por cidade, especialidade, tipo

**Para Colecionadores:**
- Geolocalização: "Encontre lojas físicas de TCG perto de você"
- Informações: Endereço, contato, especialidades, redes sociais
- Objetivo: "Colecionador que tá com grana na mão acha você"

**Para Lojistas:**
- Plano Básico (Grátis): Listagem simples, aprovação 48h
- Plano Pro (R$ 39/mês ou R$ 390/ano): Analytics básico, WhatsApp, 14 dias grátis
- Plano Premium (R$ 89/mês ou R$ 890/ano): Analytics completo, eventos/torneios ilimitados, suporte prioritário, 14 dias grátis

**Analytics de Lojista (Premium):**
- Visualizações da loja
- Cliques em WhatsApp
- Análise por dias da semana

---

### 2.9 SEPARADORES

**Produto Físico:**
- Tamanho exato: 6,3 × 8,8 cm (padrão TCG Pokémon)
- Designs temáticos por geração (Gen I-IX)
- Cada geração com tema específico (Kanto, Johto, Hoenn, etc)

**Funcionalidades:**
- Filtro por geração
- Opção de imprimir/PDF
- Integração com coleção (para organização)

**Status:** Produto complementar, não totalmente detalhado na homepage

---

## 3. ANÁLISE DE DESIGN E UX

### 3.1 Paleta de Cores

**Cores Primárias:**
- **Roxo/Violeta:** Usado em CTAs destacados, badges "PRO"
- **Branco/Cinza claro:** Fundos principais
- **Preto/Cinza escuro:** Texto e contraste

**Cores Secundárias e Temáticas:**
- Vermelho (🔥) - Fire-type
- Amarelo (⚡) - Electric-type
- Azul (🌙) - Water-type
- Roxo (🌀) - Psychic-type
- Outras cores de tipo para visual dos cards

**Uso de Emojis:**
- 🤝 Partnership
- 📦 Produtos
- 💬 Chat/Communication
- 📋 Dados/Documentos
- ⭐ Premium/Destaque
- 🔥🌟💧 Elementos temáticos

---

### 3.2 Tipografia

**Informações Limitadas:**
- Hierarquia clara (h1, h2, h3 semânticos)
- Títulos grandes e destacados
- Corpo legível em tamanho apropriado
- **Fonte específica não detectada** (presumivelmente sans-serif moderno)

---

### 3.3 Padrões de Componentes

- **Cards:** Imagem + preço (estilo marketplace/galeria)
- **Tabs/Abas:** Interativas para planos, FAQ
- **Badges:** Status Pro, Verificado
- **Ícones:** Emojis + SVG customizado (logo Bynx)
- **Tabelas:** Comparação de planos
- **Gráficos:** Histórico de preços (presumivelmente charts.js ou similar)
- **Modais/Dropdowns:** "+ Filtros" e expansíveis de FAQ

---

### 3.4 Layout e Responsiveness

**Desktop:**
- Grid layout para catálogo de cartas
- Sidebar/Navegação horizontal
- Dashboard com múltiplas colunas

**Mobile (Inferido):**
- Empilhamento vertical
- Câmera como feature móvel nativa (Scan IA)
- Botões grandes e touchable
- Navegação colapsável

**Indicadores de PWA/Mobile-First:**
- Acesso a câmera do dispositivo
- Funcionalidade Scan IA otimizada para mobile
- Integração com WhatsApp (mobile-native)

---

### 3.5 Padrão de Design

**Classificação:** Custom Design com inspirações FinTech + Marketplace

- Dashboard financeiro similar a apps de investimento (Nubank, Rico, etc)
- Marketplace estilo OLX/Facebook Marketplace
- Gamificação simples (badges, rankings)
- Foco em clarity e usabilidade (problema-solução clara)

---

## 4. STACK TÉCNICO DETECTADO

### 4.1 Backend

**Serviços/Providers Mencionados:**
- **Supabase Cloud:** Storage de imagens (`hvkcwfcvizrvhkerupfc.supabase.co`)
- **Stripe:** Processamento de pagamentos (PCI-compliant, sem armazenar cartões)
- **Resend:** Provavelmente email delivery
- **Anthropic Claude Opus 4.5:** IA para Scan
- **Vercel:** Hosting/deployment (mencionado na política de privacidade)
- **Google Analytics 4:** Analytics via Tag Manager

**APIs Externas:**
- **Pokemon TCG Official API:** Imagens e metadados das cartas (`images.pokemontcg.io`)
- **Google Tag Manager:** Analytics

**Autenticação:**
- Criptografia bcrypt
- HTTPS/TLS obrigatório
- Sessões/JWTs (presumido)

### 4.2 Frontend

**Framework:** Não determinado pelo HTML extraído
- **Candidatos:** Next.js, React, Vue (arquitetura modular observada)
- **Indicadores:** SPA behavior (rotas protegidas retornam 404, redirecionamento client-side)

**Otimizações:**
- CDN Supabase para imagens (compressão)
- Lazy loading presumido para galeriais longas
- Responsive design (mobile-first indicators)

### 4.3 Análise/Dados

- **Analytics:** Google Analytics 4 (via GTM)
- **Cookies:** 
  - Essenciais (não opcionais)
  - Analíticos (opcionais, Google Analytics 4)
  - Sem cookies publicitários

**Política explícita:** "O Bynx não utiliza cookies publicitários"

---

## 5. ESTRUTURA DE PREÇOS

### 5.1 Plano Grátis

**Valor:** R$ 0/mês

**Features:**
- 7 dias Pro grátis no cadastro (sem cartão de crédito)
- Cartas ilimitadas **para sempre**
- Perfil público
- 3 anúncios no marketplace
- Pokédex completa
- Dashboard financeiro
- Exportar dados em CSV
- Compartilhamento de perfil

**Sem:**
- Scan IA
- Anúncios ilimitados no marketplace
- Separadores

**Nota importante:** "Após trial: cartas ilimitadas pra sempre, sem Scan IA"

### 5.2 Pro Mensal

**Valor:** R$ 29,90/mês

**Cancelável:** Quando quiser, sem fidelidade

**Features Adicionais (vs Grátis):**
- Scan IA (com créditos/limite)
- Anúncios ilimitados no marketplace
- Dashboard completo
- Badge Pro no perfil
- Acesso a Separadores
- Suporte padrão

### 5.3 Pro Anual

**Valor:** R$ 249/ano

**Desconto:** 30% OFF (economiza R$ 109,80 vs R$ 358,80 anual)
**Preço mensal efetivo:** R$ 20,75/mês

**Features Adicionais:**
- Todas do Pro Mensal
- Prioridade no suporte
- Acesso antecipado a novos features

### 5.4 Planos para Lojistas

**Básico:** Grátis
- Listagem no Guia de Lojas
- URL customizada
- Botão WhatsApp

**Pro:** R$ 39/mês (ou R$ 390/ano)
- 14 dias grátis
- Publicação de eventos/torneios
- Analytics básico
- Customização de página

**Premium:** R$ 89/mês (ou R$ 890/ano)
- 14 dias grátis
- Eventos/torneios ilimitados
- Analytics completo (visualizações, cliques, dias da semana)
- Suporte prioritário
- Customização avançada

---

## 6. SEGURANÇA E PRIVACIDADE

### 6.1 Coleta de Dados

**Cadastro Voluntário:**
- Nome completo
- Email
- CPF
- Data de nascimento
- Cidade
- WhatsApp (opcional)

**Uso da Plataforma:**
- Cartas cadastradas e variantes
- Anúncios no Marketplace
- Avaliações de transações
- Histórico de navegação
- Imagens para escaneamento por IA

**Dados Técnicos:**
- Endereço IP
- Informações do dispositivo
- Eventos analíticos anônimos

### 6.2 Retenção de Dados

- **Contábeis/Pagamento:** 5 anos (obrigação legal tributária)
- **Após exclusão da conta:** Anonimizados ou excluídos em até 30 dias
- **Senhas:** Criptografia bcrypt (never plaintext)
- **Dados de cartão:** Nunca armazenados (Stripe apenas)

### 6.3 Compartilhamento

**Apenas com fornecedores operacionais:**
- Supabase (storage)
- Stripe (pagamentos)
- Resend (email)
- Anthropic (IA - Claude)
- Vercel (hosting)
- Google Analytics (analytics)

**Política:** "Não vendemos, alugamos ou cedemos seus dados pessoais a terceiros para fins comerciais"

### 6.4 Direitos do Usuário (LGPD)

Conforme Lei Geral de Proteção de Dados (Brasil):
- Solicitar acesso
- Solicitar correção
- Solicitar eliminação (right to be forgotten)
- Solicitar portabilidade
- Revogar consentimento

**Prazo de resposta:** Até 15 dias úteis
**Contato:** privacidade@bynx.gg

### 6.5 Segurança Técnica

- Criptografia bcrypt (senhas)
- HTTPS/TLS (comunicação)
- Controle de acesso baseado em função (RBAC)
- Monitoramento de acessos
- Notificação de incidentes (ANPD + usuários afetados)

---

## 7. POLÍTICAS LEGAIS

### 7.1 Termos de Uso

**Público-Alvo:**
- Colecionadores brasileiros de Pokémon TCG
- Menores de 13 anos: Não podem se cadastrar
- 13-17 anos: Necessário consentimento parental (LGPD)

**Obrigações:**
- Informações verídicas (nome, CPF, email, data de nascimento)
- Responsabilidade pela segurança de credenciais
- Proibição: Fraude, assédio, conteúdo ofensivo, scraping, sobrecarga de servidor, criação de contas falsas

**Responsabilidades da Plataforma:**
- Oferecida "no estado em que se encontra"
- Sem garantias de disponibilidade ininterrupta
- **Não intermedia transações** (marketplace P2P)
- **Não é responsável** por qualidade ou entrega de cartas vendidas

**Marketplace Específico:**
- Status de venda: Disponível, Reservado, Enviado, Concluído
- Contato via WhatsApp
- Avaliações públicas de ambas as partes
- Moderação ativa contra fraudes e "preços abusivos"

**Modificações de Termos:**
- Notificação com antecedência mínima de 15 dias
- Uso continuado = aceitação das novas condições

**Encerramento de Conta:**
- Bynx pode suspender/encerrar por violação
- Notificação por email
- Possibilidade de contestação via suporte@bynx.gg

**Jurisdição:** Leis brasileiras, foro em São Paulo/SP

---

## 8. ANÁLISE DE FUNCIONALIDADES POR CATEGORIA DE USUÁRIO

### 8.1 Colecionador Casual

**Problema Resolvido:** "Não sei quanto vale minha coleção"

**Features Essenciais:**
- ✅ Pokédex com 22k+ cartas
- ✅ Adição rápida de cartas (2 cliques)
- ✅ Scan IA (identificação automática)
- ✅ Dashboard com patrimônio total
- ✅ Perfil público para compartilhamento
- ✅ Grátis com 7 dias Pro

**Prioridade:** Alta

---

### 8.2 Colecionador/Investidor Sério

**Problema Resolvido:** "Preciso trackear ROI e performance de minha coleção"

**Features Essenciais:**
- ✅ Dashboard financeiro com métricas
- ✅ Histórico de preços (6 meses)
- ✅ Performance percentual (+13,6%)
- ✅ Exportação em CSV
- ✅ Análise por carta
- ✅ Acompanhamento em tempo real

**Features Desejadas (não encontradas):**
- ❌ Alertas de preço (notificações)
- ❌ Integração com Google Sheets
- ❌ API pública para análise customizada
- ❌ Comparação com índices (benchmark)

**Prioridade:** Alta

---

### 8.3 Colecionador Competitivo

**Problema Resolvido:** "Preciso evitar pagar muito por cartas hyped e tomar decisões informadas"

**Features Essenciais:**
- ✅ Preços por variante separados
- ✅ Histórico de preços
- ✅ Comparação min/médio/máximo
- ✅ Identification rápida de cartas
- ✅ Marketplace com referência de preço

**Features Desejadas:**
- ❌ Análise de meta (cartas trending)
- ❌ Alertas de preço quando cai
- ❌ Comunidade/fóruns para discussão

**Prioridade:** Média

---

### 8.4 Lojista

**Problema Resolvido:** "Como precificar minhas cartas? Como encontro mais clientes?"

**Features Essenciais:**
- ✅ Guia de Lojas (visibilidade)
- ✅ Preços de referência da Pokédex
- ✅ Planos com analytics (Pro/Premium)
- ✅ Publicação de eventos/torneios (Premium)

**Features Desejadas:**
- ❌ Integração com estoque/POS
- ❌ API para sincronizar preços
- ❌ Relatório de conversão

**Prioridade:** Média

---

### 8.5 Vendedor no Marketplace

**Problema Resolvido:** "Como encontro comprador para minha carta? Qual preço cobrar?"

**Features Essenciais:**
- ✅ Anúncio fácil via "+ Anunciar"
- ✅ Preço de referência Bynx
- ✅ Status de transação
- ✅ Sistema de avaliação

**Features Desejadas:**
- ❌ Proteção do comprador (escrow/intermediação)
- ❌ Shipping integrado
- ❌ Pagamento integrado (PayPal, PIX, etc)

**Prioridade:** Alta

---

## 9. FUNCIONALIDADES PRESENTES VS. AUSENTES

### Funcionalidades PRESENTES

✅ Autenticação básica (email/senha)  
✅ Catálogo/Pokédex com 22k+ cartas  
✅ Busca por nome, geração, tipo  
✅ Filtros por variante (Normal, Holo, Reverse, Foil, Promo)  
✅ Preços em BRL atualizados diariamente  
✅ Histórico de preços (6 meses)  
✅ Dashboard financeiro com patrimônio total  
✅ Scan IA com 97-99% de acurácia  
✅ Marketplace P2P (WhatsApp)  
✅ Perfis públicos de colecionadores  
✅ Sistema de avaliação em transações  
✅ Ranking de indicações com premiação  
✅ Guia de Lojas com filtros  
✅ Planos com trial grátis  
✅ Exportação de dados em CSV  
✅ LGPD-compliant  
✅ Moderação de marketplace  
✅ Separadores como produto complementar  
✅ Mobile responsiveness (Scan IA)  

### Funcionalidades AUSENTES

❌ Notificações em tempo real (push/email)  
❌ Chat integrado entre usuários  
❌ Sistema de seguir/seguidores  
❌ Comunidade integrada (fórums, grupos)  
❌ Autenticação OAuth (Google, Apple, Discord)  
❌ 2FA/Autenticação multi-fator  
❌ Wishlist/Favoritos oficial  
❌ Alertas de preço customizáveis  
❌ Integração com Google Sheets/Excel  
❌ API pública para desenvolvedores  
❌ Suporte a múltiplas moedas  
❌ Sincronização com apps externos  
❌ Sistema de referência/affiliate (apenas ranking de indicações)  
❌ Backup automático (explícito)  
❌ Busca por imagem similar  
❌ Discord/Telegram integrado  
❌ Blog ou educational content  

---

## 10. PRIORIDADE DE IMPLEMENTAÇÃO PARA SLABR

### CRÍTICA (P0) - Sem isso, não funciona como CCG marketplace

1. **Autenticação de Usuários** (email/senha, token-based)
2. **Catálogo de Cartas** (Pokédex-like com busca)
3. **Marketplace P2P** (criar/editar/listar anúncios)
4. **Dashboard de Portfólio** (patrimônio total, histórico)
5. **Sistema de Preços Dinâmicos** (atualização diária)
6. **Perfil do Usuário** (público/compartilhável)

### ALTA (P1) - Diferencial competitivo

1. **Scan IA** (reconhecimento de cartas via foto)
2. **Integração WhatsApp** (facilitador de transações)
3. **Histórico de Preços com Gráficos** (análise temporal)
4. **Variantes de Cartas** (Normal, Holo, Reverse, etc)
5. **Sistema de Avaliação** (reputação de vendedor)
6. **Guia de Lojas/Parceiros** (com mapa/filtros)

### MÉDIA (P2) - Bom ter, diferencia

1. **Ranking com Premiação** (gamificação)
2. **Separadores/Produtos Complementares** (upsell)
3. **Análise de ROI por Carta** (investidor-focused)
4. **Integração com Redes Sociais** (compartilhamento)
5. **Badge Pro/Status Verificado** (gamificação)
6. **Exportação de Dados** (flexibilidade)

### BAIXA (P3) - Melhorias futuras

1. **Notificações de Preço** (email/push)
2. **Chat Integrado** (vs WhatsApp)
3. **2FA/Multi-factor Auth**
4. **API Pública** (para integradores)
5. **Blog/Guias Educacionais**
6. **Sistema de Referência Avançado**

---

## 11. NOTAS DE IMPLEMENTAÇÃO

### 11.1 Decisões Arquiteturais

**Frontend:**
- Aparenta ser SPA (Single Page Application) com roteamento client-side
- Páginas públicas são SSG/ISR (Static Site Generation/Incremental Static Regeneration)
- Páginas autenticadas retornam 404 (redirecionamento via JavaScript)
- **Recomendação SLABR:** Next.js com SSG + App Router

**Backend:**
- Microserviços/APIs separadas:
  - API de Pokédex
  - API de Preços
  - API de Marketplace
  - API de Autenticação
  - API de Scan (IA)
- **Recomendação SLABR:** Node.js/Express ou Python FastAPI

**Database:**
- Dados de usuário: SQL (PostgreSQL com Supabase)
- Dados de cartas: SQL (tabelas normalize: cartas, sets, variantes, preços)
- Cache: Redis para preços atualizados em tempo real
- **Recomendação:** Supabase ou Firebase

**IA/Vision:**
- Claude Opus 4.5 via Anthropic API (verificar custos)
- Alternativa mais barata: Google Vision API ou AWS Rekognition
- **Consideração:** Custo por requisição é significativo

### 11.2 Integração com Serviços Externos

**Essenciais:**
- Stripe para pagamentos (cartão)
- Supabase para storage de imagens
- Anthropic Claude para Scan IA

**Opcionais mas Recomendados:**
- Google Analytics 4 (analytics)
- SendGrid/Resend para emails
- Mapbox/Google Maps para Guia de Lojas
- Twilio para WhatsApp API (alternativa a link direto)

### 11.3 Conformidade Legal (Brasil)

- **LGPD:** Política de privacidade, consentimento, direito ao esquecimento
- **Termos de Uso:** Responsabilidades da plataforma vs. usuários
- **Marketplace:** Moderação ativa, política anti-fraude
- **Pagamentos:** PCI-DSS compliance (delegar a Stripe)

### 11.4 Performance

- Otimização de imagens: CDN com compressão
- Lazy loading para catálogo grande (22k+ cartas)
- Cache de preços (atualização diária, não real-time)
- Indexação de busca: Elasticsearch ou Algolia

### 11.5 Segurança

- Criptografia bcrypt para senhas (não plaintext)
- HTTPS/TLS obrigatório
- Rate limiting em endpoints de API
- CORS configurado corretamente
- Validação de entrada (SQL injection, XSS prevention)
- Moderação de conteúdo no marketplace

---

## 12. RESUMO TÉCNICO

| Aspecto | Valor |
|---------|-------|
| **Catálogo** | 22.000+ cartas, 240+ sets |
| **Atualizador de Preços** | Diário |
| **Histórico** | 6 meses |
| **Variantes Suportadas** | 5+ (Normal, Holo, Reverse, Foil, Promo, Secret) |
| **Scan IA Acurácia** | 97-99% |
| **Scan IA Velocidade** | 3-6 segundos/foto |
| **Limite de Cartas por Foto** | 8 simultâneas |
| **Usuários Base** | Brasileiro (100% Brasil) |
| **Moeda** | BRL |
| **Maior Card** | Mew Star: R$ 19.000 |
| **Menor Card** | Não especificado |
| **Transações** | P2P via WhatsApp (não intermediado) |
| **Moderação** | Ativa (fraude + preços abusivos) |
| **Número de Lojas** | Não quantificado |

---

## 13. ANÁLISE COMPETITIVA (O que Bynx faz bem)

1. **Foco 100% Brasil:** Preços em BRL, lojas brasileiras, suporte em português
2. **Scan IA diferenciado:** 97-99% de acurácia com tolerância a ângulos/luz
3. **Dashboard financeiro inteligente:** ROI, performance, histórico
4. **Marketplace descentralizado:** Sem comissão, apenas moderação
5. **Freemium model:** 7 dias Pro + cartas ilimitadas forever no grátis
6. **Privacidade:** LGPD-compliant, sem cookies publicitários
7. **Comunidade legitimada:** 14 testimonials de usuários reais com localização

---

## 14. OPORTUNIDADES PARA SLABR

**Se o objetivo é criar um concorrente ou alternativa:**

1. **Integração de Pagamento:** Adicionar PIX/boleto/cartão integrado (vs WhatsApp)
2. **Chat Integrado:** Conversa dentro da plataforma (vs WhatsApp)
3. **Notificações Ativas:** Alertas de preço, novas vendas que batem wishlist
4. **API Pública:** Permitir integradores construírem features
5. **Community Features:** Fórums, grupos, discussões sobre meta
6. **Expandir Moedas:** Suporte a USD, EUR para exportação
7. **Blockchain/NFT:** Certificado de autenticidade (opcional, hype-driven)
8. **Análise de Meta:** Quais cartas estão trending, análises por competitivo

---

## 15. CONCLUSÃO

**Bynx.gg** é uma plataforma bem-construída, focada em resolver um problema específico e real do mercado de Pokémon TCG brasileiro. Sua combinação de:

- Catálogo abrangente (22k+ cartas)
- IA diferenciada (Scan com 97-99% acurácia)
- Dashboard inteligente (ROI tracking)
- Marketplace simplificado (WhatsApp)
- Modelo freemium agressivo (7 dias Pro + ilimitado forever)

...cria uma oferta competitiva e acessível.

Para **SLABR**, a implementação deve focar em **replicar os features críticos (P0)** com possível diferenciação nos **features de alta prioridade (P1)** — especialmente em áreas onde Bynx tem gaps:

- Chat integrado (não WhatsApp)
- Notificações de preço
- API pública
- Pagamento integrado

A segurança, privacidade e conformidade LGPD devem ser prioritárias desde o início.

---

**Análise Finalizada**  
**Data:** 14 de Junho de 2026
