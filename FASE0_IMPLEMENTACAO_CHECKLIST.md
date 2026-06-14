# ✅ FASE 0 - CHECKLIST DE IMPLEMENTAÇÃO

**Timeline:** 4 semanas  
**Status:** Iniciado em 14 de junho de 2026

---

## 📋 SEMANA 1: SETUP & INTEGRAÇÃO BACKEND

### [ ] 1.1 - Instalar dependências
```bash
pip install requests playwright
python -m playwright install chromium
```

### [ ] 1.2 - Integrar scraper no api.py
**Arquivo:** `C:\Users\ltasca\Documents\Slab\slabr-br\api.py`

Adicione no início:
```python
# Após os imports existentes
from scraper_bynx import BynxScraperSync
_bynx_scraper = BynxScraperSync()
```

### [ ] 1.3 - Copiar endpoints para api.py
Copie TODO o código de `api_bynx_endpoint.py` para `api.py`

Endpoints adicionados:
- `GET /api/prices/bynx/<card_id>` - Busca preço
- `GET /api/prices/bynx/compare/<card_id>` - Compara SLABR vs Bynx
- `POST /api/prices/bynx/bulk` - Busca em lote
- `GET /api/prices/bynx/health` - Health check

### [ ] 1.4 - Testar endpoints

```bash
# Terminal 1: Inicie o app
cd C:\Users\ltasca\Documents\Slab\slabr-br
source .venv/Scripts/activate
python api.py

# Terminal 2: Teste os endpoints
curl http://localhost:5000/api/prices/bynx/base1-4
curl http://localhost:5000/api/prices/bynx/compare/base1-4
curl http://localhost:5000/api/prices/bynx/health
```

**Status esperado:** 200 OK com dados ou 404

---

## 📋 SEMANA 2: INTEGRAÇÃO FRONTEND

### [ ] 2.1 - Modificar renderCarta() em HTML
**Arquivo:** `slabr_app.html`

Encontre a função `renderCarta()` (linha ~392) e adicione:

```javascript
// Após: const offers = await J('/all-copies/'+id)||[];
const bynx_price = await J('/api/prices/bynx/'+id)||null;
```

### [ ] 2.2 - Adicionar componente de preço Bynx no HTML
Na seção `.two` da página de detalhe, adicione:

```html
<!-- Após a seção de ofertas -->
<div class="bynx-price-panel" style="margin-top:20px;padding:14px;border:1px solid var(--line);border-radius:10px">
  <div class="sectit">Preço em Bynx.gg</div>
  ${bynx_price && bynx_price.found?`
    <div style="font-size:18px;color:var(--champagne);margin:8px 0">
      R$ ${bynx_price.price_brl.toLocaleString('pt-BR')}
    </div>
    <a href="https://bynx.gg/search?q=${bynx_price.name}" target="_blank" style="color:var(--mist);font-size:12px">
      Ver em Bynx.gg →
    </a>
  `:`<div style="color:var(--mist);font-size:12px">Preço não disponível</div>`}
</div>
```

### [ ] 2.3 - Testar no navegador
1. Acesse uma carta: `https://anime-...trycloudflare.com/#/carta/base1-4`
2. Scroll down
3. Deve aparecer "Preço em Bynx.gg" com o valor

---

## 📋 SEMANA 3: TESTE & OTIMIZAÇÃO

### [ ] 3.1 - Testar 10 cartas diferentes
```javascript
const test_ids = [
  "base1-1", "base1-4", "base1-2",
  "base2-11", "swsh4-171", "sv1-121",
  "bw2-11", "xy1-3", "sm1-1"
];

// For each, test: GET /api/prices/bynx/{card_id}
```

### [ ] 3.2 - Otimizar cache
- Cache TTL: 60 minutos (já está em `api_bynx_endpoint.py`)
- Implementar Redis se houver (opcional para Fase 0)

### [ ] 3.3 - Performance check
- Tempo de resposta: < 5 segundos
- Taxa de sucesso: > 80%
- Erro rate: < 5%

### [ ] 3.4 - Error handling
- Se Bynx.gg não responde: mostrar "Indisponível"
- Se carta não encontrada: mostrar "Não encontrada em Bynx"
- Se timeout: cache anterior ou fallback

---

## 📋 SEMANA 4: DEPLOY & VALIDAÇÃO

### [ ] 4.1 - Deploy em produção
```bash
# Build docker (se usar Docker)
docker build -t slabr:fase0 .

# Ou deploy direto
git push origin main
```

### [ ] 4.2 - Monitorar via health check
```bash
# Cron job a cada 5 minutos
*/5 * * * * curl http://localhost:5000/api/prices/bynx/health
```

### [ ] 4.3 - Testar com 100 usuários piloto
- Convidar 100 usuários para testar
- Coletar feedback
- Medir NPS

### [ ] 4.4 - Go/No-Go decision
**Critério de sucesso:**
- ✅ NPS > 20
- ✅ Taxa de erro < 3%
- ✅ Performance < 3 seg (90º percentile)
- ✅ CTR > 1% (cliques em "Ver em Bynx")

**Se GO:**
→ Avançar para Fase 1 (16 semanas)

**Se NO-GO:**
→ Pivotear ou abortar

---

## 🔧 TROUBLESHOOTING

### Problema: "ModuleNotFoundError: No module named 'scraper_bynx'"
**Solução:** Certifique-se que `scraper_bynx.py` está no mesmo diretório que `api.py`

### Problema: "Playwright timeout"
**Solução:** Aumentar timeout em `scraper_bynx.py`:
```python
await self.page.goto(search_url, wait_until='networkidle', timeout=30000)  # 30s
```

### Problema: Bynx.gg bloqueia o scraper
**Solução 1:** Usar fallback com requests (já está implementado)
**Solução 2:** Fazer parceria com Bynx (enviar email)

### Problema: "Preço não disponível em Bynx"
**Solução:** Carta pode não existir em Bynx.gg ainda (ex: cartas novas)

---

## 📊 MÉTRICAS PARA RASTREAR

| Métrica | Target | Atual |
|---------|--------|-------|
| Taxa de sucesso (queries) | > 80% | ??? |
| Tempo médio (ms) | < 3000 | ??? |
| Uptime do scraper | > 99% | ??? |
| NPS (piloto) | > 20 | ??? |
| CTR (click em Bynx) | > 1% | ??? |

---

## 🚀 PRÓXIMOS PASSOS

### Hoje (14 de junho):
- [ ] Ler este documento
- [ ] Instalar dependências
- [ ] Integrar scraper no api.py
- [ ] Testar endpoints

### Amanhã:
- [ ] Integrar no frontend HTML
- [ ] Testar no navegador
- [ ] Primeira rodada de debugging

### Próximas 2 semanas:
- [ ] Otimizar performance
- [ ] Testar com múltiplas cartas
- [ ] Decidir Go/No-Go

---

## 📞 CONTATOS & ESCALATION

**Tech issues:**
→ Verificar `IMPLEMENTACAO_TECNICA_FASE0.md`

**Bynx partnership:**
→ Usar `TEMPLATE_CONTATO_BYNX.md`

**Decisão Go/No-Go:**
→ Apresentar resultados ao Board

---

**Documentação criada em:** 14 de junho de 2026  
**Responsável:** Tim de Dev (Backend + Frontend + QA)  
**Classificação:** CONFIDENCIAL - ESTRATÉGICO
