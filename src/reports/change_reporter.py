import os
import pandas as pd
import numpy as np
from typing import Dict, Any, List
from ..ingestion.normalizer import clean_currency

def fix_text_encoding(text: Any) -> str:
    if text is None or pd.isna(text):
        return ""
    if isinstance(text, pd.Series):
        text = text.iloc[0] if not text.empty else ""
    s = str(text).strip()
    try:
        return s.encode('latin1').decode('utf-8')
    except:
        return s

def generate_pre_import_audit_report(
    df_cad_orig: pd.DataFrame,
    df_cad_novo: pd.DataFrame,
    df_folha_orig: pd.DataFrame,
    df_folha_novo: pd.DataFrame,
    output_md_path: str = "relatorio_mudancas_pre_importacao.md",
    output_csv_path: str = "relatorio_mudancas_pre_importacao.csv"
) -> Dict[str, Any]:
    """
    Gera automaticamente um Relatório Executivo de Pré-Importação (DW vs Google Sheets)
    detalhando Função/Símbolo, Vínculo, Ingressos, Saídas e Folha de Pagamento.
    """
    df_c1 = df_cad_orig.copy()
    df_c2 = df_cad_novo.copy()
    df_c1['Matricula'] = df_c1['Matricula'].apply(fix_text_encoding)
    df_c2['Matricula'] = df_c2['Matricula'].apply(fix_text_encoding)

    df_c1_idx = df_c1.set_index('Matricula')
    df_c2_idx = df_c2.set_index('Matricula')

    mats_1 = set(df_c1['Matricula']) - {'', 'nan', 'None'}
    mats_2 = set(df_c2['Matricula']) - {'', 'nan', 'None'}

    novos_mats = sorted(list(mats_2 - mats_1))
    saida_mats = sorted(list(mats_1 - mats_2))
    comuns_mats = sorted(list(mats_1.intersection(mats_2)))

    # Agrupa Folha por Matrícula
    def agg_folha(df_folha: pd.DataFrame) -> Dict[str, Dict[str, float]]:
        df = df_folha.copy()
        df['Matricula'] = df['Matricula'].apply(fix_text_encoding)
        df['VALOR_NUM'] = df['VALOR'].apply(clean_currency) if 'VALOR' in df.columns else 0.0
        folha_map = {}
        for mat, group in df.groupby('Matricula'):
            if not mat: continue
            prov = group[group['Tipo'].astype(str).str.lower() == 'vantagens']['VALOR_NUM'].sum() if 'Tipo' in group.columns else group['VALOR_NUM'].sum()
            desc = group[group['Tipo'].astype(str).str.lower() == 'descontos']['VALOR_NUM'].sum() if 'Tipo' in group.columns else 0.0
            folha_map[mat] = {'proventos': prov, 'descontos': desc, 'liquido': prov - desc}
        return folha_map

    folha_map_1 = agg_folha(df_folha_orig)
    folha_map_2 = agg_folha(df_folha_novo)

    all_diff_records = []

    # 1. Mudanças de Função / Símbolo / Cargo e Vínculo
    funcao_diffs = []
    vinculo_diffs = []
    lugar_diffs = []

    for m in comuns_mats:
        nome = fix_text_encoding(df_c1_idx.loc[m, 'Nome']) if 'Nome' in df_c1_idx.columns else ""
        
        # Cargo / Função / Símbolo
        c1 = fix_text_encoding(df_c1_idx.loc[m, 'Cargo']) if 'Cargo' in df_c1_idx.columns else ""
        c2 = fix_text_encoding(df_c2_idx.loc[m, 'Cargo']) if 'Cargo' in df_c2_idx.columns else ""
        
        if c1 and c2 and c1.upper() != c2.upper():
            rec = {
                'Matricula': m,
                'Nome': nome,
                'Categoria da Mudança': 'Mudança de Função / Símbolo',
                'Campo Alterado': 'Cargo / Função',
                'Valor Anterior (Base)': c1,
                'Valor Novo (DW)': c2,
                'Detalhamento / Obs': 'Mudança de cargo/função comissionada no DW'
            }
            funcao_diffs.append(rec)
            all_diff_records.append(rec)

        # Relação de emprego / Vínculo
        v1 = fix_text_encoding(df_c1_idx.loc[m, 'Relação de emprego']) if 'Relação de emprego' in df_c1_idx.columns else ""
        v2 = fix_text_encoding(df_c2_idx.loc[m, 'Relação de emprego']) if 'Relação de emprego' in df_c2_idx.columns else ""
        if v1 and v2 and v1.upper() != v2.upper():
            rec = {
                'Matricula': m,
                'Nome': nome,
                'Categoria da Mudança': 'Alteração Cadastral / Vínculo',
                'Campo Alterado': 'Relação de emprego',
                'Valor Anterior (Base)': v1,
                'Valor Novo (DW)': v2,
                'Detalhamento / Obs': 'Alteração de status do vínculo'
            }
            vinculo_diffs.append(rec)
            all_diff_records.append(rec)

        # Lugar / Unidade Organizacional
        u1 = fix_text_encoding(df_c1_idx.loc[m, 'Sigla. Unid. organizacional']) if 'Sigla. Unid. organizacional' in df_c1_idx.columns else ""
        u2 = fix_text_encoding(df_c2_idx.loc[m, 'Sigla. Unid. organizacional']) if 'Sigla. Unid. organizacional' in df_c2_idx.columns else ""
        if u1 and u2 and u1.upper() != u2.upper():
            rec = {
                'Matricula': m,
                'Nome': nome,
                'Categoria da Mudança': 'Mudança de Lugar / Setor',
                'Campo Alterado': 'Sigla. Unid. organizacional',
                'Valor Anterior (Base)': u1,
                'Valor Novo (DW)': u2,
                'Detalhamento / Obs': 'Movimentação de setor'
            }
            lugar_diffs.append(rec)
            all_diff_records.append(rec)

    # 2. Ingressos
    novos_servidores = []
    for m in novos_mats:
        nome = fix_text_encoding(df_c2_idx.loc[m, 'Nome']) if 'Nome' in df_c2_idx.columns else ""
        cargo = fix_text_encoding(df_c2_idx.loc[m, 'Cargo']) if 'Cargo' in df_c2_idx.columns else ""
        rec = {
            'Matricula': m,
            'Nome': nome,
            'Categoria da Mudança': 'Ingresso / Novo Servidor',
            'Campo Alterado': 'Situação na Base',
            'Valor Anterior (Base)': 'Não Constava',
            'Valor Novo (DW)': 'Admitido / Ativo',
            'Detalhamento / Obs': f"Cargo: {cargo}"
        }
        novos_servidores.append(rec)
        all_diff_records.append(rec)

    # 3. Desligamentos
    saida_servidores = []
    for m in saida_mats:
        nome = fix_text_encoding(df_c1_idx.loc[m, 'Nome']) if 'Nome' in df_c1_idx.columns else ""
        cargo = fix_text_encoding(df_c1_idx.loc[m, 'Cargo']) if 'Cargo' in df_c1_idx.columns else ""
        rec = {
            'Matricula': m,
            'Nome': nome,
            'Categoria da Mudança': 'Desligamento / Ausente',
            'Campo Alterado': 'Situação na Base',
            'Valor Anterior (Base)': 'Ativo',
            'Valor Novo (DW)': 'Não Consta no DW',
            'Detalhamento / Obs': f"Cargo anterior: {cargo}"
        }
        saida_servidores.append(rec)
        all_diff_records.append(rec)

    # Totais Folha
    tot_prov_1 = sum(f['proventos'] for f in folha_map_1.values())
    tot_prov_2 = sum(f['proventos'] for f in folha_map_2.values())
    delta_prov = tot_prov_2 - tot_prov_1
    pct_prov = (delta_prov / tot_prov_1 * 100) if tot_prov_1 > 0 else 0.0

    # Formatação do Relatório Markdown Executivo
    md_lines = [
        "# 📊 RELATÓRIO PRÉ-IMPORTAÇÃO: AUDITORIA DE MUDANÇAS E IMPACTO (DW vs BASE ANTERIOR)",
        "",
        "<blockquote>⚠️ <b>Atenção:</b> Este relatório é gerado automaticamente antes de aplicar a importação no Google Sheets. Utilize estas informações para validar todas as movimentações.</blockquote>",
        "",
        "## 📌 Resumo Executivo das Alterações",
        f"- **Servidores na Base Anterior**: `{len(mats_1):,}`",
        f"- **Servidores na Nova Carga DW**: `{len(mats_2):,}`",
        f"- **🎭 Mudanças de Função / Símbolo**: `{len(funcao_diffs)}`",
        f"- **📋 Alterações Cadastrais / Vínculo**: `{len(vinculo_diffs)}`",
        f"- **📍 Mudanças de Lugar / Setor**: `{len(lugar_diffs)}`",
        f"- **🟢 Ingressos / Novos Servidores**: `{len(novos_servidores)}`",
        f"- **🔴 Exonerações / Ausentes**: `{len(saida_servidores)}`",
        f"- **💰 Variação Bruta da Folha**: `R$ {tot_prov_1:,.2f}` ➔ `R$ {tot_prov_2:,.2f}` (Variação: `R$ {delta_prov:,.2f}` | `{pct_prov:+.2f}%`)",
        "",
        "---",
        "",
        "## 🎭 1. Detalhamento de Mudanças de Função / Símbolo",
        ""
    ]

    if funcao_diffs:
        md_lines.append("| Matrícula | Nome | Cargo / Símbolo Anterior | Cargo / Símbolo Novo (DW) | Observação |")
        md_lines.append("|---|---|---|---|---|")
        for r in funcao_diffs:
            md_lines.append(f"| {r['Matricula']} | {r['Nome']} | `{r['Valor Anterior (Base)']}` | `{r['Valor Novo (DW)']}` | {r['Detalhamento / Obs']} |")
    else:
        md_lines.append("*Nenhuma mudança de função ou símbolo detectada.*")
    md_lines.append("")

    md_lines.extend([
        "## 📋 2. Detalhamento de Alterações Cadastrais e de Vínculo",
        ""
    ])

    if vinculo_diffs:
        md_lines.append("| Matrícula | Nome | Campo Alterado | Valor Anterior | Valor Novo (DW) | Observação |")
        md_lines.append("|---|---|---|---|---|---|")
        for r in vinculo_diffs:
            md_lines.append(f"| {r['Matricula']} | {r['Nome']} | `{r['Campo Alterado']}` | `{r['Valor Anterior (Base)']}` | `{r['Valor Novo (DW)']}` | {r['Detalhamento / Obs']} |")
    else:
        md_lines.append("*Nenhuma alteração de vínculo cadastral detectada.*")
    md_lines.append("")

    if novos_servidores:
        md_lines.extend([
            "## 🟢 3. Novos Servidores Admitidos",
            "",
            "| Matrícula | Nome | Cargo | Status |",
            "|---|---|---|---|"
        ])
        for r in novos_servidores[:15]:
            md_lines.append(f"| {r['Matricula']} | {r['Nome']} | `{r['Detalhamento / Obs']}` | 🟢 Novo |")
        md_lines.append("")

    if saida_servidores:
        md_lines.extend([
            "## 🔴 4. Servidores Ausentes / Exonerados",
            "",
            "| Matrícula | Nome | Cargo Anterior | Status |",
            "|---|---|---|---|"
        ])
        for r in saida_servidores[:15]:
            md_lines.append(f"| {r['Matricula']} | {r['Nome']} | `{r['Detalhamento / Obs']}` | 🔴 Ausente |")
        md_lines.append("")

    md_content = "\n".join(md_lines)

    # Exporta relatórios
    if output_md_path:
        with open(output_md_path, 'w', encoding='utf-8') as f:
            f.write(md_content)

    if output_csv_path and all_diff_records:
        df_csv = pd.DataFrame(all_diff_records)
        df_csv.to_csv(output_csv_path, index=False, encoding='utf-8-sig')

    return {
        'num_orig': len(mats_1),
        'num_novo': len(mats_2),
        'funcao_diffs': funcao_diffs,
        'vinculo_diffs': vinculo_diffs,
        'novos': novos_servidores,
        'saidas': saida_servidores,
        'tot_prov_1': tot_prov_1,
        'tot_prov_2': tot_prov_2,
        'delta_prov': delta_prov,
        'pct_prov': pct_prov,
        'md_content': md_content
    }
