import gspread
import pandas as pd
from src.ingestion.dw_parser import find_latest_dw_files, parse_dw_cadastro, parse_dw_folha
from src.transformation.cadastro_processor import process_cadastro_for_sheets
from src.transformation.folha_processor import process_folha_for_sheets
from src.reports.column_by_column_auditor import compare_dataframes_column_by_column, format_column_audit_markdown

# 1. Carrega Planilha Original (Linha de Base 07/2026)
client = gspread.service_account(filename='acaua-web-4898dee734cb.json')
orig_id = '1gRG-x5WMk_BMxPjQYXuNN4Ym4wJivlVv0pu7RLRUqgY'
sheet_orig = client.open_by_key(orig_id)

print("Carregando tabelas originais da planilha (07/2026)...")
data_cad_orig = sheet_orig.worksheet("BD_Cadastro").get_all_values()
df_cad_orig = pd.DataFrame(data_cad_orig[1:], columns=data_cad_orig[0])

data_folha_orig = sheet_orig.worksheet("BD_Folha").get_all_values()
df_folha_orig = pd.DataFrame(data_folha_orig[1:], columns=data_folha_orig[0])

# 2. Parse e Processa Novo Mês do DW (08/2026)
print("Executando parsing MHTML dos arquivos do DW (08/2026)...")
bd_file, folha_file = find_latest_dw_files("import")
df_raw_dw_cad = parse_dw_cadastro(bd_file)
df_raw_dw_folha = parse_dw_folha(folha_file)

df_cad_novo = process_cadastro_for_sheets(df_raw_dw_cad, df_existing_bd=df_cad_orig)
df_folha_novo = process_folha_for_sheets(df_raw_dw_folha)

# 3. Comparação Coluna por Coluna em BD_Cadastro
print("\nAuditando todas as 64 colunas de BD_Cadastro...")
audit_cad = compare_dataframes_column_by_column(
    df_base=df_cad_orig,
    df_novo=df_cad_novo,
    key_col='Matricula',
    tab_name='BD_Cadastro'
)
md_cad = format_column_audit_markdown(audit_cad)

# 4. Comparação Coluna por Coluna em BD_Folha
print("Auditando todas as colunas de BD_Folha...")
audit_folha = compare_dataframes_column_by_column(
    df_base=df_folha_orig,
    df_novo=df_folha_novo,
    key_col='Matricula',
    tab_name='BD_Folha'
)
md_folha = format_column_audit_markdown(audit_folha)

# 5. Salva Relatório Completo em Markdown
full_report_md = md_cad + "\n\n---\n\n" + md_folha

output_path = "relatorio_comparacao_coluna_por_coluna.md"
with open(output_path, "w", encoding="utf-8") as f:
    f.write(full_report_md)

print(f"\n✅ Relatório Coluna por Coluna gerado com sucesso em: {output_path}")
