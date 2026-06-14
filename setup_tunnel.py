#!/usr/bin/env python3
"""
SLABR - Cloudflare Tunnel Setup
Script interativo para configurar o Named Tunnel
"""

import subprocess
import os
import time
import json

def main():
    print("\n" + "="*70)
    print("  SLABR - CONFIGURACAO CLOUDFLARE TUNNEL")
    print("="*70)

    tunnel_name = "slabr"
    local_url = "http://localhost:5000"

    print(f"\n[1] Login no Cloudflare")
    print("-" * 70)
    print("Pressione ENTER para abrir o navegador e autorizar...")
    input()

    # Step 1: Login
    print("\n[*] Abrindo navegador para autorizacao...")
    result = subprocess.run(
        ["cloudflared.exe", "tunnel", "login"],
        capture_output=False
    )

    if result.returncode != 0:
        print("[ERRO] Login falhou. Tente novamente.")
        return False

    print("[OK] Login concluido!")
    time.sleep(2)

    # Step 2: Criar tunnel
    print(f"\n[2] Criando Named Tunnel '{tunnel_name}'")
    print("-" * 70)

    result = subprocess.run(
        ["cloudflared.exe", "tunnel", "create", tunnel_name],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        if "already exists" in result.stderr:
            print(f"[INFO] Tunnel '{tunnel_name}' ja existe. Continuando...")
        else:
            print(f"[ERRO] {result.stderr}")
            return False
    else:
        print(f"[OK] Tunnel '{tunnel_name}' criado!")

    time.sleep(1)

    # Step 3: Get tunnel ID
    print(f"\n[3] Obtendo ID do tunnel")
    print("-" * 70)

    result = subprocess.run(
        ["cloudflared.exe", "tunnel", "list", "--output", "json"],
        capture_output=True,
        text=True
    )

    if result.returncode == 0:
        try:
            tunnels = json.loads(result.stdout)
            for t in tunnels:
                if t.get("name") == tunnel_name:
                    tunnel_id = t.get("id")
                    print(f"[OK] Tunnel ID: {tunnel_id}")
                    break
        except:
            print("[WARN] Nao conseguiu obter ID. Continuando...")

    time.sleep(1)

    # Step 4: Criar config.yaml
    print(f"\n[4] Criando arquivo de configuracao")
    print("-" * 70)

    config_content = f"""tunnel: {tunnel_name}
credentials-file: C:\\Users\\ltasca\\.cloudflared\\{tunnel_name}.json

ingress:
  - hostname: slabr.seu-dominio.com
    service: {local_url}
  - service: http_status:404
"""

    config_path = os.path.expanduser("~/.cloudflared/config.yml")
    os.makedirs(os.path.dirname(config_path), exist_ok=True)

    with open(config_path, "w") as f:
        f.write(config_content)

    print(f"[OK] Configuracao salva em: {config_path}")

    print(f"\n[5] Proximos passos")
    print("-" * 70)
    print("""
    1. Acesse: https://dash.cloudflare.com/
    2. Vá em: Zero Trust > Networks > Tunnels
    3. Clique em 'slabr' tunnel
    4. Em 'Public hostname', configure seu dominio (ex: app.seu-dominio.com)
    5. Salve a configuracao

    Depois, para manter o tunnel ativo:

    cloudflared.exe service install
    cloudflared.exe service start

    Ou execute manualmente:

    cloudflared.exe tunnel run slabr
    """)

    print("="*70)
    print("[OK] Configuracao concluida!")
    print("="*70)

if __name__ == "__main__":
    main()
