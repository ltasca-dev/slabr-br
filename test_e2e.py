#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Testes E2E - Validar fluxos completos
Execute: python test_e2e.py
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:5000"
USER_ID = "leonardo"

class Colors:
    GREEN = ''
    RED = ''
    YELLOW = ''
    BLUE = ''
    END = ''

def log_test(name, status):
    symbol = "[OK]" if status else "[FAIL]"
    print(f"{symbol} {name}")

def log_section(name):
    print(f"\n{'='*50}")
    print(f"{name}")
    print(f"{'='*50}\n")

# ============================================================================
# FASE 0: Bynx Price Integration
# ============================================================================

def test_fase0():
    log_section("TESTE FASE 0: Bynx Price Integration")

    # Test 1: Health check
    try:
        response = requests.get(f"{BASE_URL}/api/prices/bynx/health")
        log_test("Health check", response.status_code == 200)
    except:
        log_test("Health check", False)

    # Test 2: Get price
    try:
        response = requests.get(f"{BASE_URL}/api/prices/bynx/base1-4")
        data = response.json()
        success = data.get('status') == 'success' and data.get('price_brl')
        log_test("Get Charizard price", success)
    except:
        log_test("Get Charizard price", False)

    print()

# ============================================================================
# FASE 1: Portfolio Manager
# ============================================================================

def test_portfolio():
    log_section("TESTE FASE 1: Portfolio Manager")

    # Test 1: Add card
    try:
        response = requests.post(
            f"{BASE_URL}/api/portfolio/collections",
            json={
                "user_id": USER_ID,
                "card_id": "base1-25",
                "card_name": "Pikachu",
                "purchase_price": 150.00,
                "quantity": 1,
                "condition": "NM"
            }
        )
        success = response.status_code == 201
        log_test("Add Pikachu to collection", success)
        collection_id = response.json().get('id') if success else None
    except Exception as e:
        log_test("Add Pikachu to collection", False)
        collection_id = None

    # Test 2: Get collections
    try:
        response = requests.get(f"{BASE_URL}/api/portfolio/collections/{USER_ID}")
        data = response.json()
        success = data.get('status') == 'success' and data.get('count', 0) > 0
        log_test("Get user collections", success)
    except:
        log_test("Get user collections", False)

    # Test 3: Get portfolio stats
    try:
        response = requests.get(f"{BASE_URL}/api/portfolio/stats/{USER_ID}")
        data = response.json()
        success = data.get('status') == 'success'
        log_test("Get portfolio statistics", success)
    except:
        log_test("Get portfolio statistics", False)

    # Test 4: Create price alert
    try:
        response = requests.post(
            f"{BASE_URL}/api/portfolio/alerts",
            json={
                "user_id": USER_ID,
                "card_id": "base1-4",
                "card_name": "Charizard",
                "threshold_price": 600.00,
                "alert_type": "up"
            }
        )
        success = response.status_code == 201
        log_test("Create price alert", success)
    except:
        log_test("Create price alert", False)

    print()

# ============================================================================
# FASE 1: Marketplace
# ============================================================================

def test_marketplace():
    log_section("TESTE FASE 1: Marketplace")

    # Test 1: Create listing
    try:
        response = requests.post(
            f"{BASE_URL}/api/marketplace/listings",
            json={
                "seller_id": USER_ID,
                "card_id": "base1-6",
                "card_name": "Gyarados",
                "quantity": 1,
                "price": 450.00,
                "condition": "NM",
                "listing_type": "sale"
            }
        )
        success = response.status_code == 201
        log_test("Create marketplace listing", success)
        listing_id = response.json().get('id') if success else None
    except Exception as e:
        log_test("Create marketplace listing", False)
        listing_id = None

    # Test 2: Get listings
    try:
        response = requests.get(f"{BASE_URL}/api/marketplace/listings")
        data = response.json()
        success = data.get('status') == 'success'
        log_test("Get marketplace listings", success)
    except:
        log_test("Get marketplace listings", False)

    # Test 3: Get trending
    try:
        response = requests.get(f"{BASE_URL}/api/marketplace/trending")
        data = response.json()
        success = data.get('status') == 'success'
        log_test("Get trending cards", success)
    except:
        log_test("Get trending cards", False)

    # Test 4: Get deals
    try:
        response = requests.get(f"{BASE_URL}/api/marketplace/deals")
        data = response.json()
        success = data.get('status') == 'success'
        log_test("Get best deals", success)
    except:
        log_test("Get best deals", False)

    print()

# ============================================================================
# FASE 1: Bynx Sync
# ============================================================================

def test_bynx_sync():
    log_section("TESTE FASE 1: Bynx Sync")

    # Test 1: Check sync status
    try:
        response = requests.get(f"{BASE_URL}/api/bynx-sync/status/{USER_ID}")
        data = response.json()
        success = data.get('status') == 'not_connected'
        log_test("Check Bynx sync status", success)
    except:
        log_test("Check Bynx sync status", False)

    # Test 2: Connect to Bynx
    try:
        response = requests.post(
            f"{BASE_URL}/api/bynx-sync/connect",
            json={"user_id": USER_ID}
        )
        data = response.json()
        success = data.get('status') == 'success' and 'oauth_url' in data
        log_test("Get Bynx OAuth URL", success)
    except:
        log_test("Get Bynx OAuth URL", False)

    print()

# ============================================================================
# PERFORMANCE TESTS
# ============================================================================

def test_performance():
    log_section("TESTE DE PERFORMANCE")

    # Test 1: Response time - Get price
    try:
        start = time.time()
        requests.get(f"{BASE_URL}/api/prices/bynx/base1-4")
        elapsed = (time.time() - start) * 1000
        success = elapsed < 500
        log_test(f"Get price response time: {elapsed:.0f}ms", success)
    except:
        log_test("Get price response time", False)

    # Test 2: Response time - Get portfolio
    try:
        start = time.time()
        requests.get(f"{BASE_URL}/api/portfolio/collections/{USER_ID}")
        elapsed = (time.time() - start) * 1000
        success = elapsed < 500
        log_test(f"Get portfolio response time: {elapsed:.0f}ms", success)
    except:
        log_test("Get portfolio response time", False)

    # Test 3: Response time - Get marketplace
    try:
        start = time.time()
        requests.get(f"{BASE_URL}/api/marketplace/listings")
        elapsed = (time.time() - start) * 1000
        success = elapsed < 500
        log_test(f"Get marketplace response time: {elapsed:.0f}ms", success)
    except:
        log_test("Get marketplace response time", False)

    print()

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    print(f"\nIniciando Testes E2E")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    try:
        test_fase0()
        test_portfolio()
        test_marketplace()
        test_bynx_sync()
        test_performance()

        log_section("RESUMO")
        print(f"Todos os testes foram executados!")
        print(f"\nEndpoints testados:")
        print(f"  • Fase 0: 2 endpoints")
        print(f"  • Portfolio: 4 endpoints")
        print(f"  • Marketplace: 4 endpoints")
        print(f"  • Bynx Sync: 2 endpoints")
        print(f"  • Performance: 3 endpoints\n")

    except Exception as e:
        print(f"\nErro durante testes: {e}")
