#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Load Test - Simular multiplas requisicoes
Execute: python test_load.py
"""

import requests
import time
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE_URL = "http://localhost:5000"
NUM_REQUESTS = 50
NUM_THREADS = 10

def make_request(endpoint, request_num):
    """Fazer uma requisicao e retornar tempo de resposta"""
    try:
        start = time.time()
        response = requests.get(f"{BASE_URL}{endpoint}", timeout=10)
        elapsed = (time.time() - start) * 1000
        return {
            'request': request_num,
            'endpoint': endpoint,
            'status': response.status_code,
            'time_ms': elapsed,
            'success': response.status_code == 200
        }
    except Exception as e:
        return {
            'request': request_num,
            'endpoint': endpoint,
            'status': 0,
            'time_ms': 0,
            'success': False,
            'error': str(e)
        }

def run_load_test():
    print("\n" + "="*50)
    print("LOAD TEST - 50 requisicoes com 10 threads")
    print("="*50 + "\n")

    endpoints = [
        "/api/prices/bynx/health",
        "/api/portfolio/collections/leonardo",
        "/api/marketplace/listings",
        "/api/bynx-sync/status/leonardo"
    ]

    all_results = []
    results_by_endpoint = {}

    with ThreadPoolExecutor(max_workers=NUM_THREADS) as executor:
        futures = []

        # Submeter requisicoes
        for i in range(NUM_REQUESTS):
            endpoint = endpoints[i % len(endpoints)]
            future = executor.submit(make_request, endpoint, i + 1)
            futures.append(future)

        # Coletar resultados
        for future in as_completed(futures):
            result = future.result()
            all_results.append(result)

            endpoint = result['endpoint']
            if endpoint not in results_by_endpoint:
                results_by_endpoint[endpoint] = []
            results_by_endpoint[endpoint].append(result)

    # Analise por endpoint
    print("\nResultados por Endpoint:")
    print("-" * 50)

    total_time = 0
    total_success = 0

    for endpoint in endpoints:
        if endpoint in results_by_endpoint:
            results = results_by_endpoint[endpoint]
            times = [r['time_ms'] for r in results if r['success']]
            success_count = sum(1 for r in results if r['success'])

            if times:
                avg_time = statistics.mean(times)
                min_time = min(times)
                max_time = max(times)
                total_time += sum(times)
                total_success += success_count

                print(f"\n{endpoint}")
                print(f"  Requisicoes: {len(results)}")
                print(f"  Sucesso: {success_count}/{len(results)}")
                print(f"  Tempo medio: {avg_time:.0f}ms")
                print(f"  Min/Max: {min_time:.0f}ms / {max_time:.0f}ms")

    # Resumo geral
    print("\n" + "="*50)
    print("RESUMO GERAL")
    print("="*50)

    total_requests = len(all_results)
    success_rate = (total_success / total_requests * 100) if total_requests > 0 else 0
    avg_time = (total_time / total_success) if total_success > 0 else 0

    print(f"Total de requisicoes: {total_requests}")
    print(f"Sucessos: {total_success}")
    print(f"Taxa de sucesso: {success_rate:.1f}%")
    print(f"Tempo medio global: {avg_time:.0f}ms")

    if success_rate >= 95:
        print("\n[OK] Load test PASSOU - Sistema aguenta carga")
    elif success_rate >= 80:
        print("\n[AVISO] Load test com limitacoes - Revisar performance")
    else:
        print("\n[FAIL] Load test FALHOU - Otimizar antes de deploy")

    print()

if __name__ == "__main__":
    run_load_test()
