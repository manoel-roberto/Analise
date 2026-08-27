import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
CREDENTIALS_FILE = os.getenv("GOOGLE_SHEETS_CREDENTIALS", str(BASE_DIR / "acaua-web-4898dee734cb.json"))

# ID da Planilha de Testes do Usuário ("Cópia de Estudo de Impacto Orçamentário - RTI e GSTU")
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID", "1KujGsjeJFgCdmPy6jt1MddPxrWEkS1EDYj9Tk4eGAqs")
SPREADSHEET_TITLE = "Cópia de Estudo de Impacto Orçamentário - RTI e GSTU"
DEFAULT_IMPORT_DIR = str(BASE_DIR / "import")

# Worksheets
TAB_BD_CADASTRO = "BD_Cadastro"
TAB_LISTAGEM = "Listagem"
TAB_BD_FOLHA = "BD_Folha"
TAB_TB_VENCIMENTOS = "TB_Vencimentos"
TAB_TB_COMISSIONADOS = "TB_Comissionados"
TAB_ANALISE_SIMULACAO = "Analise_Simulacao"
TAB_VISAO = "Visão"
TAB_PAINEL = "Painel de Ajuste Orçamentário - Verba RTI"
TAB_FONTE = "Fonte de dados"
TAB_TB_VENCIMENTOS_V2 = "TB_Vencimentos_v2"

# Simulação Groups Defaults (% Acréscimo)
DEFAULT_GRUPO_ACRESCIMOS = {
    "1.": 0.0,
    "2.": 0.0,
    "3.": 0.0,
    "4.": 0.0,
    "5.": 0.0,
    "6.": 0.0,
}
