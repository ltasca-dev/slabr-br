#!/usr/bin/env python3
"""
SLABR Public Tunnel - Exponha o aplicativo publicamente via ngrok
Execute: python expose_slabr.py
"""

from pyngrok import ngrok
import time
import webbrowser

def main():
    print("\n" + "="*70)
    print("     SLABR - EXPONDO PUBLICAMENTE VIA NGROK")
    print("="*70)

    # Configurar ngrok
    ngrok.set_auth_token("")  # Deixe vazio para usar limite gratuito

    try:
        # Conectar localhost:5000 ao ngrok
        print("\n[*] Conectando ao ngrok...")
        public_url = ngrok.connect(5000, "http")

        print("\n" + "="*70)
        print("  [OK] SLABR ESTA EXPOSTO PUBLICAMENTE!")
        print("="*70)

        print(f"\n[URL PUBLICA] {public_url}")
        print(f"\n[COMPARTILHE COM USUARIOS]:")
        print(f"   {public_url}/home-public")

        print(f"\n[LINKS DIRETOS]:")
        print(f"   Marketplace:     {public_url}/marketplace")
        print(f"   Ranking Mensal:  {public_url}/ranking-mensal")
        print(f"   Guia de Lojas:   {public_url}/lojas")
        print(f"   Colecionadores:  {public_url}/colecionadores")

        print(f"\n[TEMPO ATIVO] Ate 2 horas (limite gratuito do ngrok)")
        print(f"   Para mais tempo, crie conta gratuita em https://ngrok.com")

        print("\n" + "="*70)
        print("  Tunnel ativo. Pressione Ctrl+C para desconectar.")
        print("="*70 + "\n")

        # Manter ativo
        while True:
            time.sleep(1)

    except Exception as e:
        print(f"\n[ERRO] Erro ao conectar ao ngrok: {e}")
        print("\nDica: Se estiver offline, crie conta gratuita em https://ngrok.com")
    finally:
        print("\n[*] Tunnel encerrado.")

if __name__ == "__main__":
    main()
