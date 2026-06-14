# -*- coding: utf-8 -*-
"""
Web Scraper para Bynx.gg - Fase 0
Extrai preços de cartas Pokémon TCG de bynx.gg
"""

import asyncio
import logging
import json
import re
import time
import random
from typing import Optional, Dict
from datetime import datetime
import os

# Se tiver Playwright, usar. Se não, usar requests simples
try:
    from playwright.async_api import async_playwright
    HAS_PLAYWRIGHT = True
except ImportError:
    HAS_PLAYWRIGHT = False
    import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# User-Agents para rotation
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
]

class BynxScraper:
    def __init__(self):
        self.base_url = "https://bynx.gg"
        self.browser = None
        self.page = None

    async def init_browser(self):
        """Inicializa navegador Playwright"""
        if not HAS_PLAYWRIGHT:
            logger.warning("Playwright não instalado. Usando fallback com requests.")
            return

        try:
            playwright = await async_playwright().start()
            self.browser = await playwright.chromium.launch(
                headless=True,
                args=['--disable-blink-features=AutomationControlled']
            )
            self.page = await self.browser.new_page()
            await self.page.set_user_agent(
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )
            logger.info("✓ Browser Playwright iniciado")
        except Exception as e:
            logger.error(f"Erro ao iniciar Playwright: {e}")
            HAS_PLAYWRIGHT = False

    async def close_browser(self):
        """Fecha navegador"""
        if self.page:
            try:
                await self.page.close()
            except:
                pass
        if self.browser:
            try:
                await self.browser.close()
            except:
                pass
        logger.info("✓ Browser fechado")

    def _parse_price(self, price_text: str) -> Optional[float]:
        """
        Parse de preço em BRL
        Ex: "R$ 250,00" → 250.00
        """
        if not price_text:
            return None

        # Remove "R$" e espaços
        price_text = re.sub(r'[R$\s]', '', price_text)
        # Trata separador decimal português (vírgula)
        price_text = price_text.replace(',', '.')

        try:
            return float(price_text)
        except ValueError:
            logger.warning(f"Não conseguiu fazer parse de preço: {price_text}")
            return None

    async def search_card_playwright(self, card_name: str, set_id: str) -> Optional[Dict]:
        """Busca carta usando Playwright"""
        if not self.page:
            return None

        try:
            # 1. Acessar página de busca
            search_url = f"{self.base_url}/search?q={card_name}"
            logger.info(f"Acessando: {search_url}")
            await self.page.goto(search_url, wait_until='networkidle', timeout=10000)

            # 2. Aguardar resultados carregarem
            await self.page.wait_for_selector('[data-testid="card-listing"]', timeout=5000)

            # 3. Extrair dados
            cards = await self.page.query_selector_all('[data-testid="card-listing"]')
            logger.info(f"Encontrados {len(cards)} cards")

            for card_element in cards:
                try:
                    card_data = await card_element.evaluate("""
                        el => {
                            const id = el.getAttribute('data-card-id');
                            const name = el.querySelector('[data-testid="card-name"]')?.innerText;
                            const set = el.querySelector('[data-testid="set-name"]')?.innerText;
                            const priceText = el.querySelector('[data-testid="price"]')?.innerText;
                            const imageUrl = el.querySelector('img')?.src;

                            return { id, name, set, priceText, imageUrl };
                        }
                    """)

                    if set_id in (card_data.get('id') or ''):
                        price = self._parse_price(card_data.get('priceText', ''))

                        result = {
                            'id': card_data['id'],
                            'name': card_data['name'],
                            'set': card_data['set'],
                            'price_brl': price,
                            'image_url': card_data['imageUrl'],
                            'source': 'bynx.gg',
                            'timestamp': datetime.now().isoformat()
                        }
                        logger.info(f"✓ Encontrado: {card_data['name']} - R$ {price}")
                        return result
                except Exception as e:
                    logger.debug(f"Erro ao extrair card: {e}")
                    continue

            logger.warning(f"Carta não encontrada: {card_name} ({set_id})")
            return None

        except Exception as e:
            logger.error(f"Erro ao buscar carta: {e}")
            return None

    def search_card_fallback(self, card_name: str, set_id: str) -> Optional[Dict]:
        """Fallback usando requests (sem Playwright) com retry e delays"""
        if not requests:
            logger.error("requests não disponível")
            return None

        max_retries = 3
        for attempt in range(max_retries):
            try:
                # Delay aleatório entre tentativas (1-3s)
                if attempt > 0:
                    delay = random.uniform(1, 3)
                    logger.info(f"Aguardando {delay:.1f}s antes de retry {attempt}...")
                    time.sleep(delay)

                # Tentar múltiplos endpoints
                urls = [
                    f"{self.base_url}/api/search?q={card_name}",
                    f"{self.base_url}/search?q={card_name}",
                ]

                user_agent = random.choice(USER_AGENTS)
                headers = {
                    'User-Agent': user_agent,
                    'Accept': 'application/json',
                    'Referer': self.base_url,
                }

                for search_url in urls:
                    try:
                        logger.info(f"[{attempt+1}/{max_retries}] Buscando: {card_name} em {search_url}")
                        response = requests.get(search_url, headers=headers, timeout=10)

                        if response.status_code == 200:
                            try:
                                data = response.json()
                            except:
                                # Se não for JSON, try parse HTML
                                logger.debug("Resposta não é JSON, tentando HTML parse")
                                continue

                            # Procura pela carta correta
                            if isinstance(data, list):
                                for card in data:
                                    if set_id in (card.get('id', '') or ''):
                                        price = card.get('price_brl')
                                        if isinstance(price, str):
                                            price = self._parse_price(price)

                                        result = {
                                            'id': card.get('id'),
                                            'name': card.get('name'),
                                            'set': card.get('set'),
                                            'price_brl': price,
                                            'image_url': card.get('image_url'),
                                            'source': 'bynx.gg',
                                            'timestamp': datetime.now().isoformat()
                                        }
                                        logger.info(f"✓ Encontrado: {result['name']} - R$ {price}")
                                        return result
                            elif isinstance(data, dict):
                                # Caso seja um objeto único
                                if set_id in (data.get('id', '') or ''):
                                    price = data.get('price_brl')
                                    if isinstance(price, str):
                                        price = self._parse_price(price)
                                    return {
                                        'id': data.get('id'),
                                        'name': data.get('name'),
                                        'set': data.get('set'),
                                        'price_brl': price,
                                        'image_url': data.get('image_url'),
                                        'source': 'bynx.gg',
                                        'timestamp': datetime.now().isoformat()
                                    }
                    except requests.exceptions.Timeout:
                        logger.warning(f"Timeout em {search_url}")
                    except requests.exceptions.ConnectionError:
                        logger.warning(f"Erro de conexão em {search_url}")
                    except Exception as e:
                        logger.debug(f"Erro ao processar {search_url}: {e}")

            except Exception as e:
                logger.error(f"[{attempt+1}/{max_retries}] Erro: {e}")

        logger.warning(f"Carta não encontrada após {max_retries} tentativas: {card_name} ({set_id})")
        return None

    async def search_card(self, card_name: str, set_id: str) -> Optional[Dict]:
        """Interface principal - tenta Playwright, depois fallback"""
        if HAS_PLAYWRIGHT and self.page:
            return await self.search_card_playwright(card_name, set_id)
        else:
            return self.search_card_fallback(card_name, set_id)


