import pandas as pd
import numpy as np

BD_FOLHA_COLUMNS = [
    'Matricula', 'Nome', 'Tipo', 'Competência', 'Cod. Rubrica salarial', 'Rubrica salarial', 'VALOR'
]

def format_currency_br(val: float) -> str:
    """Formata valor float para string moeda BR: R$ 1.234,56"""
    if pd.isna(val) or val is None:
        return "R$ 0,00"
    is_neg = val < 0
    abs_val = abs(val)
    formatted = f"{abs_val:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    return f"-R$ {formatted}" if is_neg else f"R$ {formatted}"

def process_folha_for_sheets(df_dw_folha: pd.DataFrame) -> pd.DataFrame:
    """
    Processa e alinha os dados do DW Folha para o formato exato da aba BD_Folha no Google Sheets.
    """
    df = df_dw_folha.copy()
    out_df = pd.DataFrame()

    out_df['Matricula'] = df['Matricula'] if 'Matricula' in df.columns else ""
    out_df['Nome'] = df['Nome'] if 'Nome' in df.columns else ""
    out_df['Tipo'] = df['Tipo'] if 'Tipo' in df.columns else ""
    out_df['Competência'] = df['Mes_Ano'] if 'Mes_Ano' in df.columns else ""
    out_df['Cod. Rubrica salarial'] = df['Cod_Rubrica'] if 'Cod_Rubrica' in df.columns else ""
    out_df['Rubrica salarial'] = df['Rubrica'] if 'Rubrica' in df.columns else ""

    # Converte e formata o Valor R$
    if 'Valor' in df.columns:
        def parse_val(v):
            if pd.isna(v) or v is None: return 0.0
            s = str(v).replace('R$', '').strip().replace('.', '').replace(',', '.')
            try: return float(s)
            except: return 0.0
        
        numeric_vals = df['Valor'].apply(parse_val)
        out_df['VALOR'] = numeric_vals.apply(format_currency_br)
    else:
        out_df['VALOR'] = "R$ 0,00"

    return out_df[BD_FOLHA_COLUMNS]
