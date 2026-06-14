# Prompt para o agente — publicar o SLABR.br com link HTTPS (Cloudflare Tunnel)

Você é um agente com acesso ao terminal da minha máquina. Sua tarefa é instalar as
dependências, subir o app web "SLABR.br" localmente e expô-lo num link HTTPS público
temporário usando o Cloudflare Tunnel (quick tunnel, que NÃO exige conta nem login).
Trabalhe de forma incremental, verificando cada passo antes de seguir, e me mostrando os
comandos antes de executar os que exigem privilégios de administrador.

## Contexto
Tenho uma pasta com estes arquivos (peça o caminho se não souber qual é):
- `api.py` — servidor Flask (serve o app e a API)
- `slabr_app.html` — o front-end
- `pokemon_catalog.db` — banco SQLite (catálogo + contas + cartas)
- `requirements.txt` — dependências (Flask, gunicorn)
- `Procfile` — comando de produção (não obrigatório para rodar local)
- `update_prices.py` — atualizador de preços (opcional, não precisa rodar agora)

O app é Python 3 + Flask. Ao rodar `python3 api.py` ele sobe em `http://localhost:5000`,
faz a migração do banco sozinho e serve a página inicial.

## Regras importantes
- NÃO crie conta na Cloudflare nem peça login: use o "quick tunnel"
  (`cloudflared tunnel --url ...`), que gera uma URL `https://*.trycloudflare.com` sem cadastro.
- NÃO digite senhas, tokens ou dados de cartão em lugar nenhum.
- Antes de qualquer comando com `sudo`/admin, me mostre o comando e peça confirmação.
- Não apague nem mova meus arquivos. Use um ambiente virtual (venv) para não bagunçar o
  Python do sistema.
- Detecte meu sistema operacional e use o método de instalação correto.

## Passos

1. **Localizar os arquivos.** Verifique se a pasta atual contém `api.py`, `slabr_app.html`,
   `pokemon_catalog.db` e `requirements.txt`. Se não, me pergunte o caminho e use `cd` para entrar.

2. **Python e ambiente.** Confirme que há Python 3.9+ (`python3 --version`). Crie e ative um
   venv na pasta:
   - macOS/Linux: `python3 -m venv .venv && source .venv/bin/activate`
   - Windows (PowerShell): `python -m venv .venv ; .\.venv\Scripts\Activate.ps1`
   Instale as dependências: `pip install -r requirements.txt`.

3. **Definir um segredo de sessão** (qualquer string aleatória):
   - macOS/Linux: `export SLABR_SECRET="$(python3 -c 'import secrets;print(secrets.token_hex(16))')"`
   - Windows (PowerShell): `$env:SLABR_SECRET = (python -c "import secrets;print(secrets.token_hex(16))")`

4. **Subir o app em segundo plano** e verificar:
   - Rode `python3 api.py` em background (em outro terminal/processo).
   - Aguarde ~3s e teste: `curl -s -o /dev/null -w "%{http_code}" http://localhost:5000/`
   - O resultado deve ser `200`. Se não for, leia o log do app e corrija (porta ocupada → use
     `SLABR_PORT=5001 python3 api.py` e ajuste a URL nos próximos passos).

5. **Instalar o cloudflared** (se ainda não tiver — teste com `cloudflared --version`):
   - macOS: `brew install cloudflared`
   - Windows: `winget install --id Cloudflare.cloudflared` (ou `choco install cloudflared`)
   - Linux (Debian/Ubuntu): baixe o binário oficial mais recente de
     `https://github.com/cloudflare/cloudflared/releases/latest`
     (arquivo `cloudflared-linux-amd64` para x86_64 ou `cloudflared-linux-arm64` para ARM),
     dê `chmod +x` e mova para um diretório do PATH.
   Confirme a instalação com `cloudflared --version`.

6. **Abrir o túnel HTTPS:**
   `cloudflared tunnel --url http://localhost:5000`
   Esse comando imprime uma linha com a URL pública no formato
   `https://<algo-aleatorio>.trycloudflare.com`. **Capture exatamente essa URL.**

7. **Validar de ponta a ponta:** faça um `curl -s -o /dev/null -w "%{http_code}"` na URL
   `https://<...>.trycloudflare.com/` e confirme que retorna `200`.

## Entregue no final
- A **URL HTTPS pública** em destaque (é o link que vou compartilhar e abrir no celular).
- Aviso de que o link funciona enquanto os dois processos (app + cloudflared) estiverem rodando;
  se eu fechar o terminal, o link cai (e os dados continuam salvos no `pokemon_catalog.db` local).
- Como parar tudo (encerrar os dois processos) e como subir de novo quando eu quiser.
- Conta de teste já existente: usuário `raf10`, senha `demo123` (ou criar conta nova no app).
