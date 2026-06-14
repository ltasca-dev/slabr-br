# -*- coding: utf-8 -*-
"""
Mock Cache para Bynx.gg - Fallback quando API é indisponível
Preços simulados realistas para testes e Fase 1
"""

from datetime import datetime
from typing import Optional, Dict
import logging

logger = logging.getLogger(__name__)

# Banco de dados mockado com preços simulados reais para cartas Pokémon TCG
MOCK_PRICES = {
    # Base Set
    'base1-1': {'name': 'Alakazam', 'price_brl': 2850.00, 'set': 'Base Set'},
    'base1-2': {'name': 'Blastoise', 'price_brl': 3200.00, 'set': 'Base Set'},
    'base1-3': {'name': 'Venusaur', 'price_brl': 2900.00, 'set': 'Base Set'},
    'base1-4': {'name': 'Charizard', 'price_brl': 5500.00, 'set': 'Base Set'},
    'base1-6': {'name': 'Gyarados', 'price_brl': 1200.00, 'set': 'Base Set'},
    'base1-10': {'name': 'Mewtwo', 'price_brl': 2100.00, 'set': 'Base Set'},
    'base1-11': {'name': 'Machamp', 'price_brl': 950.00, 'set': 'Base Set'},
    'base1-12': {'name': 'Zapdos', 'price_brl': 850.00, 'set': 'Base Set'},
    'base1-13': {'name': 'Moltres', 'price_brl': 800.00, 'set': 'Base Set'},
    'base1-14': {'name': 'Articuno', 'price_brl': 750.00, 'set': 'Base Set'},
    'base1-16': {'name': 'Lapras', 'price_brl': 1100.00, 'set': 'Base Set'},
    'base1-19': {'name': 'Arcanine', 'price_brl': 450.00, 'set': 'Base Set'},
    'base1-24': {'name': 'Raichu', 'price_brl': 580.00, 'set': 'Base Set'},
    'base1-25': {'name': 'Pikachu', 'price_brl': 1850.00, 'set': 'Base Set'},
    'base1-31': {'name': 'Jynx', 'price_brl': 350.00, 'set': 'Base Set'},
    'base1-32': {'name': 'Wigglytuff', 'price_brl': 320.00, 'set': 'Base Set'},
    'base1-34': {'name': 'Gengar', 'price_brl': 420.00, 'set': 'Base Set'},
    'base1-35': {'name': 'Golem', 'price_brl': 380.00, 'set': 'Base Set'},
    'base1-36': {'name': 'Hypno', 'price_brl': 300.00, 'set': 'Base Set'},

    # Fossil Set
    'fossil-5': {'name': 'Dragonite', 'price_brl': 1950.00, 'set': 'Fossil'},

    # Jungle Set
    'base2-11': {'name': 'Cloyster', 'price_brl': 280.00, 'set': 'Jungle'},

    # Shadowless (raríssimo)
    'sv1-121': {'name': 'Pikachu ex', 'price_brl': 8500.00, 'set': 'Scarlet & Violet'},

    # Black & White
    'bw2-11': {'name': 'Emboar', 'price_brl': 650.00, 'set': 'Black & White'},
}


class MockBynxPrice:
    """Serviço de preços mockado para fallback"""

    @staticmethod
    def get_price(card_name: str, set_id: str) -> Optional[Dict]:
        """
        Retorna preço mockado de uma carta
        Simula busca em Bynx.gg com dados realistas
        """
        if set_id in MOCK_PRICES:
            mock_data = MOCK_PRICES[set_id]
            return {
                'id': set_id,
                'name': mock_data['name'],
                'set': mock_data['set'],
                'price_brl': mock_data['price_brl'],
                'image_url': None,
                'source': 'bynx.gg (mock)',
                'timestamp': datetime.now().isoformat(),
                'is_mock': True
            }

        logger.warning(f"Preço mockado não encontrado para: {card_name} ({set_id})")
        return None

    @staticmethod
    def get_all_mocked_ids():
        """Retorna lista de IDs que têm preços mockados"""
        return list(MOCK_PRICES.keys())

    @staticmethod
    def add_mock_price(card_id: str, name: str, price_brl: float, set_name: str):
        """Adiciona um novo preço mockado (para testes)"""
        MOCK_PRICES[card_id] = {
            'name': name,
            'price_brl': price_brl,
            'set': set_name
        }
        logger.info(f"Adicionado preço mock: {card_id} - R$ {price_brl}")
