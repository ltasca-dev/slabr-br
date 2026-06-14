#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Servidor HTTP melhorado para SLABR 2.0"""

from http.server import HTTPServer, SimpleHTTPRequestHandler
import os
import json
import sys

class SLABRHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        # Mapear rotas para arquivos
        route_map = {
            '/': 'home.html',
            '/home': 'home.html',
            '/app': 'app.html',
            '/slabr': 'slabr_complete.html',
            '/dashboard': 'slabr_complete.html',
            '/index.html': 'home.html',
        }

        # Verificar rotas especiais
        if self.path in route_map:
            file_path = route_map[self.path]
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.send_response(200)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                content_bytes = content.encode('utf-8')
                self.send_header('Content-Length', len(content_bytes))
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Cache-Control', 'no-cache')
                self.end_headers()
                self.wfile.write(content_bytes)
                return
            except Exception as e:
                sys.stderr.write(f"Erro ao servir {file_path}: {e}\n")

        # API health check
        if self.path == '/api/prices/bynx/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({'status': 'healthy', 'scraper': 'online', 'test': 'OK'}).encode())
            return

        # Servir arquivos normais
        return super().do_GET()

    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Cache-Control', 'no-cache')
        super().end_headers()

if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    server = HTTPServer(('0.0.0.0', 5000), SLABRHandler)
    print("=" * 70)
    print("SLABR 2.0 - Complete Server")
    print("=" * 70)
    print("\nAcesso local:")
    print("  > http://localhost:5000              (Home)")
    print("  > http://localhost:5000/app          (App Original)")
    print("  > http://localhost:5000/slabr        (SLABR COMPLETE - NOVO)")
    print("  > http://localhost:5000/dashboard    (Dashboard)")
    print("\nPressione CTRL+C para parar\n")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\nServidor parado.")
        server.server_close()
