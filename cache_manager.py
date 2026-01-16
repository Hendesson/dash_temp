"""
Sistema de cache simplificado para dados processados.
"""
import os
import hashlib
import joblib
from typing import Any, Optional
import pandas as pd
import logging
from config_paths import CACHE_DIR

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CacheManager:
    def __init__(self, cache_dir: str = CACHE_DIR):
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
    
    def get_cache_path(self, key: str) -> str:
        return os.path.join(self.cache_dir, f"{key}.pkl")
    
    def get(self, key: str) -> Optional[Any]:
        cache_path = self.get_cache_path(key)
        if os.path.exists(cache_path):
            try:
                return joblib.load(cache_path)
            except Exception as e:
                logger.warning(f"Erro ao carregar cache {key}: {e}")
                return None
        return None
    
    def set(self, key: str, value: Any):
        cache_path = self.get_cache_path(key)
        try:
            joblib.dump(value, cache_path, compress=3)
            logger.debug(f"Cache salvo: {key}")
        except Exception as e:
            logger.warning(f"Erro ao salvar cache {key}: {e}")

cache_manager = CacheManager()
