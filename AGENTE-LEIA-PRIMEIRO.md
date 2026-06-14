# SLABR.br — INSTRUÇÕES PARA O AGENTE DE IMPLANTAÇÃO

Leia este arquivo primeiro. Há **dois caminhos**. Faça o **Caminho A** já (sobe na hora,
sem conta nenhuma) e use o **Caminho B** para a produção real no Supabase.

> ⚠️ O agente NÃO deve criar contas, NÃO deve inventar/baixar credenciais e NÃO deve
> colocar segredos em arquivos versionados. As chaves do Supabase vêm **do usuário**
> (ele cria o projeto e te passa). Onde precisar de credencial, **peça ao usuário**.

---

## Inventário
```
slabr_app.html                         front do protótipo (fala com api.py via /api)
api.py                                 backend Flask (SQLite) — protótipo
pokemon_catalog.db                     catálogo: 173 sets, 20.324 cartas (+ dados demo)
requirements.txt / Procfile            deps + start (gunicorn)
publicar.sh                            sobe app + túnel HTTPS (Mac/Linux)

slabr-supabase.html                    front de PRODUÇÃO (fala com Supabase via supabase-js)
SETUP-SUPABASE.md                      guia detalhado de produção (passo a passo)
supabase/schema_supabase.sql           tabelas + RLS + trigger + bucket (colar no SQL Editor)
supabase/migrate_catalog_to_supabase.py  migra o catálogo do SQLite -> Supabase
supabase/functions/price-updater/      Edge Function: preços por variante (Deno)
supabase/functions/tag-webhook/        Edge Function: status da TAG -> vira item p/ graduado

docs/                                  arquitetura (md + svg), análise competitiva, plano
```

---

## CAMINHO A — Rodar AGORA (local, sem contas) ✅
Sobe o protótipo completo e gera uma URL HTTPS pública para teste imediato.

```bash
# 1) dependências
python3 -m pip install -r requirements.txt

# 2) iniciar o app (serve o front em http://localhost:5000)
python3 api.py
#   -> migra/seed automático no primeiro start

# 3) (em outro terminal) URL HTTPS pública, sem conta:
cloudflared tunnel --url http://localhost:5000
#   alternativa: ngrok http 5000
```
Pronto: abra a URL do túnel. Dá pra cadastrar, adicionar carta com foto, marcar pública/à venda,
e solicitar graduação (handoff para a TAG). Dados persistem em `pokemon_catalog.db`.

> Contas demo (senha `demo123`): raf10, marina.sp, joao_v, ana.bea, lucas_rs, tcg_bsb.

---

## CAMINHO B — PRODUÇÃO no Supabase 🚀
Segue o `SETUP-SUPABASE.md`. Resumo do que o agente faz × o que precisa do usuário:

### Precisa do USUÁRIO (pare e peça):
1. Criar projeto no Supabase (https://supabase.com).
2. Entregar 3 valores de **Project Settings → API**:
   - `SUPABASE_URL`
   - `SUPABASE_ANON_KEY` (pública — vai no front)
   - `SUPABASE_SERVICE_ROLE_KEY` (SECRETA — só em scripts/funções/CI; nunca no front nem no git)
3. (Opcional) `POKEMONTCG_API_KEY` e um `TAG_WEBHOOK_SECRET` à escolha.

### O agente faz (mecânico), nesta ordem:
```bash
# B1) Schema: cole supabase/schema_supabase.sql no SQL Editor do Supabase e rode.
#     (ou via psql, se tiver a connection string do projeto)

# B2) Migrar catálogo (na pasta do projeto, com a service_role do usuário):
export SUPABASE_URL="<do usuário>"
export SUPABASE_SERVICE_ROLE_KEY="<do usuário>"
python3 -m pip install requests
python3 supabase/migrate_catalog_to_supabase.py pokemon_catalog.db

# B3) Configurar o front: edite slabr-supabase.html, bloco CONFIG no topo do <script>:
#       url:  '<SUPABASE_URL>'
#       anon: '<SUPABASE_ANON_KEY>'
#     (só a anon key vai no front — a service_role NUNCA)

# B4) Hospedar o front: renomeie slabr-supabase.html -> index.html e publique
#     na Vercel/Netlify (deploy estático). Gera HTTPS + CDN.

# B5) Edge Functions:
npm i -g supabase
supabase login                              # interativo, do usuário
supabase link --project-ref <ref>
supabase secrets set SUPABASE_SERVICE_ROLE_KEY="..." POKEMONTCG_API_KEY="..." TAG_WEBHOOK_SECRET="..."
supabase functions deploy price-updater
supabase functions deploy tag-webhook

# B6) Agendar preços: cron diário batendo em price-updater por set (?set=base1, ...),
#     via pg_cron (net.http_get) ou cron externo. Ver SETUP-SUPABASE.md §7.
```

### Antes de testar (config do Supabase):
- Authentication → Providers → Email → **desligar "Confirm email"** enquanto testa
  (assim o cadastro já entra). Religue em produção.

### Smoke test (validar a implantação):
1. Abrir o site → Cadastrar (entra direto se a confirmação estiver desligada).
2. Adicionar carta → anexar foto → pública + à venda → salvar.
3. Conferir na biblioteca, na vitrine e no mercado (foto vinda do Storage).
4. Carta crua → "Graduar pela TAG Grading" → checklist → protocolo + abre site da TAG.
5. Reportar QUALQUER erro de console/Supabase para ajuste (o front de produção ainda não
   foi testado contra um projeto real).

---

## Regras de segurança (obrigatórias)
- `SUPABASE_SERVICE_ROLE_KEY` e `TAG_WEBHOOK_SECRET`: **nunca** no front, **nunca** no git.
  Use variáveis de ambiente / Supabase secrets.
- No front vai **somente** a `anon key` (é pública por design; o RLS protege os dados).
- Não criar contas em nome do usuário; não manipular senhas; pedir credenciais ao usuário.
- Não publicar/expor nada além do necessário para o deploy solicitado.
