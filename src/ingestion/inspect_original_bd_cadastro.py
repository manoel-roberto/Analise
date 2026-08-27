import gspread
import pandas as pd

json_creds = 'acaua-web-4898dee734cb.json'
orig_id = '1gRG-x5WMk_BMxPjQYXuNN4Ym4wJivlVv0pu7RLRUqgY'

client = gspread.service_account(filename=json_creds)
sheet_orig = client.open_by_key(orig_id)
ws_bd = sheet_orig.worksheet("BD_Cadastro")

data = ws_bd.get_all_values()
headers = data[0]
row2 = data[1]

print("=== ORIGINAL BD_CADASTRO COLUMNS & SAMPLE VALUES ===")
for idx, (h, val) in enumerate(zip(headers, row2)):
    print(f"Col {idx:02d} [{h}]: {val}")

# Check unique matriculas in original BD_Cadastro
df_orig = pd.DataFrame(data[1:], columns=headers)
print(f"\nOriginal BD_Cadastro Shape: {df_orig.shape}")
print(f"Unique Matrículas: {df_orig['Matricula'].nunique()}")
