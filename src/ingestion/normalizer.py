import pandas as pd
import numpy as np

def clean_currency(val) -> float:
    """Converte valores monetários no formato brasileiro ('R$ 1.234,56' ou '-R$ 500,00') para float."""
    if pd.isna(val) or val is None or val == '':
        return 0.0
    if isinstance(val, (int, float)):
        return float(val) if not np.isnan(val) else 0.0
    
    s = str(val).replace('R$', '').replace('\xa0', '').strip()
    if not s:
        return 0.0
    
    is_negative = s.startswith('-') or s.endswith('-')
    s = s.replace('-', '').strip()
    s = s.replace('.', '').replace(',', '.')
    try:
        parsed = float(s)
        return -parsed if is_negative else parsed
    except ValueError:
        return 0.0

def clean_percent(val) -> float:
    """Converte percentuais ('50,00%' ou '0,5') para float decimal (ex: 0.50)."""
    if pd.isna(val) or val is None or val == '':
        return 0.0
    if isinstance(val, (int, float)):
        v = float(val)
        return v / 100.0 if v > 1.0 else v
    s = str(val).replace('%', '').strip().replace(',', '.')
    if not s:
        return 0.0
    try:
        v = float(s)
        return v / 100.0 if v > 1.0 else v
    except ValueError:
        return 0.0

def normalize_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Limpa e padroniza strings, espaços em branco e nulos em um DataFrame."""
    df_clean = df.copy()
    for col in df_clean.columns:
        # Aplica strip em cada elemento de texto
        df_clean[col] = df_clean[col].apply(lambda x: str(x).strip() if pd.notnull(x) and str(x).strip() not in ['nan', 'None', 'NaN', '#'] else '')
    return df_clean
