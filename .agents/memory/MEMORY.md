# Memory Index

## Mandatory Protocol
- [user] Always read MEMORY.md before executing any project task or routine → user-preferences.md
- [user] Register all execution history, successful routines, and failed attempts (with root causes and fixes) to guarantee 100% reproducibility → user-preferences.md & learned-lessons.md

## Project Domain & Architecture
- [domain] UEFS Budget Impact Study Spreadsheet ("Estudo de Impacto Orçamentário - RTI e GSTU") complete mapping, 10 tabs analysis & Apps Script rules → sheet-mapping-uefs.md
- [eda] Full Exploratory Data Analysis (EDA) & Statistical Index of all 10 worksheets → eda-index-sheet.md
- [dw] DW Exports Exploratory Data Analysis (08/2026: `bd-.08.2026.xls` & `folha-08.2026.xls`), comparison with Google Sheet & automated update pipeline architecture → dw-analysis-082026.md
- [app] DW → Google Sheets Automated Update Application (Python ETL CLI app in `main.py`, `src/ingestion`, `src/transformation`, `src/sheets`, `src/reports`) → README.md & tech-decisions.md
- [pre-import-audit] Automated Pre-Import Audit Reporter (`src/reports/change_mapper.py`, `main.py update/report`) automatically generating Markdown & CSV change reports (`relatorio_mudancas_pre_importacao.md` & `.csv`) BEFORE writing to Google Sheets → tech-decisions.md
- [ui-streamlit] Interactive Web Application UI (`app.py`) built with Streamlit for visual DW files upload, interactive 8-domain audit report preview, and one-click Google Sheets update execution → app.py & README.md

## Project Conventions & Setup
- [project] Always create a new dedicated branch for major code changes → project-conventions.md
- [project] AG Kit only supports Gemini CLI and Google Antigravity (not other AI coding tools) → project-conventions.md
- [project] Component metadata uses SemVer while toolkit releases use CalVer → tech-decisions.md

## Infrastructure & Tooling Installed
- [tech] Toolkits: AG Kit (vudovn/ag-kit) + Spec Kit (github/spec-kit with `agy` integration) → tech-decisions.md
- [tech] Skills: `data-exploration-profiling` (v1.1.0), `explore-data`, `profiling-tables` → tech-decisions.md

## Learned Lessons & Failed Routines
- [lessons] Spec Kit integration flag for Antigravity is `--integration agy` (`antigravity` fails) → learned-lessons.md
- [lessons] Python virtualenv pip path is `.venv/bin/pip` → learned-lessons.md
- [lessons] Non-interactive flags (`--non-interactive -f`) must be used for CLI initializations → learned-lessons.md
- [lessons] DW exports (`.xls`) are MHTML/quopri HTML tables requiring `quopri.decodestring` + `lxml` parser → learned-lessons.md
- [lessons] Google Sheets API JSON serialization requires replacing all `float('nan')` with empty string `""` before sending `gspread` updates → learned-lessons.md
- [lessons] Exclusive update policy for `BD_Cadastro` and `BD_Folha` preserves all formulas, dynamic reports, and pivot tables in Google Sheets → learned-lessons.md
- [lessons] Column-by-column cell auditing handles scalar Series vs multiple rubrica rows using `compare_dataframes_column_by_column` → learned-lessons.md
- [lessons] Pre-import automated audit pipeline generates `relatorio_mudancas_pre_importacao.md` and `.csv` automatically BEFORE any update command writes to Google Sheets → learned-lessons.md
- [lessons] Streamlit dashboard running on port 8501 (`.venv/bin/streamlit run app.py`) allows non-technical users to review audit reports visually and confirm Google Sheets updates safely → learned-lessons.md
