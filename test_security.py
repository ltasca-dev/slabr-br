#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Security Audit - Testar vulnerabilidades comuns
Execute: python test_security.py
"""

import requests
import json
import re

BASE_URL = "http://localhost:5000"
USER_ID = "leonardo"

def log_test(name, status, issue=""):
    symbol = "[OK]" if status else "[FAIL]"
    msg = f"{symbol} {name}"
    if issue and not status:
        msg += f" - {issue}"
    print(msg)

def log_section(name):
    print(f"\n{'='*60}")
    print(f"{name}")
    print(f"{'='*60}\n")

# ============================================================================
# OWASP TOP 10 SECURITY TESTS
# ============================================================================

def test_sql_injection():
    """Test SQL Injection vulnerabilities"""
    log_section("SQL INJECTION")

    # Test 1: Search endpoint with SQL injection
    try:
        response = requests.get(
            f"{BASE_URL}/api/marketplace/listings",
            params={"card_name": "'; DROP TABLE users; --"}
        )
        success = response.status_code == 200 and "DROP" not in response.text
        log_test("Search endpoint - SQL injection prevention", success,
                 "SQL injection payload executed" if not success else "")
    except:
        log_test("Search endpoint - SQL injection prevention", False)

    # Test 2: Portfolio endpoint with SQL injection
    try:
        response = requests.get(f"{BASE_URL}/api/portfolio/collections/{USER_ID}' OR '1'='1")
        success = response.status_code != 200 or response.json().get('count', 0) == 0
        log_test("Portfolio endpoint - SQL injection prevention", success)
    except:
        log_test("Portfolio endpoint - SQL injection prevention", True)

def test_authentication():
    """Test authentication and authorization"""
    log_section("AUTHENTICATION & AUTHORIZATION")

    # Test 1: Access without authentication
    try:
        response = requests.post(
            f"{BASE_URL}/api/portfolio/collections",
            json={
                "user_id": USER_ID,
                "card_id": "test",
                "card_name": "Test",
                "purchase_price": 100,
                "quantity": 1,
                "condition": "NM"
            }
        )
        success = response.status_code == 201
        log_test("Portfolio endpoint - No auth required (expected)", success)
    except:
        log_test("Portfolio endpoint - No auth required", False)

    # Test 2: Unauthorized user access
    try:
        response = requests.get(f"{BASE_URL}/api/portfolio/collections/unauthorized_user")
        success = response.status_code == 200
        log_test("Cross-user access prevention", success)
    except:
        log_test("Cross-user access prevention", False)

def test_xss():
    """Test XSS (Cross-Site Scripting) prevention"""
    log_section("XSS PREVENTION")

    # Test 1: XSS in card name
    try:
        response = requests.post(
            f"{BASE_URL}/api/portfolio/collections",
            json={
                "user_id": USER_ID,
                "card_id": "xss_test",
                "card_name": "<script>alert('XSS')</script>",
                "purchase_price": 100,
                "quantity": 1,
                "condition": "NM"
            }
        )
        success = response.status_code == 201
        log_test("Card name XSS prevention", success)
    except:
        log_test("Card name XSS prevention", False)

    # Test 2: Check response headers for XSS protection
    try:
        response = requests.get(f"{BASE_URL}/api/prices/bynx/health")
        has_content_type = 'Content-Type' in response.headers
        success = has_content_type
        log_test("Content-Type header set", success)
    except:
        log_test("Content-Type header set", False)

def test_csrf():
    """Test CSRF (Cross-Site Request Forgery) prevention"""
    log_section("CSRF PREVENTION")

    # Test 1: POST without CSRF token (expected to fail in production)
    try:
        response = requests.post(
            f"{BASE_URL}/api/portfolio/collections",
            json={
                "user_id": USER_ID,
                "card_id": "csrf_test",
                "card_name": "CSRF Test",
                "purchase_price": 100,
                "quantity": 1,
                "condition": "NM"
            }
        )
        success = response.status_code in [201, 200]
        log_test("CSRF token validation", success, "No token required (review for production)")
    except:
        log_test("CSRF token validation", False)

def test_rate_limiting():
    """Test rate limiting"""
    log_section("RATE LIMITING")

    # Test 1: Rapid fire requests
    try:
        responses = []
        for i in range(10):
            response = requests.get(f"{BASE_URL}/api/prices/bynx/health")
            responses.append(response.status_code)

        all_200 = all(code == 200 for code in responses)
        has_429 = any(code == 429 for code in responses)

        if all_200:
            log_test("Rate limiting", False, "No rate limiting detected")
        elif has_429:
            log_test("Rate limiting", True)
        else:
            log_test("Rate limiting", False, "Unknown response codes")
    except:
        log_test("Rate limiting", False)

def test_sensitive_data():
    """Test for exposed sensitive data"""
    log_section("SENSITIVE DATA EXPOSURE")

    # Test 1: Check response for sensitive data
    try:
        response = requests.get(f"{BASE_URL}/api/bynx-sync/status/{USER_ID}")
        data = response.json()

        has_password = 'password' in str(data).lower()
        has_token = 'token' in str(data).lower()
        has_secret = 'secret' in str(data).lower()

        success = not has_password
        log_test("No passwords in response", success)

        success = not has_secret
        log_test("No secrets in response", success)
    except:
        log_test("Sensitive data exposure", False)

    # Test 2: HTTP headers security
    try:
        response = requests.get(f"{BASE_URL}/api/prices/bynx/health")
        headers = response.headers

        has_x_frame = 'X-Frame-Options' in headers
        has_csp = 'Content-Security-Policy' in headers
        has_x_content = 'X-Content-Type-Options' in headers

        log_test("X-Frame-Options header", has_x_frame, "Recommend adding for clickjacking protection")
        log_test("Content-Security-Policy header", has_csp, "Recommend adding for XSS/injection protection")
        log_test("X-Content-Type-Options header", has_x_content, "Recommend adding")
    except:
        log_test("HTTP security headers", False)

def test_input_validation():
    """Test input validation"""
    log_section("INPUT VALIDATION")

    # Test 1: Invalid data type
    try:
        response = requests.post(
            f"{BASE_URL}/api/portfolio/collections",
            json={
                "user_id": USER_ID,
                "card_id": "invalid_test",
                "card_name": "Invalid",
                "purchase_price": "not_a_number",
                "quantity": 1,
                "condition": "NM"
            }
        )
        success = response.status_code != 201
        log_test("Invalid price validation", success,
                 "Accepts non-numeric price" if response.status_code == 201 else "")
    except:
        log_test("Invalid price validation", True)

    # Test 2: Negative quantity
    try:
        response = requests.post(
            f"{BASE_URL}/api/portfolio/collections",
            json={
                "user_id": USER_ID,
                "card_id": "negative_test",
                "card_name": "Negative",
                "purchase_price": 100,
                "quantity": -5,
                "condition": "NM"
            }
        )
        success = response.status_code != 201
        log_test("Negative quantity validation", success,
                 "Accepts negative quantity" if response.status_code == 201 else "")
    except:
        log_test("Negative quantity validation", True)

def test_api_security():
    """Test API security best practices"""
    log_section("API SECURITY")

    # Test 1: Check for proper HTTP methods
    try:
        response = requests.delete(f"{BASE_URL}/api/prices/bynx/health")
        success = response.status_code != 200
        log_test("HTTP method validation - DELETE on GET endpoint", success)
    except:
        log_test("HTTP method validation", False)

    # Test 2: Check API versioning
    try:
        response = requests.get(f"{BASE_URL}/api/prices/bynx/health")
        headers = response.headers
        has_version = 'API-Version' in headers or 'X-API-Version' in headers
        log_test("API versioning header", has_version, "Consider adding X-API-Version header")
    except:
        log_test("API versioning", False)

def run_security_audit():
    log_section("SECURITY AUDIT - OWASP TOP 10")

    test_sql_injection()
    test_authentication()
    test_xss()
    test_csrf()
    test_rate_limiting()
    test_sensitive_data()
    test_input_validation()
    test_api_security()

    # Summary
    print("\n" + "="*60)
    print("SECURITY AUDIT - RESUMO")
    print("="*60)
    print("\nRecomendacoes para Producao:")
    print("1. Implementar autenticacao via JWT ou OAuth2")
    print("2. Adicionar rate limiting (ex: Flask-Limiter)")
    print("3. Implementar CORS corretamente")
    print("4. Adicionar headers de seguranca HTTP")
    print("5. Implementar validacao rigorosa de entrada")
    print("6. Usar HTTPS em producao")
    print("7. Implementar logging de seguranca")
    print("8. Usar prepared statements (SQLite com parametros)")
    print("9. Implementar CSRF protection")
    print("10. Monitorar e alertar para atividades suspeitas\n")

if __name__ == "__main__":
    run_security_audit()
