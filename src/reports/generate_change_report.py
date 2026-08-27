import gspread
import pandas as pd
import numpy as np
from src.ingestion.dw_parser import find_latest_dw_files, parse_dw_cadastro, parse_dw_folha
from src.transformation.cadastro_processor import process_cadastro_for_sheets
from src.transformation.folha_processor import process_folha_for_sheets
from src.ingestion.normalizer import clean_currency

# 1. Carrega base original do Google Sheets (Linha de base: 07/2026)
client = gspread.service_account(filename='acaua-web-4898dee734cb.json')
sheet_orig = client.open_by_key('1gRG-x5WMk_BMxPjQYXuNN4Ym4wJivlVv0pu7RLRUqgY')

ws_cad_orig = sheet_orig.worksheet("BD_Cadastro")
data_cad_orig = ws_cad_orig.get_all_values()
df_cad_orig = pd.DataFrame(data_cad_orig[1:], columns=data_cad_orig[0])

ws_folha_orig = sheet_orig.worksheet("BD_Folha")
data_folha_orig = ws_folha_orig.get_all_values()
df_folha_orig = pd.DataFrame(data_folha_orig[1:], columns=data_folha_orig[0])

# 2. Carrega e processa dados do novo mês DW (08/2026)
bd_file, folha_file = find_latest_dw_files("import")
df_raw_dw_cad = parse_dw_cadastro(bd_file)
df_raw_dw_folha = parse_dw_folha(folha_file)

df_cad_novo = process_cadastro_for_sheets(df_raw_dw_cad)
df_folha_novo = process_folha_for_sheets(df_raw_dw_folha)

# 3. Análise de Mudanças Cadastrais
mats_orig = set(df_cad_orig['Matricula'].str.strip()) - {''}
mats_novo = set(df_cad_novo['Matricula'].str.strip()) - {''}

novos_servidores = mats_novo - mats_orig
servidores_saida = mats_orig - mats_novo
servidores_comuns = mats_orig.intersection(mats_novo)

# Mudanças de Cargo / Símbolo / Lotação entre servidores comuns
df_orig_indexed = df_cad_orig.set_index('Matricula')
df_novo_indexed = df_cad_novo.set_index('Matricula')

mudancas_cargo = []
for mat in servidores_comuns:
    c_orig = df_orig_indexed.loc[mat, 'Cargo'] if 'Cargo' in df_orig_indexed.columns else ''
    c_novo = df_novo_indexed.loc[mat, 'Cargo'] if 'Cargo' in df_novo_indexed.columns else ''
    nome = df_orig_indexed.loc[mat, 'Nome'] if 'Nome' in df_orig_indexed.columns else ''
    
    if c_orig and c_novo and str(c_orig).strip() != str(c_novo).strip():
        mudancas_cargo.append({
            'Matricula': mat,
            'Nome': nome,
            'Cargo Anterior': c_orig,
            'Cargo Novo': c_novo
        })

# 4. Análise de Variação de Folha de Pagamento
tot_folha_orig = df_folha_orig['VALOR'].apply(clean_currency).sum()
tot_folha_novo = df_folha_novo['VALOR'].apply(clean_currency).sum()
var_folha_abs = tot_folha_novo - tot_folha_orig
var_folha_pct = (var_folha_abs / tot_folha_orig * 100) if tot_folha_orig > 0 else 0

# 5. Imprime Relatório Consolidado
print("==========================================================================")
print("     RELATÓRIO DE AUDITORIA E IMPACTO DE MUDANÇAS (DW → SHEETS)")
print("==========================================================================")
print(f"Competência Base (Anterior): 07/2026")
print(f"Competência Nova (DW Import): 08/2026")
print("--------------------------------------------------------------------------")
print(f"📊 CADASTRO DE SERVIDORES:")
print(f"  - Servidores na Base Anterior: {len(mats_orig)}")
print(f"  - Servidores na Nova Base DW:  {len(mats_novo)}")
print(f"  - 🟢 Ingressos / Novos Servidores: {len(novos_servidores)}")
print(f"  - 🔴 Exonerações / Ausentes:        {len(servidores_saida)}")
print(f"  - 🔄 Alterações de Cargo / Função: {len(mudancas_cargo)}")

print("\n💰 FOLHA DE PAGAMENTO:")
print(f"  - Total Folha Anterior (07/2026): R$ {tot_folha_orig:,.2f}")
print(f"  - Total Folha Nova (08/2026):     R$ {tot_folha_novo:,.2f}")
print(f"  - Variação Bruta:                 R$ {var_folha_abs:,.2f} ({var_folha_pct:+.2f}%)")

if mudancas_cargo:
    print("\n📋 DETALHAMENTO DE MUDANÇAS DE CARGO / FUNÇÃO (Amostra):")
    for item in mudancas_cargo[:5]:
        print(f"  • Matrícula {item['Matricula']} ({item['Nome']}): '{item['Cargo Anterior']}' ➔ '{item['Cargo Novo']}'")

print("==========================================================================")
