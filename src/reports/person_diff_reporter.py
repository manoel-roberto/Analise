import pandas as pd
import numpy as np
from typing import List, Dict, Any
from ..ingestion.normalizer import clean_currency

def fix_str(val: Any) -> str:
    if val is None or pd.isna(val):
        return ""
    if isinstance(val, pd.Series):
        val = val.iloc[0] if not val.empty else ""
    s = str(val).strip()
    try:
        return s.encode('latin1').decode('utf-8')
    except:
        return s

def build_person_by_person_diff_report(
    df_cad_orig: pd.DataFrame,
    df_cad_novo: pd.DataFrame,
    df_folha_orig: pd.DataFrame,
    df_folha_novo: pd.DataFrame
) -> List[Dict[str, Any]]:
    """
    Compara pessoa por pessoa (Matrícula) todos os campos de Lugar, Função, Cargo e Folha de Pagamento,
    registrando individualmente cada valor que teve alteração entre 07/2026 e 08/2026.
    """
    diff_records = []

    # Prepara Cadastro
    df_cad_1 = df_cad_orig.copy()
    df_cad_2 = df_cad_novo.copy()
    df_cad_1['Matricula'] = df_cad_1['Matricula'].apply(fix_str)
    df_cad_2['Matricula'] = df_cad_2['Matricula'].apply(fix_str)

    df_cad_1_idx = df_cad_1.set_index('Matricula')
    df_cad_2_idx = df_cad_2.set_index('Matricula')

    mats_1 = set(df_cad_1['Matricula']) - {'', 'nan', 'None'}
    mats_2 = set(df_cad_2['Matricula']) - {'', 'nan', 'None'}
    all_mats = sorted(list(mats_1.union(mats_2)))

    # Agrupa Folha por Matrícula
    def aggregate_folha(df_folha: pd.DataFrame) -> Dict[str, Dict[str, float]]:
        df = df_folha.copy()
        df['Matricula'] = df['Matricula'].apply(fix_str)
        if 'VALOR' in df.columns:
            df['VALOR_NUM'] = df['VALOR'].apply(clean_currency)
        else:
            df['VALOR_NUM'] = 0.0

        folha_map = {}
        for mat, group in df.groupby('Matricula'):
            if not mat: continue
            prov = group[group['Tipo'].astype(str).str.lower() == 'vantagens']['VALOR_NUM'].sum() if 'Tipo' in group.columns else group['VALOR_NUM'].sum()
            desc = group[group['Tipo'].astype(str).str.lower() == 'descontos']['VALOR_NUM'].sum() if 'Tipo' in group.columns else 0.0
            folha_map[mat] = {'proventos': prov, 'descontos': desc, 'liquido': prov - desc}
        return folha_map

    folha_map_1 = aggregate_folha(df_folha_orig)
    folha_map_2 = aggregate_folha(df_folha_novo)

    cols_cad = [c for c in df_cad_1.columns if c in df_cad_2.columns and c != 'Matricula']

    # Categorias de campos para classificação clara no relatório
    CAMPOS_LUGAR = {'Unid. organizacional', 'Sigla. Unid. organizacional', 'Subárea de RH', 'Área RecursosHumanos'}
    CAMPOS_FUNCAO = {'Cargo', 'Cargo_tmp', 'Símbolo Do cargo', 'Tipo de Cargo', 'Grupo de empregados'}
    CAMPOS_CARGO_EFETIVO = {'Cargo Efetivo', 'Cargo Origem', 'Cargo Amplo', 'Nível salarial Efetivo', 'Classe do agente'}

    for mat in all_mats:
        in_1 = mat in df_cad_1_idx.index
        in_2 = mat in df_cad_2_idx.index

        nome_1 = fix_str(df_cad_1_idx.loc[mat, 'Nome']) if in_1 and 'Nome' in df_cad_1_idx.columns else ""
        nome_2 = fix_str(df_cad_2_idx.loc[mat, 'Nome']) if in_2 and 'Nome' in df_cad_2_idx.columns else ""
        nome = nome_2 if nome_2 else nome_1

        # Case 1: Servidor Novo (Ingresso)
        if not in_1 and in_2:
            cargo = fix_str(df_cad_2_idx.loc[mat, 'Cargo']) if 'Cargo' in df_cad_2_idx.columns else ""
            setor = fix_str(df_cad_2_idx.loc[mat, 'Sigla. Unid. organizacional']) if 'Sigla. Unid. organizacional' in df_cad_2_idx.columns else ""
            diff_records.append({
                'Matricula': mat,
                'Nome': nome,
                'Categoria da Mudança': 'Ingresso / Novo Servidor',
                'Campo Alterado': 'Situação na Base',
                'Valor Anterior (07/2026)': 'Não Constava',
                'Valor Novo (08/2026)': 'Admitido / Ativo',
                'Detalhamento / Obs': f"Novo cadastro em {setor} (Cargo: {cargo})"
            })
            continue

        # Case 2: Servidor Ausente (Exoneração/Saída)
        if in_1 and not in_2:
            cargo = fix_str(df_cad_1_idx.loc[mat, 'Cargo']) if 'Cargo' in df_cad_1_idx.columns else ""
            diff_records.append({
                'Matricula': mat,
                'Nome': nome,
                'Categoria da Mudança': 'Desligamento / Ausente',
                'Campo Alterado': 'Situação na Base',
                'Valor Anterior (07/2026)': 'Ativo',
                'Valor Novo (08/2026)': 'Não Consta no DW',
                'Detalhamento / Obs': f"Cargo anterior: {cargo}"
            })
            continue

        # Case 3: Servidor presente nas duas bases - compara campo por campo
        for col in cols_cad:
            v1 = fix_str(df_cad_1_idx.loc[mat, col])
            v2 = fix_str(df_cad_2_idx.loc[mat, col])

            if v1 != v2 and (v1 != "" or v2 != ""):
                cat = 'Alteração Cadastral'
                if col in CAMPOS_LUGAR:
                    cat = 'Mudança de Lugar / Lotação'
                elif col in CAMPOS_FUNCAO:
                    cat = 'Mudança de Função / Símbolo'
                elif col in CAMPOS_CARGO_EFETIVO:
                    cat = 'Mudança de Cargo Efetivo / Origem'

                diff_records.append({
                    'Matricula': mat,
                    'Nome': nome,
                    'Categoria da Mudança': cat,
                    'Campo Alterado': col,
                    'Valor Anterior (07/2026)': v1,
                    'Valor Novo (08/2026)': v2,
                    'Detalhamento / Obs': 'Dado alterado no DW'
                })

        # Compara variações na Folha de Pagamento
        f1 = folha_map_1.get(mat, {'proventos': 0.0, 'descontos': 0.0, 'liquido': 0.0})
        f2 = folha_map_2.get(mat, {'proventos': 0.0, 'descontos': 0.0, 'liquido': 0.0})

        if abs(f1['proventos'] - f2['proventos']) > 0.05:
            diff_prov = f2['proventos'] - f1['proventos']
            diff_records.append({
                'Matricula': mat,
                'Nome': nome,
                'Categoria da Mudança': 'Variação Salarial (Folha)',
                'Campo Alterado': 'Total Proventos (Bruto)',
                'Valor Anterior (07/2026)': f"R$ {f1['proventos']:,.2f}",
                'Valor Novo (08/2026)': f"R$ {f2['proventos']:,.2f}",
                'Detalhamento / Obs': f"Variação: R$ {diff_prov:,.2f}"
            })

    return diff_records

