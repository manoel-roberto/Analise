import gspread
import pandas as pd
import numpy as np
from typing import Dict, List, Any
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class GoogleSheetsConnector:
    """Connector para operações em lote seguras no Google Sheets via gspread."""

    def __init__(self, credentials_path: str, spreadsheet_id: str):
        self.credentials_path = credentials_path
        self.spreadsheet_id = spreadsheet_id
        self.client = None
        self.spreadsheet = None

    def connect(self):
        """Autentica na API do Google Sheets com Service Account."""
        logger.info(f"Conectando ao Google Sheets com credenciais: {self.credentials_path}")
        self.client = gspread.service_account(filename=self.credentials_path)
        self.spreadsheet = self.client.open_by_key(self.spreadsheet_id)
        logger.info(f"Conexão estabelecida com sucesso: '{self.spreadsheet.title}'")

    def get_worksheet_dataframe(self, tab_name: str) -> pd.DataFrame:
        """Carrega os dados de uma aba específica como DataFrame do pandas."""
        if not self.spreadsheet:
            self.connect()
            
        ws = self.spreadsheet.worksheet(tab_name)
        data = ws.get_all_values()
        if not data:
            return pd.DataFrame()
            
        headers = [h.strip() if h else f"col_{i}" for i, h in enumerate(data[0])]
        rows = data[1:]
        df = pd.DataFrame(rows, columns=headers)
        return df

    def update_worksheet(self, tab_name: str, df: pd.DataFrame, clear_first: bool = True):
        """
        Atualiza o conteúdo de uma aba com um DataFrame do pandas em lote.
        Garante que nenhum valor float('nan') chegue à requisição JSON da API.
        """
        if not self.spreadsheet:
            self.connect()

        logger.info(f"Atualizando aba '{tab_name}' ({len(df)} linhas x {len(df.columns)} colunas)...")
        ws = self.spreadsheet.worksheet(tab_name)

        # Trata nulos e converte para string pura sem NaN
        df_clean = df.fillna('')
        values_rows = []
        for row in df_clean.values:
            row_clean = [
                "" if pd.isna(cell) or str(cell).strip().lower() in ['nan', 'none', '<na>', 'null']
                else str(cell).strip()
                for cell in row
            ]
            values_rows.append(row_clean)

        header_row = [list(df_clean.columns)]
        all_values = header_row + values_rows

        if clear_first:
            ws.clear()

        # Atualiza em lote
        ws.update(range_name='A1', values=all_values)
        logger.info(f"Aba '{tab_name}' atualizada com sucesso.")

    def update_batch(self, updates: Dict[str, pd.DataFrame]):
        """
        Atualiza múltiplas abas em sequência com tratamento de erro.
        """
        for tab_name, df in updates.items():
            try:
                self.update_worksheet(tab_name, df)
            except Exception as e:
                logger.error(f"Erro ao atualizar aba '{tab_name}': {e}")
                raise e
