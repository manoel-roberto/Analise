# Learned Lessons & Technical Pitfalls Log

## 1. DW Export MHTML Parsing
- **Issue**: DW export files ending in `.xls` (`bd-MM.YYYY.xls` and `folha-MM.YYYY.xls`) are HTML files encoded in `quoted-printable` (`quopri`).
- **Root Cause**: Passing the raw `.xls` directly to `pandas.read_excel` or `pandas.read_html` causes `ValueError: invalid literal for int() with base 10: '3D2'`.
- **Fix**: Decode binary bytes with `quopri.decodestring(content).decode('latin1', errors='ignore')` and parse HTML with `lxml.html.fromstring`.

## 2. Google Sheets API JSON NaN Serialization
- **Issue**: `requests.exceptions.InvalidJSONError: Out of range float values are not JSON compliant: nan`.
- **Root Cause**: `gspread` serializes python/pandas DataFrames to JSON before HTTP POST/PUT. Python `float('nan')` is not JSON compliant.
- **Fix**: Replace all `np.nan` and `float('nan')` with empty string `""` using `df.fillna('')` and string sanitation before passing matrix to `ws.update()`.

## 3. Data Grain & VLOOKUP Formula Integrity in `BD_Cadastro`
- **Issue**: Overwriting `BD_Cadastro` with raw 13.206 rows from `bd-.08.2026.xls` broke dependent sheets (`Analise_Simulacao`, `Listagem`, `Visão`) with `#N/A` errors.
- **Root Cause**: `bd-.08.2026.xls` lists historical position entries (13.206 rows), whereas `BD_Cadastro` in Google Sheets has a grain of **1 row per active employee/server (2.120 rows)**. Overwriting changed column offsets and duplicated rows.
- **Fix**: Maintain 1 row per unique Matrícula (2.120 active servers) and exact 64-column order (`Matricula`, `Nome`, `CPF`, `Sexo`, `Aniversário`...) so all VLOOKUPs and Pivot Tables in `Listagem` and `Visão` evaluate cleanly with zero `#N/A` errors.
