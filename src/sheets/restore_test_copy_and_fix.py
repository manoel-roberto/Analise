import gspread
import pandas as pd
import numpy as np

json_creds = 'acaua-web-4898dee734cb.json'
orig_id = '1gRG-x5WMk_BMxPjQYXuNN4Ym4wJivlVv0pu7RLRUqgY'
test_id = '1KujGsjeJFgCdmPy6jt1MddPxrWEkS1EDYj9Tk4eGAqs'

client = gspread.service_account(filename=json_creds)
sheet_orig = client.open_by_key(orig_id)
sheet_test = client.open_by_key(test_id)

print("Restoring test copy tabs from original sheet for comparison...")

# Restore BD_Cadastro, Listagem, Analise_Simulacao, Visão in test copy from original
tabs_to_restore = ["BD_Cadastro", "Listagem", "Analise_Simulacao", "Visão"]

for tab_name in tabs_to_restore:
    ws_orig = sheet_orig.worksheet(tab_name)
    ws_test = sheet_test.worksheet(tab_name)
    
    data = ws_orig.get_all_values()
    ws_test.clear()
    ws_test.update(range_name='A1', values=data)
    print(f"Restored '{tab_name}' ({len(data)} rows x {len(data[0]) if data else 0} cols)")

print("Restoration of test copy completed successfully.")
