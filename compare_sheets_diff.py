import gspread
import pandas as pd
import json

json_creds = 'acaua-web-4898dee734cb.json'
orig_id = '1gRG-x5WMk_BMxPjQYXuNN4Ym4wJivlVv0pu7RLRUqgY'
test_id = '1KujGsjeJFgCdmPy6jt1MddPxrWEkS1EDYj9Tk4eGAqs'

client = gspread.service_account(filename=json_creds)

sheet_orig = client.open_by_key(orig_id)
sheet_test = client.open_by_key(test_id)

print(f"Original Sheet Title: '{sheet_orig.title}'")
print(f"Test Copy Sheet Title: '{sheet_test.title}'")

diff_report = {}

for ws_orig in sheet_orig.worksheets():
    title = ws_orig.title
    print(f"\n--- Comparing Tab: '{title}' ---")
    try:
        ws_test = sheet_test.worksheet(title)
    except Exception as e:
        print(f"Tab '{title}' missing in test sheet!")
        continue

    data_orig = ws_orig.get_all_values()
    data_test = ws_test.get_all_values()

    rows_orig = len(data_orig)
    rows_test = len(data_test)
    cols_orig = len(data_orig[0]) if data_orig else 0
    cols_test = len(data_test[0]) if data_test else 0

    print(f"  Original: {rows_orig} rows x {cols_orig} cols")
    print(f"  Test Copy: {rows_test} rows x {cols_test} cols")

    headers_orig = data_orig[0] if data_orig else []
    headers_test = data_test[0] if data_test else []

    if headers_orig != headers_test:
        print(f"  ⚠️ Header Difference in '{title}':")
        print(f"    Orig ({len(headers_orig)}): {headers_orig[:8]}")
        print(f"    Test ({len(headers_test)}): {headers_test[:8]}")

    sample_orig = data_orig[1][:5] if len(data_orig) > 1 else []
    sample_test = data_test[1][:5] if len(data_test) > 1 else []
    print(f"  Sample Row 2 Orig: {sample_orig}")
    print(f"  Sample Row 2 Test: {sample_test}")

    diff_report[title] = {
        "orig_rows": rows_orig,
        "test_rows": rows_test,
        "orig_cols": cols_orig,
        "test_cols": cols_test,
        "headers_orig": headers_orig[:10],
        "headers_test": headers_test[:10]
    }

with open('sheets_diff_analysis.json', 'w', encoding='utf-8') as f:
    json.dump(diff_report, f, ensure_ascii=False, indent=2)

print("\nComparison completed. Saved to sheets_diff_analysis.json")
