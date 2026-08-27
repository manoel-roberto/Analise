import gspread
import pandas as pd
from src.ingestion.dw_parser import find_latest_dw_files, parse_dw_cadastro, parse_dw_folha
from src.transformation.cadastro_processor import process_cadastro_for_sheets
from src.transformation.folha_processor import process_folha_for_sheets
from src.reports.change_reporter import generate_audit_report

# Carrega base original (07/2026)
client = gspread.service_account(filename='acaua-web-4898dee734cb.json')
sheet_orig = client.open_by_key('1gRG-x5WMk_BMxPjQYXuNN4Ym4wJivlVv0pu7RLRUqgY')

df_cad_orig = sheet_orig.worksheet("BD_Cadastro").get_all_values()
df_cad_orig = pd.DataFrame(df_cad_orig[1:], columns=df_cad_orig[0])

df_folha_orig = sheet_orig.worksheet("BD_Folha").get_all_values()
df_folha_orig = pd.DataFrame(df_folha_orig[1:], columns=df_folha_orig[0])

# Parse DW novo (08/2026)
bd_file, folha_file = find_latest_dw_files("import")
df_raw_cad = parse_dw_cadastro(bd_file)
df_raw_folha = parse_dw_folha(folha_file)

df_cad_novo = process_cadastro_for_sheets(df_raw_cad, df_existing_bd=df_cad_orig)
df_folha_novo = process_folha_for_sheets(df_raw_folha)

report_data = generate_audit_report(
    df_cad_orig=df_cad_orig,
    df_cad_novo=df_cad_novo,
    df_folha_orig=df_folha_orig,
    df_folha_novo=df_folha_novo,
    output_md_path="relatorio_mudancas_07_vs_08_2026.md"
)

print(report_data['md_content'])
