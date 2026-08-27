import os
import glob
import quopri
from lxml import html
import pandas as pd
from typing import Tuple, Optional, List

def decode_mhtml_file(file_path: str) -> str:
    """Decodifica arquivo MHTML/Quoted-Printable (.xls exportado do DW) em string HTML."""
    with open(file_path, 'rb') as f:
        content = f.read()
    # Checa se é MHTML
    if b'MIME-Version:' in content[:100] or b'quoted-printable' in content[:500]:
        return quopri.decodestring(content).decode('latin1', errors='ignore')
    else:
        return content.decode('latin1', errors='ignore')

def parse_dw_cadastro(file_path: str) -> pd.DataFrame:
    """
    Lê o arquivo DW de Cadastro (ex: bd-.08.2026.xls) e retorna um DataFrame sanitizado.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Arquivo de cadastro não encontrado: {file_path}")

    html_content = decode_mhtml_file(file_path)
    tree = html.fromstring(html_content)
    tables = tree.xpath('//table')

    if not tables:
        raise ValueError(f"Nenhuma tabela HTML encontrada no arquivo {file_path}")

    data_table = max(tables, key=lambda t: len(t.xpath('.//tr')))
    rows = data_table.xpath('.//tr')

    table_data = []
    for r in rows:
        cells = [c.text_content().strip() for c in r.xpath('.//td | .//th')]
        if cells:
            table_data.append(cells)

    if len(table_data) < 4:
        raise ValueError(f"Dados insuficientes na tabela de cadastro de {file_path}")

    raw_headers = table_data[2]
    data_rows = table_data[3:]

    # Ajusta dimensões das colunas
    max_cols = max(len(r) for r in data_rows)
    headers = [str(raw_headers[i]).strip() if i < len(raw_headers) and raw_headers[i] else f"col_{i}" for i in range(max_cols)]

    df = pd.DataFrame(data_rows, columns=headers[:max_cols])
    df = df.dropna(how='all')
    return df

def parse_dw_folha(file_path: str) -> pd.DataFrame:
    """
    Lê o arquivo DW da Folha (ex: folha-08.2026.xls) e retorna um DataFrame sanitizado.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Arquivo da folha não encontrado: {file_path}")

    html_content = decode_mhtml_file(file_path)
    tree = html.fromstring(html_content)
    tables = tree.xpath('//table')

    if not tables:
        raise ValueError(f"Nenhuma tabela HTML encontrada no arquivo {file_path}")

    data_table = max(tables, key=lambda t: len(t.xpath('.//tr')))
    rows = data_table.xpath('.//tr')

    folha_data = []
    for r in rows:
        cells = [c.text_content().strip() for c in r.xpath('.//td | .//th')]
        if cells:
            folha_data.append(cells)

    if len(folha_data) < 3:
        raise ValueError(f"Dados insuficientes na tabela da folha de {file_path}")

    # Headers conhecidos da folha DW: ['Mes_Ano', 'Matricula', 'Nome', 'Tipo', 'Cod_Rubrica', 'Rubrica', 'Num_Servidores', 'Valor']
    standard_headers = ['Mes_Ano', 'Matricula', 'Nome', 'Tipo', 'Cod_Rubrica', 'Rubrica', 'Num_Servidores', 'Valor']
    
    data_rows = folha_data[2:]
    max_cols = max(len(r) for r in data_rows) if data_rows else 8
    headers = standard_headers[:max_cols] if max_cols <= len(standard_headers) else standard_headers + [f"col_{i}" for i in range(len(standard_headers), max_cols)]

    df = pd.DataFrame(data_rows, columns=headers[:max_cols])
    df = df.dropna(how='all')
    return df

def find_latest_dw_files(import_dir: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Localiza os arquivos mais recentes de cadastro (bd-*.xls) e folha (folha-*.xls) no diretório especificado.
    """
    bd_pattern = os.path.join(import_dir, "bd*.xls*")
    folha_pattern = os.path.join(import_dir, "folha*.xls*")

    bd_files = sorted(glob.glob(bd_pattern), key=os.path.getmtime, reverse=True)
    folha_files = sorted(glob.glob(folha_pattern), key=os.path.getmtime, reverse=True)

    bd_path = bd_files[0] if bd_files else None
    folha_path = folha_files[0] if folha_files else None

    return bd_path, folha_path
