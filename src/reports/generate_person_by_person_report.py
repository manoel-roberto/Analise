import gspread
import pandas as pd
from src.ingestion.dw_parser import find_latest_dw_files, parse_dw_cadastro, parse_dw_folha
from src.transformation.cadastro_processor import process_cadastro_for_sheets
from src.transformation.folha_processor import process_folha_for_sheets
from src.reports.person_diff_reporter import build_person_by_person_diff_report, format_person_diff_markdown

# 1. Carrega Planilha Original (Linha de Base 07/2026)
print("Carregando tabelas originais da planilha (07/2026)...")
client = gspread.service_account(filename='acaua-web-4898dee734cb.json')
orig_id = '1gRG-x5WMk_BMxPjQYXuNN4Ym4wJivlVv0pu7RLRUqgY'
sheet_orig = client.open_by_key(orig_id)

data_cad_orig = sheet_orig.worksheet("BD_Cadastro").get_all_values()
df_cad_orig = pd.DataFrame(data_cad_orig[1:], columns=data_cad_orig[0])

data_folha_orig = sheet_orig.worksheet("BD_Folha").get_all_values()
df_folha_orig = pd.DataFrame(data_folha_orig[1:], columns=data_folha_orig[0])

# 2. Parse e Processa Novo Mês DW (08/2026)
print("Executando parsing MHTML dos arquivos do DW (08/2026)...")
bd_file, folha_file = find_latest_dw_files("import")
df_raw_dw_cad = parse_dw_cadastro(bd_file)
df_raw_dw_folha = parse_dw_folha(folha_file)

df_cad_novo = process_cadastro_for_sheets(df_raw_dw_cad, df_existing_bd=df_cad_orig)
df_folha_novo = process_folha_for_sheets(df_raw_dw_folha)

# 3. Comparação Pessoa por Pessoa (Campo a Campo)
print("Gerando relatório de divergências por servidor (campo a campo)...")
diff_records = build_person_by_person_diff_report(
    df_cad_orig=df_cad_orig,
    df_cad_novo=df_cad_novo,
    df_folha_orig=df_folha_orig,
    df_folha_novo=df_folha_novo
)

# 4. Salva CSV Completo
df_diff = pd.DataFrame(diff_records)
csv_path = "relatorio_alteracoes_por_servidor.csv"
df_diff.to_csv(csv_path, index=False, encoding='utf-8-sig')

# 5. Salva Markdown Formatado
md_path = "relatorio_alteracoes_por_servidor.md"
md_content = format_person_diff_markdown(diff_records)
with open(md_path, "w", encoding="utf-8") as f:
    f.write(md_content)

print(f"\n✅ Relatório concluído!")
print(f"  - CSV Completo: {csv_path} ({len(df_diff)} registros de alterações)")
print(f"  - Markdown: {md_path}")
