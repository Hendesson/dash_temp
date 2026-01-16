"""
Processamento de dados para dashboard de temperaturas.
Versão simplificada - apenas o necessário para temperaturas diárias.
"""
import pandas as pd
import numpy as np
from datetime import datetime
import os
import logging
from typing import List, Optional
from cache_manager import cache_manager
from config_paths import DATA_DIR, PROCESSED_DIR

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DataProcessor:
    def __init__(self, file_path: Optional[str] = None):
        parquet_path = os.path.join(PROCESSED_DIR, "temp.parquet")
        excel_path = file_path or os.path.join(DATA_DIR, "temp.xlsx")
        
        if os.path.exists(parquet_path):
            self.file_path = parquet_path
            self.use_parquet = True
            logger.info(f"Usando arquivo Parquet: {self.file_path}")
        else:
            self.file_path = excel_path
            self.use_parquet = False
            logger.info(f"Usando arquivo Excel: {self.file_path}")
        
        self.df = None
        self.cidades = []
        self.anos = []
        self.load_data()

    def load_data(self) -> pd.DataFrame:
        """Carrega os dados do arquivo Parquet (prioritário) ou Excel."""
        try:
            logger.info(f"Tentando carregar dados do arquivo: {self.file_path}")
            
            if not os.path.exists(self.file_path):
                logger.warning(f"Arquivo não encontrado: {self.file_path}")
                filename = os.path.basename(self.file_path)
                alt_path = os.path.join(DATA_DIR, filename)
                if os.path.exists(alt_path):
                    logger.info(f"Arquivo encontrado em DATA_DIR: {alt_path}")
                    self.file_path = alt_path
                else:
                    logger.error(f"Arquivo não encontrado. Verifique se {filename} está em {DATA_DIR}")
                    return pd.DataFrame()
            
            cache_key = f"temp_data_{os.path.getmtime(self.file_path) if os.path.exists(self.file_path) else 0}"
            cached_df = cache_manager.get(cache_key)
            if cached_df is not None:
                logger.info("Dados carregados do cache")
                df = cached_df.copy()
            else:
                df = None
            
            if df is None:
                logger.info("Arquivo encontrado, iniciando leitura...")
                if self.use_parquet:
                    df = pd.read_parquet(self.file_path, engine='pyarrow')
                else:
                    df = pd.read_excel(self.file_path, engine='openpyxl')
                logger.info(f"Dados lidos com sucesso. Shape: {df.shape}")
            
            # Processa dados
            logger.info("Processando dados...")
            if "index" in df.columns:
                if not pd.api.types.is_datetime64_any_dtype(df["index"]):
                    df["index"] = pd.to_datetime(df["index"], errors="coerce")
            if "index" in df.columns:
                if "year" not in df.columns or df["year"].isna().any():
                    df["year"] = df["index"].dt.year
            if "cidade" in df.columns:
                if df["cidade"].dtype == 'category':
                    df["cidade"] = df["cidade"].astype(str)
                df["cidade"] = df["cidade"].astype(str).str.strip()
                df = df[df["cidade"].notna() & (df["cidade"] != "nan")]
            if "year" in df.columns:
                if df["year"].dtype == 'category':
                    df["year"] = df["year"].astype(str).astype(int)
                elif not pd.api.types.is_integer_dtype(df["year"]):
                    df["year"] = pd.to_numeric(df["year"], errors='coerce').astype('Int64')
                df = df[df["year"].notna()]
            if "year" in df.columns:
                df = df[df["year"] <= 2023]
            
            self.df = df
            if "cidade" in df.columns:
                self.cidades = sorted(df["cidade"].unique().tolist())
            else:
                self.cidades = []
            if "year" in df.columns:
                self.anos = sorted([int(x) for x in df["year"].unique().tolist() if pd.notna(x)])
            else:
                self.anos = []
            
            cache_manager.set(cache_key, df)
            logger.info(f"Dados processados. Cidades: {len(self.cidades)}, Anos: {len(self.anos)}")
            return df
                
        except Exception as e:
            logger.error(f"Erro ao carregar dados: {str(e)}")
            logger.exception("Detalhes do erro:")
            return pd.DataFrame()
