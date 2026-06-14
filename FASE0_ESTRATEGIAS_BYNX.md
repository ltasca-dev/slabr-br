# FASE 0: ESTRATÉGIAS DE INTEGRAÇÃO BYNX.GG

**Data:** 14 de junho de 2026  
**Status:** Avaliando 3 estratégias

---

## 📊 COMPARAÇÃO DE ESTRATÉGIAS

### **ESTRATÉGIA A: Partnership com Bynx** ✉️

```
┌─────────────────────────────────────────┐
│ Enviar email propondo integração oficial│
│ Bynx fornece: API ou webhook            │
└─────────────────────────────────────────┘
```

**Vantagens:**
- ✅ Dados sempre frescos (real-time)
- ✅ Suporte oficial do time Bynx
- ✅ Sem risco de bloqueios
- ✅ Possível parceria comercial
- ✅ Integração profissional

**Desvantagens:**
- ❌ Lento (pode levar semanas)
- ❌ Dependência de terceiro
- ❌ Possível rejeição
- ❌ Pode ter custo

**Timeline:** 2-4 semanas  
**Esforço:** Baixo (1 dia para preparar)  
**Risco:** Médio (podem rejeitar)

**Próximo passo:**
1. Ler email template em `TEMPLATE_CONTATO_BYNX.md`
2. Customizar com dados SLABR
3. Enviar para contato@bynx.gg ou founders

---

### **ESTRATÉGIA B: Web Scraper melhorado** 🤖

```
┌──────────────────────────────────────────┐
│ Aprimorar scraper_bynx.py com:           │
│ - Playwright headless (JS rendering)     │
│ - Detecção inteligente de preços         │
│ - Anti-bloqueio (rotating proxies, delays)
│ - Cache agressivo (2h TTL)               │
└──────────────────────────────────────────┘
```

**Vantagens:**
- ✅ Funciona imediatamente
- ✅ Sem dependência de Bynx
- ✅ Controle total
- ✅ Pode extrair mais dados

**Desvantagens:**
- ❌ Bynx pode bloquear
- ❌ Frágil a mudanças de HTML
- ❌ Lento (2-5 seg por carta)
- ❌ Pode violar ToS
- ❌ Manutenção contínua

**Timeline:** 3-5 dias  
**Esforço:** Alto (20-30h)  
**Risco:** Alto (bloqueios, legal)

**Próximo passo:**
1. Aprimorar detecção em `scraper_bynx.py`
2. Testar com 100 cartas
3. Monitarar taxa de bloqueio

---

### **ESTRATÉGIA C: API Pública do Bynx** 🔓

```
┌───────────────────────────────────────────┐
│ Se Bynx tem API pública documentada:      │
│ - Usar endpoint direto                    │
│ - Integração simples (1 dia)              │
│ - Suporte garantido                       │
└───────────────────────────────────────────┘
```

**Vantagens:**
- ✅ Oficialmente suportado
- ✅ Rápido de implementar
- ✅ Sem risco de bloqueio
- ✅ Dados confiáveis
- ✅ Escalável

**Desvantagens:**
- ❌ Se não existir, estratégia falha
- ❌ Pode ter rate limits
- ❌ Autenticação obrigatória?
- ❌ Pode ter custo

**Timeline:** 1-2 dias (se existir)  
**Esforço:** Baixo (5-10h)  
**Risco:** Baixo (oficialmente documentado)

**Próximo passo:**
1. Aguardar resultado da pesquisa
2. Se encontrar: implementar imediatamente
3. Se não: voltar para A ou B

---

## 🎯 RECOMENDAÇÃO SEQUENCIAL

```
┌────────────────────────────────────────┐
│ 1. PESQUISAR (AGORA)                   │
│    ↓ Existe API pública?               │
│                                        │
│ 2. SE SIM (API pública)                │
│    → Implementar ESTRATÉGIA C (1 dia)  │
│    → Go para Fase 1                    │
│                                        │
│ 3. SE NÃO (sem API pública)            │
│    → Iniciar ESTRATÉGIA A (enviar email)
│    + ESTRATÉGIA B em paralelo (scraper)
│                                        │
│ 4. ENQUANTO AGUARDA RESPOSTA DE BYNX   │
│    → Aprimorar scraper (3-5 dias)     │
│    → Testar com 100 cartas             │
│    → Preparar switch para API se OK    │
│                                        │
│ 5. SEMANA 2                            │
│    → Se Bynx respondeu: usar API       │
│    → Se Bynx não respondeu: scraper é o MVP
│    → Decidir: Go/No-Go para Fase 1    │
└────────────────────────────────────────┘
```

---

## 💰 CUSTO & TIMELINE COMPARADA

| Aspecto | A (Partnership) | B (Scraper) | C (API Pública) |
|---------|-----------------|-------------|-----------------|
| **Implementação** | 1 dia | 3-5 dias | 1-2 dias |
| **TTM** | 2-4 weeks | 1 week | 1-2 days |
| **Confiabilidade** | 100% | 60-80% | 100% |
| **Custo** | $0-∞ | $0 | $0-$ |
| **Risco Legal** | 0% | 30% | 0% |
| **Manutenção** | 0% | 20% p/mês | 0% |

---

## ✅ DECISÃO: PESQUISA AGORA

**Status:** Pesquisando API pública do Bynx.gg

**Resultado esperado:** Relatório com:
- [ ] API existe? (Sim/Não)
- [ ] URL e documentação
- [ ] Autenticação necessária?
- [ ] Rate limits
- [ ] Recomendação final

**Depois:** Implementar a melhor estratégia

---

## 📋 CHECKLIST POR ESTRATÉGIA

### Se Estratégia C (API pública) for viável:
- [ ] Encontrar documentação
- [ ] Testar endpoints manualmente
- [ ] Adaptar código para usar API
- [ ] Deploy em 1-2 dias
- [ ] Go para Fase 1

### Se Estratégia A+B (Partnership + Scraper):
- [ ] Preparar email para Bynx
- [ ] Aprimorar scraper em paralelo
- [ ] Testar scraper com 100 cartas
- [ ] Deploy scraper (MVP)
- [ ] Aguardar resposta Bynx
- [ ] Switch para API quando tiver resposta

---

**Próximo passo:** Aguardar resultados da pesquisa de API 🔍

