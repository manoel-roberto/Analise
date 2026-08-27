import quopri
from lxml import html
import pandas as pd
import gspread

# Load raw DW file bd-.08.2026.xls
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

dw_headers = dw_rows[2]
df_dw = pd.DataFrame(dw_rows[3:], columns=[f"col_{i}_{h}" for i, h in enumerate(dw_headers)])

print("=== DW RAW HEADERS (57 cols) ===")
for i, h in enumerate(dw_headers):
    print(f"DW Col {i:02d}: {h}")

# Load Original BD_Cadastro headers
client = gspread.service_account(filename='acaua-web-4898dee734cb.json')
ws_orig = client.open_by_key('1gRG-x5WMk_BMxPjQYXuNN4Ym4wJivlVv0pu7RLRUqgY').worksheet("BD_Cadastro")
orig_headers = ws_orig.get_all_values()[0]

print("\n=== BD_CADASTRO TARGET HEADERS (64 cols) ===")
for i, h in enumerate(orig_headers):
    print(f"Target Col {i:02d}: {h}")
