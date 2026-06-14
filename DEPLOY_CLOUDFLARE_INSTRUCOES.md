# 🚀 GUIA DE DEPLOY - FASE 0 PARA CLOUDFLARE

**Data:** 14 de junho de 2026  
**URL Atual:** https://anime-pregnancy-graphical-statistics.trycloudflare.com/  
**Status:** Pronto para deploy Fase 0

---

## 📋 PRÉ-REQUISITOS

- ✅ Git inicializado (já feito)
- ✅ Código Fase 0 commitado
- ✅ Cloudflare Pages ou similar configurado
- ✅ Environment variables prontas
- ✅ Database connection string
- ✅ Flask app testado localmente

---

## 🎯 OPÇÃO 1: DEPLOY VIA GITHUB (Recomendado)

### Passo 1: Criar repositório no GitHub
```bash
# No GitHub web:
1. Ir para github.com
2. Novo repositório "slabr-br"
3. NÃO inicialize com README (já temos commits)
4. Copie a URL: https://github.com/seu-user/slabr-br.git
```

### Passo 2: Configurar remoto e fazer push
```bash
cd /c/Users/ltasca/Documents/Slab/slabr-br

# Adicione o repositório remoto
git remote add origin https://github.com/seu-user/slabr-br.git

# Renomear branch se necessário (Cloudflare geralmente quer 'main')
git branch -M main

# Fazer push
git push -u origin main
```

### Passo 3: Conectar ao Cloudflare Pages
1. Abra Cloudflare Dashboard
2. Pages → Criar aplicação → GitHub
3. Selecione repositório "slabr-br"
4. Build settings:
   ```
   Framework preset: None (custom)
   Build command: pip install -r requirements.txt
   Build output directory: .
   Root directory: (deixe vazio)
   ```
5. Environment variables:
   ```
   FLASK_ENV=production
   FLASK_APP=api.py
   DATABASE_URL=seu-database-url
   SECRET_KEY=sua-chave-secreta
   ```
6. Deploy

---

## 🎯 OPÇÃO 2: DEPLOY DIRETO (Sem GitHub)

### Se usar GitLab, Bitbucket ou outro:
```bash
# Substitua a URL pelo seu serviço
git remote add origin https://seu-git-provider.com/seu-user/slabr-br.git
git branch -M main
git push -u origin main
```

### Se usar Heroku:
```bash
# Login no Heroku
heroku login

# Criar app
heroku create slabr-br

# Deploy
git push heroku main

# Ver logs
heroku logs --tail
```

### Se usar servidor próprio (VPS/Dedicated):
```bash
# SSH para servidor
ssh user@seu-servidor.com

# Clone o repo
git clone seu-repo.git /app/slabr-br
cd /app/slabr-br

# Instale dependências
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Configure supervisor/systemd para rodar api.py
# (instruções customizadas para seu servidor)

# Inicie app
python api.py --host 0.0.0.0 --port 5000
```

---

## 🌐 OPÇÃO 3: MANTER CLOUDFLARE TUNNEL (Atual)

Se você está usando `cloudflared` local (tunnel) para expor a app:

```bash
# Terminal 1: Inicie o Flask
cd /c/Users/ltasca/Documents/Slab/slabr-br
source .venv/Scripts/activate
python api.py

# Terminal 2: Inicie o tunnel (se não estiver rodando)
cloudflared tunnel run slabr-br
# Ou com URL específica:
cloudflared tunnel run --url http://localhost:5000 slabr-br
```

**Atualize a URL em:**
1. Documentação
2. Links de compartilhamento
3. Analytics
4. DNS registros

---

## ✅ CHECKLIST PRÉ-DEPLOY

Antes de fazer deploy, verifique:

- [ ] **Dependências**
  ```bash
  pip list | grep -E "flask|requests|playwright"
  ```

- [ ] **Variáveis de ambiente** (criar `.env` se necessário)
  ```bash
  FLASK_ENV=production
  DATABASE_URL=postgresql://...
  SECRET_KEY=sua-chave-aleatoria-longa
  ```

- [ ] **Database migrations**
  ```bash
  # Se houver alterações na schema
  python ingest_catalog.py
  ```

- [ ] **Testes rápidos**
  ```bash
  curl http://localhost:5000/api/prices/bynx/health
  curl http://localhost:5000/api/prices/bynx/base1-4
  ```

- [ ] **Requirements.txt atualizado**
  ```bash
  pip freeze > requirements.txt
  ```

