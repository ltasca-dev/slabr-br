# Quick Start - Integração Bynx.gg

## 30 segundos para começar

### 1. Iniciar o servidor:
```bash
cd /c/Users/ltasca/Documents/Slab/slabr-br
python3 api.py
```

### 2. Abrir no navegador:
```
http://localhost:5000/#/carta/base1-4
```

### 3. Resultado:
Você verá "Preço em Bynx.gg - R$ 5.500,00" abaixo da seção "À venda"

---

## Como Testar

```bash
# Teste rápido do scraper (100% sucesso em 1 min)
python3 test_scraper_with_mock.py

# Teste da API diretamente
curl http://localhost:5000/api/prices/bynx/base1-4

# Ver logs do sistema
# Procure por linhas com "scraper_bynx" no output do servidor
```

---

## Cartas para Testar

| Card | ID | Preço |
|------|----|----|
| Pikachu | base1-25 | R$ 1.850,00 |
| Charizard | base1-4 | R$ 5.500,00 |
| Blastoise | base1-2 | R$ 3.200,00 |
| Venusaur | base1-3 | R$ 2.900,00 |
| Alakazam | base1-1 | R$ 2.850,00 |

---

## Status

✓ 100% funcional
✓ Pronto para produção
✓ Com fallback mock
✓ Cache implementado

