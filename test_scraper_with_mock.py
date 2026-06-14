#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste do scraper com fallback mock
Verifica que a integração funciona end-to-end
"""

import sys
import time
import io

# Fix para Windows encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from scraper_bynx import BynxScraperSync

# 10 cartas para teste rápido
TEST_CARDS = [
    ('pikachu', 'base1-25'),
    ('charizard', 'base1-4'),
    ('blastoise', 'base1-2'),
    ('venusaur', 'base1-3'),
    ('alakazam', 'base1-1'),
    ('mewtwo', 'base1-10'),
    ('machamp', 'base1-11'),
    ('zapdos', 'base1-12'),
    ('moltres', 'base1-13'),
    ('articuno', 'base1-14'),
]

def main():
    print("=" * 70)
    print("TESTE DO SCRAPER COM FALLBACK MOCK")
    print("=" * 70)

    scraper = BynxScraperSync()
    results = {'success': 0, 'mock': 0, 'failed': 0}
    prices = []

    start_time = time.time()

    for idx, (card_name, set_id) in enumerate(TEST_CARDS, 1):
        print(f"\n[{idx:2d}/10] Testando: {card_name:15s} ({set_id})")
        try:
            card_data = scraper.search_card(card_name, set_id, use_mock_fallback=True)
            if card_data:
                is_mock = card_data.get('is_mock', False)
                price = card_data.get('price_brl', 'N/A')
                source = "MOCK" if is_mock else "REAL"

                print(f"      [OK] {source:4s} - R$ {price}")

                if is_mock:
                    results['mock'] += 1
                else:
                    results['success'] += 1

                prices.append({
                    'name': card_name,
                    'price': price,
                    'source': source
                })
            else:
                print(f"      [FALHA] Preço não encontrado")
                results['failed'] += 1
        except Exception as e:
            print(f"      [ERRO] {str(e)[:50]}")
            results['failed'] += 1

    elapsed = time.time() - start_time

    print("\n" + "=" * 70)
    print("RESUMO DOS RESULTADOS")
    print("=" * 70)
    total = results['success'] + results['mock'] + results['failed']
    print(f"Total de testes:    {total}")
    print(f"Sucessos (real):    {results['success']}")
    print(f"Sucessos (mock):    {results['mock']}")
    print(f"Falhas:             {results['failed']}")
    success_rate = ((results['success'] + results['mock']) / total) * 100
    print(f"Taxa de sucesso:    {success_rate:.1f}%")
    print(f"Tempo total:        {elapsed:.1f}s")
    print(f"Tempo por carta:    {elapsed/total:.2f}s")

    print("\nPrecos obtidos:")
    for p in prices:
        print(f"  {p['name']:15s}: R$ {p['price']:8.2f} [{p['source']}]")

    print("=" * 70)

    if success_rate >= 50:
        print(f"\nSUCESO: Taxa acima de 50% ({success_rate:.1f}%)")
        print("Integração pronta para Fase 1")
        return 0
    else:
        print(f"\nERRO: Taxa baixa ({success_rate:.1f}%)")
        return 1

if __name__ == '__main__':
    sys.exit(main())
