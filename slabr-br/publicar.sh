#!/usr/bin/env bash
# Sobe o SLABR.br e publica um link HTTPS temporário (Cloudflare Tunnel ou ngrok).
# Uso:  bash publicar.sh
cd "$(dirname "$0")" || exit 1
export SLABR_SECRET="${SLABR_SECRET:-mude-este-segredo-aleatorio}"

echo "→ instalando dependências..."
python3 -m pip install -r requirements.txt --quiet 2>/dev/null || pip install -r requirements.txt --quiet

echo "→ subindo o app em http://localhost:5000 ..."
python3 api.py > slabr.log 2>&1 &
APP=$!
sleep 3
cleanup(){ kill "$APP" 2>/dev/null; }
trap cleanup EXIT

if command -v cloudflared >/dev/null 2>&1; then
  echo "→ abrindo túnel HTTPS (cloudflared)."
  echo "  O link público aparece abaixo, no formato https://XXXX.trycloudflare.com"
  cloudflared tunnel --url http://localhost:5000
elif command -v ngrok >/dev/null 2>&1; then
  echo "→ abrindo túnel HTTPS (ngrok). Veja a linha 'Forwarding https://...'"
  ngrok http 5000
else
  echo
  echo "!! Falta instalar um túnel. Escolha um (uma vez só):"
  echo "   Mac:     brew install cloudflared"
  echo "   Windows: winget install --id Cloudflare.cloudflared"
  echo "   Linux:   baixe o binário em https://github.com/cloudflare/cloudflared/releases/latest"
  echo "   (alternativa: ngrok — https://ngrok.com/download)"
  echo "Depois rode de novo: bash publicar.sh"
fi
