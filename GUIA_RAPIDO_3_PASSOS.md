# ⚡ GUIA RÁPIDO - 3 PASSOS PARA COLOCAR ONLINE

**Tempo total: 10 minutos**

---

## ✅ STATUS ATUAL

```
✅ Flask rodando:           http://localhost:5000
✅ Endpoints testados:      /api/prices/bynx/*
✅ Frontend integrado:      slabr_app.html
✅ Database:                pokemon_catalog.db
✅ Git:                     2 commits prontos
```

**Faltando:** Ativar Cloudflare Tunnel

---

## 🚀 PASSO 1: ABRIR NOVO TERMINAL

1. Abra um novo terminal (Bash, PowerShell ou Git Bash)
2. Verifique se `cloudflared` está instalado:
   ```bash
   cloudflared --version
   ```

**Se retornar a versão:** ✅ Pronto! Vá para PASSO 2

**Se retornar "command not found":** Instale aqui:
- Windows: https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/
- Mac: `brew install cloudflare/cloudflare/cloudflared`
- Linux: `curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -o /usr/local/bin/cloudflared`

---

## 🔗 PASSO 2: INICIAR CLOUDFLARE TUNNEL

No novo terminal, execute:

```bash
cloudflared tunnel run slabr-br
```

**Você verá algo assim:**
```
2026-06-14T14:45:00.000Z INF Starting metrics server on 127.0.0.1:46827
2026-06-14T14:45:01.000Z INF Tunnel running on https://anime-pregnancy-graphical-statistics.trycloudflare.com
```

✅ **Cloudflare Tunnel está ONLINE!**

Deixe este terminal aberto (não feche).

---

## 🌐 PASSO 3: TESTAR EM PRODUÇÃO

Em outro terminal (seu terminal original), teste:

```bash
# Health check
curl https://anime-pregnancy-graphical-statistics.trycloudflare.com/api/prices/bynx/health

# Deve retornar:
# {"status": "healthy", "scraper": "online"}
```

✅ **Se respondeu, você está ONLINE em produção!**

Agora abra no navegador:
```
https://anime-pregnancy-graphical-statistics.trycloudflare.com/#/carta/base1-4
```

Procure por "Preço em Bynx.gg - R$ 5.500,00" 🎉

---

## ✨ PRONTO!

Sua aplicação está LIVE em:
```
🌐 https://anime-pregnancy-graphical-statistics.trycloudflare.com
```

---

## 📋 MANTENDO ONLINE

Para manter a aplicação rodando:

**Terminal 1 (nunca feche):**
```bash
cloudflared tunnel run slabr-br
```

**Terminal 2:**
```bash
cd /c/Users/ltasca/Documents/Slab/slabr-br
python api.py
```

Ambos precisam estar rodando!

---

## 🆘 QUICK TROUBLESHOOTING

### Flask não inicia
```bash
# Pode estar portada ocupada (5000)
lsof -i :5000
# Se encontrar, mate o processo:
kill -9 <PID>
# Tente novamente
python api.py
```

### Tunnel não conecta
```bash
# Verifique se cloudflared está instalado
cloudflared --version

# Tente reconectar
cloudflared tunnel run slabr-br
```

### URL retorna erro
```bash
# Aguarde 10 segundos para tunnel ativar
# Se continuar, check logs:
tail -f api_production.log
```

---

## 📊 URLs PARA TESTAR

Coloque cada uma no navegador para confirmar:

1. **Home:**
   ```
   https://anime-pregnancy-graphical-statistics.trycloudflare.com
   ```

2. **Carta específica (Charizard):**
   ```
   https://anime-pregnancy-graphical-statistics.trycloudflare.com/#/carta/base1-4
   ```

3. **API Health Check:**
   ```
   https://anime-pregnancy-graphical-statistics.trycloudflare.com/api/prices/bynx/health
   ```

4. **API Preço (JSON):**
   ```
   https://anime-pregnancy-graphical-statistics.trycloudflare.com/api/prices/bynx/base1-4
   ```

---

## 🎉 PRÓXIMOS PASSOS

Após confirmar que tudo está online:

1. **Compartilhar link** para 10 amigos testar
2. **Coletar feedback** nos primeiros 15 minutos
3. **Monitorar erros** nos próximos 7 dias
4. **Fazer Go/No-Go** na semana 4

---

**Você está a 3 passos de colocar SLABR 2.0 online! 🚀**

Próximo passo: Execute o PASSO 1 acima ☝️

