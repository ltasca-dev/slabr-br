#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste rápido do scraper com 20 cartas conhecidas
Taxa de sucesso e performance
"""

import sys
import time
import io

# Fix para Windows encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from scraper_bynx import BynxScraperSync

# 20 cartas conhecidas para teste
TEST_CARDS = [
    ('pikachu', 'base1-25'),
    ('charizard', 'base1-4'),
    ('blastoise', 'base1-2'),
    ('venusaur', 'base1-3'),
    ('machamp', 'base1-11'),
    ('gyarados', 'base1-6'),
    ('alakazam', 'base1-1'),
    ('arcanine', 'base1-19'),
    ('golem', 'base1-35'),
    ('lapras', 'base1-16'),
    ('dragonite', 'fossil-5'),
    ('mewtwo', 'base1-10'),
    ('zapdos', 'base1-12'),
    ('articuno', 'base1-14'),
    ('moltres', 'base1-13'),
    ('raichu', 'base1-24'),
    ('gengar', 'base1-34'),
    ('hypno', 'base1-36'),
    ('wigglytuff', 'base1-32'),
    ('jynx', 'base1-31'),
]

def main():
    print("=" * 60)
    print("TESTE SCRAPER BYNX.GG - 20 CARTAS")
    print("=" * 60)

    scraper = BynxScraperSync()
    results = {
        'success': 0,
        'failed': 0,
        'errors': []
    }

    start_time = time.time()

    for idx, (card_name, set_id) in enumerate(TEST_CARDS, 1):
        print(f"\n[{idx:2d}/20] Testando: {card_name:15s} ({set_id})")
        try:
            card_data = scraper.search_card(card_name, set_id)
            if card_data:
                print(f"      ✓ SUCESSO - R$ {card_data.get('price_brl', 'N/A')}")
                results['success'] += 1
            else:
                print(f"      ✗ FALHOU - Carta não encontrada")
                results['failed'] += 1
                results['errors'].append((card_name, "Não encontrada"))
        except Exception as e:
            print(f"      ✗ ERRO - {str(e)[:50]}")
            results['failed'] += 1
            results['errors'].append((card_name, str(e)[:50]))

    elapsed = time.time() - start_time

    print("\n" + "=" * 60)
    print("RESUMO DOS RESULTADOS")
    print("=" * 60)
    print(f"Total de testes:  {results['success'] + results['failed']}")
    print(f"Sucessos:         {results['success']}")
    print(f"Falhas:           {results['failed']}")
    success_rate = (results['success'] / (results['success'] + results['failed'])) * 100
    print(f"Taxa de sucesso:  {success_rate:.1f}%")
    print(f"Tempo total:      {elapsed:.1f}s")
    print(f"Tempo por carta:  {elapsed/(results['success']+results['failed']):.2f}s")

    if results['errors']:
        print("\nErros encontrados:")
        for card_name, error in results['errors'][:5]:
            print(f"  - {card_name}: {error}")

    print("=" * 60)

    # Recomendação
    if success_rate >= 50:
        print(f"\n✓ RECOMENDAÇÃO: Taxa acima de 50% ({success_rate:.1f}%)")
        print("  Continuar com fallback mockado para problemas")
        return 0
    else:
        print(f"\n✗ RECOMENDAÇÃO: Taxa baixa ({success_rate:.1f}%)")
        print("  Usar cache mockado para todas as cartas")
        return 1

if __name__ == '__main__':
    sys.exit(main())