# Classe auxiliar para usar scraper de forma síncrona
class BynxScraperSync:
    def __init__(self):
        self.scraper = BynxScraper()
        # Try to import mock fallback
        try:
            from scraper_bynx_mock import MockBynxPrice
            self.mock_service = MockBynxPrice()
            logger.info("✓ Mock service carregado para fallback")
        except ImportError:
            self.mock_service = None
            logger.warning("Mock service não disponível")

    def search_card(self, card_name: str, set_id: str, use_mock_fallback: bool = True) -> Optional[Dict]:
        """
        Interface síncrona para scraper com fallback para mock

        Args:
            card_name: Nome da carta
            set_id: ID da carta (ex: base1-4)
            use_mock_fallback: Se True, usa mock quando scraper falha
        """
        try:
            # 1. Tenta scraper (requests com retry)
            result = self.scraper.search_card_fallback(card_name, set_id)
            if result:
                logger.info(f"✓ Preço real encontrado: {card_name}")
                return result

            # 2. Se falhar e permitir mock, usa cache mockado
            if use_mock_fallback and self.mock_service:
                logger.info(f"Usando preço mock para: {card_name} ({set_id})")
                mock_result = self.mock_service.get_price(card_name, set_id)
                if mock_result:
                    return mock_result

            logger.warning(f"Preço não encontrado: {card_name} ({set_id})")
            return None

        except Exception as e:
            logger.error(f"Erro ao buscar: {e}")
            # Último recurso: tentar mock
            if use_mock_fallback and self.mock_service:
                return self.mock_service.get_price(card_name, set_id)
            return None
