import gspread
import pandas as pd
from src.ingestion.dw_parser import find_latest_dw_files, parse_dw_cadastro, parse_dw_folha
from src.transformation.cadastro_processor import process_cadastro_for_sheets
from src.transformation.folha_processor import process_folha_for_sheets
from src.reports.change_mapper import run_comprehensive_change_audit, format_comprehensive_audit_markdown

print("Carregando base original da planilha (07/2026)...")
client = gspread.service_account(filename='acaua-web-4898dee734cb.json')
orig_id = '1gRG-x5WMk_BMxPjQYXuNN4Ym4wJivlVv0pu7RLRUqgY'
sheet_orig = client.open_by_key(orig_id)

data_cad_orig = sheet_orig.worksheet("BD_Cadastro").get_all_values()
df_cad_orig = pd.DataFrame(data_cad_orig[1:], columns=data_cad_orig[0])

data_folha_orig = sheet_orig.worksheet("BD_Folha").get_all_values()
df_folha_orig = pd.DataFrame(data_folha_orig[1:], columns=data_folha_orig[0])

print("Parsing e processando arquivos do DW (08/2026)...")
bd_file, folha_file = find_latest_dw_files("import")
df_raw_dw_cad = parse_dw_cadastro(bd_file)
df_raw_dw_folha = parse_dw_folha(folha_file)

df_folha_novo = process_folha_for_sheets(df_raw_dw_folha)

print("Executando auditoria completa de Ingressos, Exonerações, Cargos e Folha nos 8 domínios de RH...")
audit_results = run_comprehensive_change_audit(
    df_cad_orig=df_cad_orig,
    df_raw_dw_cad=df_raw_dw_cad,
    df_folha_orig=df_folha_orig,
    df_folha_novo=df_folha_novo
)

# Exporta CSV Completo
df_records = pd.DataFrame(audit_results['diff_records'])
csv_path = "relatorio_auditoria_completa_mudancas_rh.csv"
df_records.to_csv(csv_path, index=False, encoding='utf-8-sig')

# Exporta Markdown Formatado por Domínio
md_path = "relatorio_auditoria_completa_mudancas_rh.md"
md_content = format_comprehensive_audit_markdown(audit_results)
with open(md_path, "w", encoding="utf-8") as f:
    f.write(md_content)

print(f"\n✅ AUDITORIA CONCLUÍDA COM SUCESSO!")
print(f"  - Ingressos (Novos Servidores): {audit_results['novos_count']}")
print(f"  - Desligamentos (Exonerações): {audit_results['saidas_count']}")
print(f"  - Total de Ocorrências Mapeadas: {audit_results['total_alteracoes']}")
print(f"  - Planilha CSV Completa:        {csv_path}")
print(f"  - Relatório Markdown Executivo: {md_path}")
