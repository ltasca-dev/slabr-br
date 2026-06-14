#!/bin/bash

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║     SLABR - TUNNEL PUBLICO COM LOCALHOST.RUN                  ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

echo "[*] Conectando ao localhost.run..."
echo ""
echo "Instruções:"
echo "  1. Quando solicitado, pressione ENTER (ou digite 'yes')"
echo "  2. Uma URL será exibida em formato: https://XXXX.localhost.run"
echo "  3. Copie essa URL e compartilhe com qualquer pessoa"
echo "  4. Mantenha este terminal ABERTO"
echo ""
echo "Iniciando em 3 segundos..."
sleep 3

# Criar tunnel SSH
ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -R 80:localhost:5000 localhost.run

echo ""
echo "Tunnel encerrado."
