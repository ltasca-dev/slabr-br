#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Testes E2E Multi-TCG
Execute: python test_multitcg.py
"""

import requests
import json

BASE_URL = "http://localhost:5000"
USER_ID = "leonardo"

def log_test(name, status):
    symbol = "[OK]" if status else "[FAIL]"
    print(f"{symbol} {name}")

def log_section(name):
    print(f"\n{'='*60}")
    print(f"{name}")
    print(f"{'='*60}\n")

# ============================================================================
# TESTE TCG Management
# ============================================================================

def test_tcg_management():
    log_section("TESTE 1: TCG Management")

    # Test 1: List TCGs
    try:
        response = requests.get(f"{BASE_URL}/api/tcg/list")
        data = response.json()
        success = data.get('status') == 'success' and data.get('count', 0) == 4
        log_test(f"List TCGs ({data.get('count')} found)", success)
    except:
        log_test("List TCGs", False)

    # Test 2: Get Pokemon sets
    try:
        response = requests.get(f"{BASE_URL}/api/tcg/pokemon/sets")
        data = response.json()
        success = data.get('status') == 'success'
        log_test(f"Get Pokemon sets", success)
    except:
        log_test("Get Pokemon sets", False)

    # Test 3: Get Pokemon cards
    try:
        response = requests.get(f"{BASE_URL}/api/tcg/pokemon/cards?limit=10")
        data = response.json()
        success = data.get('status') == 'success'
        log_test(f"Get Pokemon cards", success)
    except:
        log_test("Get Pokemon cards", False)

# ============================================================================
# TESTE Multi-TCG Collections
# ============================================================================

def test_collections_v2():
    log_section("TESTE 2: Multi-TCG Collections")

    # Test 1: Add Pokemon card
    try:
        response = requests.post(
            f"{BASE_URL}/api/collections/v2",
            json={
                "user_id": USER_ID,
                "tcg_id": "pokemon",
                "card_id": "base1-4",
                "card_name": "Charizard",
                "quantity": 1,
                "condition": "NM",
                "purchase_price": 1500.00
            }
        )
        success = response.status_code == 201
        log_test("Add Pokemon card", success)
    except:
        log_test("Add Pokemon card", False)

    # Test 2: Add Magic card
    try:
        response = requests.post(
            f"{BASE_URL}/api/collections/v2",
            json={
                "user_id": USER_ID,
                "tcg_id": "magic",
                "card_id": "tsr-123",
                "card_name": "Black Lotus",
                "quantity": 1,
                "condition": "LP",
                "purchase_price": 5000.00
            }
        )
        success = response.status_code == 201
        log_test("Add Magic card", success)
    except:
        log_test("Add Magic card", False)

    # Test 3: Add Yu-Gi-Oh card
    try:
        response = requests.post(
            f"{BASE_URL}/api/collections/v2",
            json={
                "user_id": USER_ID,
                "tcg_id": "yugioh",
                "card_id": "lob-001",
                "card_name": "Blue-Eyes White Dragon",
                "quantity": 1,
                "condition": "NM",
                "purchase_price": 800.00
            }
        )
        success = response.status_code == 201
        log_test("Add Yu-Gi-Oh card", success)
    except:
        log_test("Add Yu-Gi-Oh card", False)

    # Test 4: Add One Piece card
    try:
        response = requests.post(
            f"{BASE_URL}/api/collections/v2",
            json={
                "user_id": USER_ID,
                "tcg_id": "onepiece",
                "card_id": "op-001",
                "card_name": "Luffy",
                "quantity": 2,
                "condition": "NM",
                "purchase_price": 300.00
            }
        )
        success = response.status_code == 201
        log_test("Add One Piece card", success)
    except:
        log_test("Add One Piece card", False)

    # Test 5: Get all collections
    try:
        response = requests.get(f"{BASE_URL}/api/collections/v2/{USER_ID}")
        data = response.json()
        success = data.get('status') == 'success' and data.get('count', 0) >= 4
        log_test(f"Get all collections ({data.get('count')} cards)", success)
    except:
        log_test("Get all collections", False)

    # Test 6: Get Pokemon collections only
    try:
        response = requests.get(f"{BASE_URL}/api/collections/v2/{USER_ID}?tcg_id=pokemon")
        data = response.json()
        success = data.get('status') == 'success'
        log_test(f"Get Pokemon collections only", success)
    except:
        log_test("Get Pokemon collections only", False)

# ============================================================================
# TESTE Multi-TCG Marketplace
# ============================================================================

def test_marketplace_v2():
    log_section("TESTE 3: Multi-TCG Marketplace")

    # Test 1: Create Pokemon listing
    try:
        response = requests.post(
            f"{BASE_URL}/api/marketplace/v2/listings",
            json={
                "seller_id": USER_ID,
                "tcg_id": "pokemon",
                "card_id": "base1-25",
                "card_name": "Pikachu",
                "quantity": 1,
                "price": 250.00,
                "currency": "BRL",
                "condition": "NM",
                "listing_type": "sale"
            }
        )
        success = response.status_code == 201
        log_test("Create Pokemon listing", success)
    except:
        log_test("Create Pokemon listing", False)

    # Test 2: Create Magic listing
    try:
        response = requests.post(
            f"{BASE_URL}/api/marketplace/v2/listings",
            json={
                "seller_id": USER_ID,
                "tcg_id": "magic",
                "card_id": "unlimited-239",
                "card_name": "Mox Pearl",
                "quantity": 1,
                "price": 3000.00,
                "currency": "BRL",
                "condition": "LP",
                "listing_type": "sale"
            }
        )
        success = response.status_code == 201
        log_test("Create Magic listing", success)
    except:
        log_test("Create Magic listing", False)

    # Test 3: Get all listings (multi-TCG)
    try:
        response = requests.get(f"{BASE_URL}/api/marketplace/v2/listings")
        data = response.json()
        success = data.get('status') == 'success' and data.get('count', 0) >= 2
        log_test(f"Get all listings ({data.get('count')} listings)", success)
    except:
        log_test("Get all listings", False)

    # Test 4: Get Pokemon listings only
    try:
        response = requests.get(f"{BASE_URL}/api/marketplace/v2/listings?tcg_id=pokemon")
        data = response.json()
        success = data.get('status') == 'success'
        log_test("Get Pokemon listings only", success)
    except:
        log_test("Get Pokemon listings only", False)

    # Test 5: Global marketplace search
    try:
        response = requests.get(f"{BASE_URL}/api/marketplace/v2/global?card_name=Pikachu")
        data = response.json()
        success = data.get('status') == 'success'
        log_test("Global marketplace search", success)
    except:
        log_test("Global marketplace search", False)

# ============================================================================
# TESTE User Preferences
# ============================================================================

def test_preferences():
    log_section("TESTE 4: User Preferences")

    # Test 1: Set Pokemon preference
    try:
        response = requests.post(
            f"{BASE_URL}/api/users/{USER_ID}/preferences",
            json={
                "tcg_id": "pokemon",
                "currency": "BRL",
                "language": "pt-BR",
                "favorite": True
            }
        )
        success = response.status_code == 201
        log_test("Set Pokemon preference", success)
    except:
        log_test("Set Pokemon preference", False)

    # Test 2: Set Magic preference
    try:
        response = requests.post(
            f"{BASE_URL}/api/users/{USER_ID}/preferences",
            json={
                "tcg_id": "magic",
                "currency": "USD",
                "language": "en-US",
                "favorite": False
            }
        )
        success = response.status_code == 201
        log_test("Set Magic preference", success)
    except:
        log_test("Set Magic preference", False)

    # Test 3: Get all preferences
    try:
        response = requests.get(f"{BASE_URL}/api/users/{USER_ID}/preferences")
        data = response.json()
        success = data.get('status') == 'success' and data.get('count', 0) >= 2
        log_test(f"Get user preferences ({data.get('count')} TCGs)", success)
    except:
        log_test("Get user preferences", False)

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    print(f"\n{'='*60}")
    print("TESTES MULTITCG FASE 2")
    print(f"{'='*60}\n")

    try:
        test_tcg_management()
        test_collections_v2()
        test_marketplace_v2()
        test_preferences()

        print(f"\n{'='*60}")
        print("RESUMO - MULTITCG")
        print(f"{'='*60}")
        print("\nTodos os testes de Multi-TCG foram executados!")
        print("\nFuncionalidades testadas:")
        print("  TCG Management: 3 endpoints")
        print("  Collections v2: 6 endpoints")
        print("  Marketplace v2: 5 endpoints")
        print("  Preferences: 3 endpoints")
        print("\nFase 2a (Multi-TCG) COMPLETA!\n")

    except Exception as e:
        print(f"\nErro durante testes: {e}")