def format_person_diff_markdown(diff_records: List[Dict[str, Any]]) -> str:
    """Formata o relatório de alterações por pessoa em Markdown."""
    total_diffs = len(diff_records)
    unique_mats = len(set(r['Matricula'] for r in diff_records))

    df_rec = pd.DataFrame(diff_records)
    cats_count = df_rec['Categoria da Mudança'].value_counts().to_dict() if not df_rec.empty else {}

    md_lines = [
        "# 👤 Relatório de Alterações de Lugar, Função, Cargo e Salário por Servidor",
        "",
        f"- **Total de Servidores com Mudanças**: `{unique_mats:,}`",
        f"- **Total de Itens Alterados**: `{total_diffs:,}`",
        "",
        "## 📊 Resumo por Categoria de Mudança:",
    ]

    for cat, count in cats_count.items():
        md_lines.append(f"- **{cat}**: `{count}` alterações")

    md_lines.extend([
        "",
        "## 📑 Detalhamento por Servidor (Amostra dos Registros):",
        "",
        "| Matrícula | Nome | Categoria da Mudança | Campo Alterado | Valor Anterior (07/2026) | Valor Novo (08/2026) | Observação |",
        "|---|---|---|---|---|---|---|"
    ])

    for r in diff_records[:120]:
        md_lines.append(
            f"| {r['Matricula']} | {r['Nome']} | **{r['Categoria da Mudança']}** | `{r['Campo Alterado']}` | `{r['Valor Anterior (07/2026)']}` | `{r['Valor Novo (08/2026)']}` | {r['Detalhamento / Obs']} |"
        )

    if total_diffs > 120:
        md_lines.append(f"\n*... e mais {total_diffs - 120} itens alterados registrados no arquivo CSV completo.*")

    return "\n".join(md_lines)
