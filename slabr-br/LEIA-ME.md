# SLABR.br — app + API com contas (rodar localmente)

Protótipo conectado ao banco real (Flask + SQLite) com **contas de colecionador**:
cadastro/login com senha em hash, sessão por cookie, e visibilidade
**pública/privada de cada card gravada no banco**.

## Arquivos (manter na mesma pasta)
- `api.py` — backend: serve o app + endpoints `/api/...` + contas
- `slabr_app.html` — o app (front-end conectado à API)
- `pokemon_catalog.db` — catálogo (20.324 cartas) + biblioteca dos usuários + contas
- `ingest_catalog.py` — reconstrói o catálogo (opcional)

## Rodar
```bash
pip install flask --break-system-packages
python3 api.py
```
Abra **http://localhost:5000**.

## Contas demo (senha: `demo123`)
`raf10` · `marina.sp` · `joao_v` · `ana.bea` · `lucas_rs` · `tcg_bsb`
(ou crie a sua em "Criar conta")

## O que testar (fluxo de contas)
1. **Criar conta** no cabeçalho → cai no "Meu espaço".
2. **Adicionar carta** à biblioteca → escolha a carta, o estado, a quantidade, se é graduada, valor e se é pública.
3. **Meu espaço** → cada card tem o botão **Pública / Privada**.
   - Privada: some das ofertas e da vitrine pública; só você vê.
   - O estado **persiste no banco** (recarregar não perde).
4. **Sair** e entrar como outro usuário: você **não** consegue mexer
   na visibilidade do card alheio (a API recusa com 403).

## Segurança
- Senhas via `werkzeug` (hash, nunca texto puro).
- Defina um segredo de sessão em produção: `export SLABR_SECRET="algo-bem-aleatorio"`.

## Endpoints de contas
| Método | Rota | O que faz |
|---|---|---|
| POST | `/api/signup` | cria conta + inicia sessão |
| POST | `/api/login` | login por @usuário ou e-mail |
| POST | `/api/logout` | encerra sessão |
| GET | `/api/me` | usuário da sessão atual |
| GET | `/api/me/cards` | meus cards (inclui privados) |
| POST | `/api/graded/<cert>/visibility` | torna público/privado (só o dono) |

## O app agora é completo
Um arquivo só (`slabr_app.html`) com tudo conectado à API:
- **Início** — home de impacto (slab holográfico que inclina com o mouse), números reais e prévia do mercado.
- **Mercado** — feed real de itens públicos à venda (`/api/market`), do mais valioso ao mais barato.
- **Catálogo** — busca nas 20.324 cartas; mostra quantas já estão no acrílico.
- **Carta** — ofertas certificadas + Pop Report (escassez por nota).
- **Verificar** — confere um certificado (slab + subnotas + dono).
- **Adicionar carta** — salva uma carta na sua biblioteca (crua ou graduada), com estado/quantidade/valor e visibilidade.
- **Meu espaço** — suas cartas com o botão público/privado.
- **Entrar / Criar conta** — contas reais.

Demais endpoints (catálogo, ofertas, pop, ranking, vitrine, verificação,
mercado e criação de graduadas) respeitam a flag pública.

## Camada de preço de referência (novo)
A página da carta tem um painel **Mercado de preços**: estatísticas (raridade, número, à venda,
tendência, médias de 30/7/1 dias) + um **gráfico de histórico** de preço ao longo do tempo.
Os dados vêm das tabelas `card_prices` (preço atual) e `price_history` (série diária),
alimentadas por `update_prices.py`. Preço de referência internacional (US$/€), convertido p/ R$ como âncora.

Atualizar (na sua máquina, com internet):
```bash
python3 update_prices.py            # atualiza as cartas que estão no mercado
python3 update_prices.py --limit 200
POKEMONTCG_API_KEY=suachave python3 update_prices.py   # eleva o rate limit
```
Sem internet (ver a feature funcionando): `python3 update_prices.py --demo`

Agendar (cron diário, ex.):
```
0 6 * * *  cd /caminho/slabr && python3 update_prices.py >> prices.log 2>&1
```
Câmbio âncora: `SLABR_USD_BRL` (padrão 5.40) e `SLABR_EUR_BRL` (padrão 5.90).

> Atenção: é REFERÊNCIA internacional, não preço de venda no Brasil. Antes de usar uma
> fonte num produto comercial, confira a licença/termos dela (a TCGplayer, p.ex., restringe).
> O ativo de verdade é o nosso próprio histórico de vendas graduadas em R$.

## Onde roda / acesso em notebook, PC e celular
O app é **web puro** (HTML/CSS/JS) — roda em qualquer navegador moderno, em qualquer sistema
(Windows, Mac, Linux, Android, iPhone). Não instala nada no aparelho. O layout é responsivo:
no celular o menu vira um botão ☰ e o slab holográfico responde ao toque.

- **No mesmo computador:** `python3 api.py` e abra `http://localhost:5000`.
- **No celular (mesma rede Wi-Fi):**
  ```bash
  SLABR_HOST=0.0.0.0 python3 api.py
  ```
  O terminal mostra o endereço (ex.: `http://192.168.0.12:5000`) — abra esse no navegador do celular.
  (Ao expor na rede, o modo debug é desligado automaticamente por segurança.)
- **Acesso de qualquer lugar (link público):** para um teste rápido, um túnel (ngrok/cloudflared)
  dá um endereço temporário. Para valer, é hospedar num servidor com domínio (deploy de verdade).

Porta também é ajustável: `SLABR_PORT=8080 python3 api.py`.

## Hospedar de graça (para testar)
O app grava num SQLite, então o ponto-chave é se o disco do serviço é persistente.

**Opção A — PythonAnywhere (free): disco persistente, dados do teste sobrevivem.**
Suba os arquivos, crie um virtualenv com `pip install -r requirements.txt`, configure o WSGI
apontando para `api:app`. Obs.: a internet de saída no free é limitada — rode `update_prices.py`
na sua máquina (ou use `--demo`).

**Opção B — Render (free): link HTTPS via GitHub. Disco efêmero (SQLite volta ao seed em cada restart).**
- Build Command: `pip install -r requirements.txt`
- Start Command: `gunicorn api:app --bind 0.0.0.0:$PORT`
- Variáveis: `SLABR_SECRET` (obrigatória em produção). Dorme após inatividade (cold start ~30s).

**Opção C — Túnel da sua máquina (mostrar agora, dados persistem no seu PC):**
```bash
python3 api.py            # roda local
# em outro terminal, um destes:
cloudflared tunnel --url http://localhost:5000
# ou:  ngrok http 5000
```

Arquivos de deploy já incluídos: `requirements.txt` e `Procfile`
(`web: gunicorn api:app --bind 0.0.0.0:$PORT`). A API lê a porta de `$PORT` automaticamente e
roda a migração do banco no boot, então funciona igual local e hospedado.

> Para qualquer host público, defina `SLABR_SECRET` e lembre que o disco efêmero apaga
> cadastros/cartas no restart. Quando o teste virar sério, migramos o SQLite para um Postgres.
