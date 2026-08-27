import gspread
import pandas as pd
import quopri
from lxml import html
from io import StringIO

json_creds = 'acaua-web-4898dee734cb.json'
orig_id = '1gRG-x5WMk_BMxPjQYXuNN4Ym4wJivlVv0pu7RLRUqgY'

# 1. Load Original BD_Cadastro for Matrícula 9381641
client = gspread.service_account(filename=json_creds)
ws_orig = client.open_by_key(orig_id).worksheet("BD_Cadastro")
data_orig = ws_orig.get_all_values()

headers_orig = data_orig[0]
df_orig = pd.DataFrame(data_orig[1:], columns=headers_orig)
row_carlos_orig = df_orig[df_orig['Matricula'] == '9381641'].iloc[0]

# 2. Load DW bd-.08.2026.xls for Matrícula 9381641
with open('import/bd-.08.2026.xls', 'rb') as f:
    raw_bd = f.read()

decoded_bd = quopri.decodestring(raw_bd).decode('latin1', errors='ignore')
tree_bd = html.fromstring(decoded_bd)
data_table = max(tree_bd.xpath('//table'), key=lambda t: len(t.xpath('.//tr')))
rows = data_table.xpath('.//tr')

dw_rows = []
for r in rows:
    cells = [c.text_content().strip() for c in r.xpath('.//td | .//th')]
    if cells:
        dw_rows.append(cells)

raw_headers_dw = dw_rows[2]
df_dw = pd.DataFrame(dw_rows[3:])

# Find row for 9381641 (Col 1 is Matrícula/Pessoa)
row_carlos_dw = df_dw[df_dw[1] == '9381641'].iloc[0]

print("=== EXACT MAPPING BETWEEN DW EXPORT AND ORIGINAL BD_CADASTRO ===")
mapping = {}
for i_orig, h_orig in enumerate(headers_orig):
    val_orig = row_carlos_orig[h_orig]
    
    matched_col_dw = None
    for i_dw, val_dw in enumerate(row_carlos_dw.values):
        if str(val_dw).strip() == str(val_orig).strip() and val_orig != '':
            matched_col_dw = i_dw
            break
            
    mapping[h_orig] = matched_col_dw
    print(f"Col {i_orig:02d} [{h_orig}]: Original='{val_orig}' | DW Col={matched_col_dw} (DW Header: '{raw_headers_dw[matched_col_dw] if matched_col_dw is not None and matched_col_dw < len(raw_headers_dw) else 'N/A'}')")