- [ ] **Nenhum segredo commitado**
  ```bash
  git log -p | grep -i "password\|key\|secret"
  ```

---

## 🚨 MONITORAMENTO PÓS-DEPLOY

### Health check automático
```bash
# Configurar cron para verificar a cada 5 minutos
*/5 * * * * curl -f https://seu-url/api/prices/bynx/health || notify

# Ou use uma ferramície de monitoramento:
# - UptimeRobot (free)
# - Datadog
# - New Relic
# - CloudFlare Analytics
```

### Logs
```bash
# Se em Cloudflare Pages:
# Dashboard → Pages → slabr-br → Analytics

# Se em Heroku:
# heroku logs --tail

# Se servidor próprio:
# tail -f /var/log/flask.log
```

### Alertas
- Receba notificações se /health retornar erro
- Monitore taxa de erro do scraper
- Alertas de performance (> 500ms)

---

## 🔄 ROLLBACK (Se algo der errado)

```bash
# Ver commits anteriores
git log --oneline

# Reverter para versão anterior (sem perder commits)
git revert HEAD

# Ou fazer reset (cuidado!)
git reset --hard <commit-hash>

# Deploy novamente
git push origin main
```

---

## 📊 VARIÁVEIS DE AMBIENTE NECESSÁRIAS

Crie um arquivo `.env` local (não commite para git):

```env
# Flask
FLASK_ENV=production
FLASK_APP=api.py
FLASK_DEBUG=0

# Database
DATABASE_URL=postgresql://user:pass@host:5432/slabr_db
# Ou SQLite (local):
DATABASE_URL=sqlite:///pokemon_catalog.db

# Secrets
SECRET_KEY=gerar-uma-chave-aleatoria-longa-aqui
API_KEY_BYNX=se-tiver-acesso-api

# Bynx Integration
BYNX_SCRAPER_ENABLED=1
BYNX_MOCK_FALLBACK=1
BYNX_CACHE_TTL=3600

# Email (para notificações)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=seu-email@gmail.com
SMTP_PASSWORD=sua-senha-app

# Analytics
ANALYTICS_ENABLED=1
ANALYTICS_API_KEY=seu-key-analytics
```

**Cloudflare Pages:** Adicione estas variáveis no dashboard:
1. Settings → Environment variables
2. Adicione cada variável

---

## 🎯 PRÓXIMOS PASSOS APÓS DEPLOY

### Imediatamente (Primeira hora)
- [ ] Verificar URL em produção
- [ ] Testar 5 cartas diferentes
- [ ] Verificar logs de erro
- [ ] Confirmar preços estão mostrando

### Dia 1
- [ ] Compartilhar link com 10 usuários de teste
- [ ] Coletar feedback inicial
- [ ] Monitorar performance
- [ ] Verificar taxa de erro do scraper

### Semana 1
- [ ] Análise de dados (quantos usuários, CTR, etc)
- [ ] Bug fixes críticos
- [ ] Otimizações de performance
- [ ] Preparar documentação para Go/No-Go

### Semana 2-4
- [ ] Teste de carga (1000 usuários)
- [ ] Security audit
- [ ] Beta com 500 usuários
- [ ] Go/No-Go decision para Fase 1

---

## 🐛 TROUBLESHOOTING

### Erro: "Module not found: scraper_bynx"
```bash
# Verifique se os arquivos existem
ls -la scraper_bynx.py scraper_bynx_mock.py

# Reinstale dependências
pip install -r requirements.txt
```

### Erro: "Database connection failed"
```bash
# Verifique a URL de conexão
echo $DATABASE_URL

# Teste conexão
psql $DATABASE_URL -c "SELECT 1"
```

### Scraper retorna 0% de sucesso
- Verifique se Bynx.gg está acessível
- Verificar logs: `tail -f api.log`
- Aumentar timeout em `scraper_bynx.py`
- Fallback automático para mock (já implementado)

### Site muito lento
- Verificar cache (TTL configurado?)
- Ver CPU/memória do servidor
- Otimizar database queries
- Usar CDN (Cloudflare já faz isso)

---

## 📞 CONTATOS & SUPORTE

**Dúvidas sobre deployment?**
- Cloudflare: docs.cloudflare.com
- Flask: flask.palletsprojects.com
- Python: python.org

**Time SLABR:**
- Tech lead: seu-email@a4solutions.com.br
- DevOps: seu-devops@a4solutions.com.br

---

**Documento criado:** 14 de junho de 2026  
**Próxima atualização:** Após Fase 1 planejamento  
**Versão:** 1.0 - Pronto para produção

