import gspread
import pandas as pd
from src.ingestion.dw_parser import find_latest_dw_files, parse_dw_cadastro
from src.reports.change_mapper import clean_val

# 1. Carrega base original
client = gspread.service_account(filename='acaua-web-4898dee734cb.json')
orig_id = '1gRG-x5WMk_BMxPjQYXuNN4Ym4wJivlVv0pu7RLRUqgY'
ws_cad = client.open_by_key(orig_id).worksheet("BD_Cadastro")
data_orig = ws_cad.get_all_values()
df_orig = pd.DataFrame(data_orig[1:], columns=data_orig[0])

mats_orig = set(df_orig['Matricula'].apply(clean_val)) - {'', 'nan', 'None'}

# 2. Carrega DW novo
bd_file, _ = find_latest_dw_files("import")
df_raw_dw = parse_dw_cadastro(bd_file)

# No DW export, Coluna 1 é a Matrícula, Coluna 2 é o Nome, Coluna 0 é o CPF, Coluna 20 é o Cargo
df_dw_mats = df_raw_dw.copy()
df_dw_mats['Matricula_Clean'] = df_dw_mats.iloc[:, 1].apply(clean_val)
mats_dw = set(df_dw_mats['Matricula_Clean']) - {'', 'nan', 'None'}

# Detecta novos e saídas
novos_mats = sorted(list(mats_dw - mats_orig))
saida_mats = sorted(list(mats_orig - mats_dw))

print("=== INGRESSOS / NOVOS SERVIDORES EM 08/2026 ===")
print(f"Total Novos Servidores: {len(novos_mats)}")
df_dw_indexed = df_dw_mats.drop_duplicates(subset=['Matricula_Clean']).set_index('Matricula_Clean')

novos_detalhes = []
for m in novos_mats[:15]:
    r = df_dw_indexed.loc[m]
    nome = clean_val(r.iloc[2]) if len(r) > 2 else ""
    cargo = clean_val(r.iloc[20]) if len(r) > 20 else ""
    setor = clean_val(r.iloc[31]) if len(r) > 31 else ""
    print(f"  • Matrícula: {m} | Nome: {nome} | Cargo: {cargo} | Setor: {setor}")
    novos_detalhes.append({'Matricula': m, 'Nome': nome, 'Cargo': cargo, 'Setor': setor})

print("\n=== SERVIDORES AUSENTES / EXONERADOS EM 08/2026 ===")
print(f"Total Servidores Ausentes: {len(saida_mats)}")
df_orig_indexed = df_orig.set_index('Matricula')
saida_detalhes = []
for m in saida_mats[:15]:
    r = df_orig_indexed.loc[m]
    nome = clean_val(r['Nome']) if 'Nome' in r else ""
    cargo = clean_val(r['Cargo']) if 'Cargo' in r else ""
    print(f"  • Matrícula: {m} | Nome: {nome} | Cargo Anterior: {cargo}")
    saida_detalhes.append({'Matricula': m, 'Nome': nome, 'Cargo': cargo})
