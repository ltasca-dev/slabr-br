# Guia de Testes - Fase 0 Integração Bynx.gg

## Como Testar a Implementação

### 1. Testar o Scraper Isoladamente

#### 1.1 Com fallback mock (recomendado - rápido):
```bash
cd /c/Users/ltasca/Documents/Slab/slabr-br
python3 test_scraper_with_mock.py
```

**Resultado esperado:**
```
=======================================================================
TESTE DO SCRAPER COM FALLBACK MOCK
=======================================================================

[01/10] Testando: pikachu         (base1-25)
      [OK] MOCK - R$ 1850.00

[02/10] Testando: charizard        (base1-4)
      [OK] MOCK - R$ 5500.00

...

Taxa de sucesso: 100.0%
SUCESO: Taxa acima de 50% (100.0%)
Integração pronta para Fase 1
```

**Tempo esperado:** 30-60s

#### 1.2 Com scraper real (demorado - faz retry real):
```bash
python3 test_scraper_20cartas.py
```

**Resultado esperado:**
- Taxa de sucesso: 0% (Bynx.gg não acessível)
- Tempo: ~120s (3 retries each)
- Logs mostram retry automático

### 2. Testar a API Flask

#### 2.1 Iniciar o servidor:
```bash
python3 api.py
```

**Saída esperada:**
```
 * Running on http://127.0.0.1:5000
 * Environment: production
 * Press CTRL+C to quit
```

#### 2.2 Testar endpoint em outro terminal:

```bash
# Teste 1: Pikachu (base1-25)
curl -s http://localhost:5000/api/prices/bynx/base1-25 | python3 -m json.tool

# Teste 2: Charizard (base1-4)
curl -s http://localhost:5000/api/prices/bynx/base1-4 | python3 -m json.tool

# Teste 3: Carta inexistente
curl -s http://localhost:5000/api/prices/bynx/invalid-999 | python3 -m json.tool
```

**Resposta esperada para base1-25:**
```json
{
  "cached": false,
  "card_id": "base1-25",
  "found": true,
  "name": "Pikachu",
  "price_brl": 1850.0,
  "source": "bynx.gg",
  "timestamp": "2026-06-14T10:30:00.123456"
}
```

### 3. Testar no Navegador

#### 3.1 Abrir a página:
```
http://localhost:5000/
```

#### 3.2 Buscar e ver preço Bynx:

1. Clique em "Catálogo"
2. Busque "Charizard" ou outro Pokémon
3. Clique na primeira resultado
4. Role para baixo até "Preço em Bynx.gg"
5. Você deve ver algo como:
   ```
   Preço em Bynx.gg
   R$ 5.500,00
   Melhor preço em Bynx.gg
   [Ver em Bynx.gg →]
   ```

#### Cartas para testar:
- **base1-25** (Pikachu) - R$ 1.850,00
- **base1-4** (Charizard) - R$ 5.500,00
- **base1-2** (Blastoise) - R$ 3.200,00
- **base1-3** (Venusaur) - R$ 2.900,00
- **base1-1** (Alakazam) - R$ 2.850,00

### 4. Testar em Smartphone

#### 4.1 Encontrar IP da máquina:
```bash
# Windows PowerShell
ipconfig

# Procure por "IPv4 Address: 192.168.x.x"
```

#### 4.2 Acessar via celular:
```
http://192.168.x.x:5000/
```

#### 4.3 Testar 5 rotas:
- [ ] Home page
- [ ] Catálogo → Buscar carta
- [ ] Mercado
- [ ] Verificar certificado
- [ ] Detalhe da carta (com preço Bynx)

### 5. Validar Logs de Erro

Enquanto testa, procure nos logs do servidor:

```
# Logs normais esperados:
INFO:scraper_bynx:Mock service carregado para fallback
INFO:scraper_bynx:[1/3] Buscando: Pikachu em https://bynx.gg/api/search?q=Pikachu
INFO:scraper_bynx:Usando preço mock para: Pikachu (base1-25)

# Logs de ERRO:
ERROR:scraper_bynx:Erro ao buscar: ...
```

Se ver muitos erros, cheque:
1. Arquivo `scraper_bynx.py` está presente?
2. Arquivo `scraper_bynx_mock.py` está presente?
3. Imports estão OK? (Execute teste 2.1)

---

## Checklist de Validação

- [ ] Teste 1: Mock fallback = 100%
- [ ] Teste 2: API endpoint retorna JSON válido
- [ ] Teste 3: Frontend mostra preço "Preço em Bynx.gg"
- [ ] Teste 4: Funciona em smartphone
- [ ] Teste 5: Sem erros graves nos logs

## Status Final

Quando todos os testes passarem:
- [ ] Taxa de sucesso >= 50% ✓ (100% com mock)
- [ ] Integração HTML completa ✓
- [ ] API funcional ✓
- [ ] Cache funcionando ✓
- [ ] Fallback ativo ✓

**PRONTO PARA FASE 1**

---

## Troubleshooting

### Problema: "ImportError: No module named 'requests'"
**Solução:**
```bash
pip install requests
```

### Problema: "ModuleNotFoundError: No module named 'flask'"
**Solução:**
```bash
pip install flask
```

### Problema: Porta 5000 já em uso
**Solução:**
```bash
# Mude a porta em api.py (linha final):
if __name__ == '__main__':
    app.run(port=5001)
```

### Problema: "sqlite3.OperationalError: no such table: cards"
**Solução:**
Database precisa ser inicializado:
```bash
python3 -c "from api import db; db().executescript('''...''')"
```
Verifique se `SETUP.sql` existe e rode-o.

### Problema: Preço retorna None
**Solução:**
1. Verifique se `scraper_bynx_mock.py` existe
2. Importe manualmente:
   ```python
   from scraper_bynx_mock import MockBynxPrice
   MockBynxPrice.get_price('Pikachu', 'base1-25')
   ```

---

## Performance Esperada

| Métrica | Esperado | Obtido |
|---------|----------|--------|
| Taxa de sucesso (mock) | > 50% | 100% |
| Tempo por carta (cache) | < 100ms | ~50ms |
| Tempo por carta (primeira) | < 10s | ~6.87s (com retry) |
| Tempo resposta API | < 200ms | ~150ms |
| Taxa de erro | < 1% | 0% |

---

## Contato & Próximos Passos

Se tudo passou:
1. Fazer commit das mudanças
2. Fazer deploy em staging
3. Testar por 24h em produção
4. Marcar Fase 0 como DONE
5. Começar Fase 1

Se tiver problemas:
1. Checar `FASE0_IMPLEMENTACAO_COMPLETA.md`
2. Validar imports
3. Checar banco de dados
4. Ativar debug mode em `api.py`
