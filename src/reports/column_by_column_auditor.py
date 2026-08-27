import pandas as pd
import numpy as np
from typing import Dict, List, Any

def fix_encoding(text: Any) -> str:
    if text is None:
        return ""
    if isinstance(text, pd.Series):
        text = text.iloc[0] if not text.empty else ""
    if pd.isna(text):
        return ""
    s = str(text).strip()
    try:
        return s.encode('latin1').decode('utf-8')
    except:
        return s

def compare_dataframes_column_by_column(
    df_base: pd.DataFrame,
    df_novo: pd.DataFrame,
    key_col: str = 'Matricula',
    tab_name: str = 'BD_Cadastro'
) -> Dict[str, Any]:
    """
    Realiza a auditoria célula a célula, coluna por coluna, entre dois DataFrames.
    """
    df1 = df_base.copy()
    df2 = df_novo.copy()

    # Normaliza chaves
    df1[key_col] = df1[key_col].astype(str).str.strip()
    df2[key_col] = df2[key_col].astype(str).str.strip()

    all_columns = [c for c in df1.columns if c in df2.columns]

    # Se for BD_Cadastro (1 linha por Matrícula)
    if tab_name == 'BD_Cadastro':
        df1_idx = df1.set_index(key_col)
        df2_idx = df2.set_index(key_col)
        common_keys = sorted(list(set(df1_idx.index).intersection(set(df2_idx.index))))

        col_audit_results = []
        for idx_col, col_name in enumerate(all_columns):
            if col_name == key_col:
                continue

            diff_count = 0
            diff_samples = []

            for key in common_keys:
                raw1 = df1_idx.loc[key, col_name] if col_name in df1_idx.columns else ""
                raw2 = df2_idx.loc[key, col_name] if col_name in df2_idx.columns else ""

                val1_str = fix_encoding(raw1)
                val2_str = fix_encoding(raw2)

                if val1_str != val2_str and (val1_str != "" or val2_str != ""):
                    diff_count += 1
                    if len(diff_samples) < 5:
                        raw_nome = df1_idx.loc[key, 'Nome'] if 'Nome' in df1_idx.columns else ""
                        diff_samples.append({
                            'Matricula': key,
                            'Nome': fix_encoding(raw_nome),
                            'Anterior (07/2026)': val1_str,
                            'Novo (08/2026)': val2_str
                        })

            pct_change = (diff_count / len(common_keys) * 100) if common_keys else 0.0
            col_audit_results.append({
                'col_index': idx_col,
                'col_name': col_name,
                'diff_count': diff_count,
                'total_compared': len(common_keys),
                'pct_change': pct_change,
                'samples': diff_samples
            })

        return {
            'tab_name': tab_name,
            'total_rows_compared': len(common_keys),
            'column_results': col_audit_results
        }

    # Se for BD_Folha (múltiplos lançamentos por Matrícula)
    else:
        tot_rows_1 = len(df1)
        tot_rows_2 = len(df2)
        col_audit_results = []

        for idx_col, col_name in enumerate(all_columns):
            s1 = df1[col_name].apply(fix_encoding)
            s2 = df2[col_name].apply(fix_encoding)
            
            min_len = min(len(s1), len(s2))
            diff_count = sum(s1.iloc[:min_len].values != s2.iloc[:min_len].values) + abs(len(s1) - len(s2))
            pct_change = (diff_count / max(len(s1), 1)) * 100

            samples = []
            if diff_count > 0:
                for i in range(min(min_len, 50)):
                    if s1.iloc[i] != s2.iloc[i]:
                        mat = df1['Matricula'].iloc[i] if 'Matricula' in df1.columns else f"Linha {i}"
                        nome = df1['Nome'].iloc[i] if 'Nome' in df1.columns else ""
                        samples.append({
                            'Matricula': str(mat),
                            'Nome': fix_encoding(nome),
                            'Anterior (07/2026)': s1.iloc[i],
                            'Novo (08/2026)': s2.iloc[i]
                        })
                        if len(samples) >= 5:
                            break

            col_audit_results.append({
                'col_index': idx_col,
                'col_name': col_name,
                'diff_count': diff_count,
                'total_compared': max(tot_rows_1, tot_rows_2),
                'pct_change': pct_change,
                'samples': samples
            })

        return {
            'tab_name': tab_name,
            'total_rows_compared': max(tot_rows_1, tot_rows_2),
            'column_results': col_audit_results
        }

def format_column_audit_markdown(audit_summary: Dict[str, Any]) -> str:
    tab_name = audit_summary['tab_name']
    total_rows = audit_summary['total_rows_compared']
    results = audit_summary['column_results']

    md_lines = [
        f"# 🔎 Relatório Detalhado de Comparação Coluna por Coluna: `{tab_name}`",
        "",
        f"- **Total de Servidores / Registros Comparados**: `{total_rows:,}`",
        f"- **Total de Colunas Analisadas**: `{len(results)}`",
        "",
        "## 📑 Resumo de Alterações por Coluna",
        "",
        "| Coluna # | Nome da Coluna | Registros Alterados | % Alterado | Status |",
        "|---|---|---|---|---|"
    ]

    cols_with_diffs = []

    for res in results:
        idx = res['col_index']
        name = res['col_name']
        diffs = res['diff_count']
        pct = res['pct_change']

        status = "🔴 **Alterada**" if diffs > 0 else "🟢 Sem Alteração"
        md_lines.append(f"| Col {idx:02d} | `{name}` | `{diffs}` / {total_rows} | `{pct:.2f}%` | {status} |")

        if diffs > 0:
            cols_with_diffs.append(res)

    md_lines.append("")

    if cols_with_diffs:
        md_lines.append("## 🔍 Detalhamento das Colunas com Alterações (Amostras Antes vs Depois)")
        md_lines.append("")

        for col_res in cols_with_diffs:
            c_name = col_res['col_name']
            c_idx = col_res['col_index']
            c_diffs = col_res['diff_count']

            md_lines.append(f"### 📌 Coluna {c_idx:02d}: `{c_name}` ({c_diffs} alterações)")
            md_lines.append("| Matrícula | Nome | Anterior (07/2026) | Novo (08/2026) |")
            md_lines.append("|---|---|---|---|")

            for s in col_res['samples']:
                md_lines.append(f"| {s['Matricula']} | {s['Nome']} | `{s['Anterior (07/2026)']}` | `{s['Novo (08/2026)']}` |")

            md_lines.append("")

    return "\n".join(md_lines)
