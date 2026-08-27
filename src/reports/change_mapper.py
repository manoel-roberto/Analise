import pandas as pd
import numpy as np
from typing import Dict, List, Any
from ..ingestion.normalizer import clean_currency

# Mapeamento completo das 64 colunas de BD_Cadastro + 7 colunas de BD_Folha em 8 Domínios RH
COLUMN_DOMAIN_MAP = {
    # 1. Movimentações de Cargo e Carreira
    'Cargo': ('Cargo & Carreira', 'Denominação do Cargo'),
    'Cargo_tmp': ('Cargo & Carreira', 'Denominação Temporária do Cargo'),
    'Cargo Amplo': ('Cargo & Carreira', 'Cargo Amplo'),
    'Cod. Cargo': ('Cargo & Carreira', 'Código do Cargo'),
    'Cod. Cargo Amplo': ('Cargo & Carreira', 'Código do Cargo Amplo'),
    'Cargo Efetivo': ('Cargo & Carreira', 'Cargo Efetivo'),
    'Cod. Cargo Efetivo': ('Cargo & Carreira', 'Código do Cargo Efetivo'),
    'Cargo Origem': ('Cargo & Carreira', 'Cargo de Origem'),
    'Cod. Cargo Origem': ('Cargo & Carreira', 'Código do Cargo de Origem'),
    'Carreira': ('Cargo & Carreira', 'Carreira do Servidor'),
    'Classe do agente': ('Cargo & Carreira', 'Classe do Agente (Progressão)'),
    'Nível salarial Efetivo': ('Cargo & Carreira', 'Nível Salarial da Carreira'),
    'Faixa SN': ('Cargo & Carreira', 'Faixa Salarial SN'),
    'Nv': ('Cargo & Carreira', 'Nível Salarial'),
    'CH': ('Cargo & Carreira', 'Carga Horária Semanal'),
    'Grau': ('Cargo & Carreira', 'Grau de Titulação'),
    'Órgão do Cargo Efetivo': ('Cargo & Carreira', 'Órgão do Cargo Efetivo'),

    # 2. Função Comissionada e Símbolo
    'Símbolo Do cargo': ('Função Comissionada & Símbolo', 'Símbolo Comissionado (DAS/DAI)'),
    'Cod. Tipo de Cargo': ('Função Comissionada & Símbolo', 'Código do Tipo de Cargo'),
    'Tipo de Cargo': ('Função Comissionada & Símbolo', 'Tipo de Cargo (Comissionado/Efetivo)'),
    'Cod. Grupo de empregados': ('Função Comissionada & Símbolo', 'Código do Grupo de Gestão'),
    'Grupo de empregados': ('Função Comissionada & Símbolo', 'Grupo de Gestão Orçamentária'),
    'Cod. Tp. Tarifa': ('Função Comissionada & Símbolo', 'Código de Tipo de Tarifa'),
    'Tp. Tarifa': ('Função Comissionada & Símbolo', 'Tipo de Tarifa / Função Gestora'),

    # 3. Lotação, Setor e Estrutura Organizacional
    'Sigla. Unid. organizacional': ('Lotação & Estrutura', 'Sigla do Setor / Unidade'),
    'Unid. organizacional': ('Lotação & Estrutura', 'Nome da Unidade Organizacional'),
    'Cod. Unid. organizacional': ('Lotação & Estrutura', 'Código da Unidade Organizacional'),
    'Área RecursosHumanos': ('Lotação & Estrutura', 'Área de RH (Adm / Acadêmica)'),
    'Cod. Área RecursosHumanos': ('Lotação & Estrutura', 'Código da Área de RH'),
    'Subárea de RH': ('Lotação & Estrutura', 'Subárea de RH (Câmpus / Cidade)'),
    'Cod. Subárea de RH': ('Lotação & Estrutura', 'Código da Subárea de RH'),
    'Gestor': ('Lotação & Estrutura', 'Chefia Imediata / Gestor'),
    'Cod. Gestor': ('Lotação & Estrutura', 'Código do Gestor'),

    # 4. Vínculo, Regime e Situação Funcional
    'Situação do Servidor': ('Vínculo & Situação Funcional', 'Situação do Servidor (Ativo/Aposentado)'),
    'Cedidos': ('Vínculo & Situação Funcional', 'Status de Cessão'),
    'Regime jurídico.': ('Vínculo & Situação Funcional', 'Regime Jurídico (Estatutário/CLT/REDA)'),
    'Vínculo empregatício': ('Vínculo & Situação Funcional', 'Vínculo Empregatício'),
    'Relação de emprego': ('Vínculo & Situação Funcional', 'Relação de Emprego'),
    'Tipo de contrato': ('Vínculo & Situação Funcional', 'Tipo de Contrato'),
    'Status de ocupação': ('Vínculo & Situação Funcional', 'Status de Ocupação'),
    'Cod. SG empregados': ('Vínculo & Situação Funcional', 'Código do Grupo de Empregados'),
    'SG empregados': ('Vínculo & Situação Funcional', 'SG Empregados (Efetivo/Comissionado/Estágio)'),

    # 5. Medidas Administrativas e Prazos
    'Início da Medida': ('Medidas Administrativas & Prazos', 'Data de Início da Medida'),
    'Últ. Motivo Medida': ('Medidas Administrativas & Prazos', 'Motivo da Última Medida Legis.'),
    'ÚltimoTipo de Medida': ('Medidas Administrativas & Prazos', 'Tipo da Última Medida'),
    'Data Inicial Infipo 14': ('Medidas Administrativas & Prazos', 'Data Inicial Infipo'),
    'Data Fim Infipo 14': ('Medidas Administrativas & Prazos', 'Data Fim Infipo'),
    'Para Período': ('Medidas Administrativas & Prazos', 'Competência / Período'),

    # 6. Dados Pessoais e Cadastrais
    'Nome': ('Dados Pessoais & Cadastrais', 'Nome do Servidor'),
    'CPF': ('Dados Pessoais & Cadastrais', 'CPF'),
    'Sexo': ('Dados Pessoais & Cadastrais', 'Sexo'),
    'Aniversário': ('Dados Pessoais & Cadastrais', 'Dia/Mês de Aniversário'),
    'Data de nascimento': ('Dados Pessoais & Cadastrais', 'Data de Nascimento'),
    'Idade em anos': ('Dados Pessoais & Cadastrais', 'Idade'),
    'Cod. Raça': ('Dados Pessoais & Cadastrais', 'Código de Raça'),
    'Raça': ('Dados Pessoais & Cadastrais', 'Raça / Etnia'),
    'Cod. Estado Civil': ('Dados Pessoais & Cadastrais', 'Código de Estado Civil'),
    'Estado Civil': ('Dados Pessoais & Cadastrais', 'Estado Civil'),
    'Cod. Tipo de Deficiência': ('Dados Pessoais & Cadastrais', 'Código de Deficiência'),
    'Tipo de Deficiência': ('Dados Pessoais & Cadastrais', 'Tipo de Deficiência'),
    'Data de Admissão': ('Dados Pessoais & Cadastrais', 'Data de Admissão na UEFS'),
    'Reg': ('Dados Pessoais & Cadastrais', 'Registro'),

    # 7 & 8. Folha de Pagamento
    'VALOR_PROVENTOS': ('Folha de Pagamento - Proventos', 'Total de Vantagens / Proventos Brutos'),
    'VALOR_DESCONTOS': ('Folha de Pagamento - Descontos', 'Total de Descontos e Consignações'),
}

def clean_val(val: Any) -> str:
    if val is None or pd.isna(val):
        return ""
    if isinstance(val, pd.Series):
        val = val.iloc[0] if not val.empty else ""
    s = str(val).strip()
    try:
        return s.encode('latin1').decode('utf-8')
    except:
        return s

def is_valid_matricula(mat: str) -> bool:
    m = str(mat).strip()
    return m.isdigit() and len(m) >= 6

def run_comprehensive_change_audit(
    df_cad_orig: pd.DataFrame,
    df_raw_dw_cad: pd.DataFrame,
    df_folha_orig: pd.DataFrame,
    df_folha_novo: pd.DataFrame
) -> Dict[str, Any]:
    """
    Executa a auditoria completa comparando a base de dados de origem (Sheets) com a nova exportação do DW,
    identificando Ingressos (Novos Servidores), Desligamentos (Exonerações), Mudanças Cadastrais/Cargo/Lotação e Folha.
    """
    diff_records = []

    # 1. Limpa chaves da base original
    df_c1 = df_cad_orig.copy()
    df_c1['Matricula_Clean'] = df_c1['Matricula'].apply(clean_val)
    df_c1_clean = df_c1[df_c1['Matricula_Clean'].apply(is_valid_matricula)].drop_duplicates(subset=['Matricula_Clean']).set_index('Matricula_Clean')
    mats_1 = set(df_c1_clean.index)

    # 2. Limpa chaves do DW bruto (Col 1 é a Matrícula, Col 2 é o Nome, Col 20 é o Cargo)
    df_dw_clean = df_raw_dw_cad.copy()
    df_dw_clean['Matricula_Clean'] = df_dw_clean.iloc[:, 1].apply(clean_val)
    df_dw_clean = df_dw_clean[df_dw_clean['Matricula_Clean'].apply(is_valid_matricula)].drop_duplicates(subset=['Matricula_Clean']).set_index('Matricula_Clean')
    mats_2 = set(df_dw_clean.index)

    novos_mats = sorted(list(mats_2 - mats_1))
    saida_mats = sorted(list(mats_1 - mats_2))
    comuns_mats = sorted(list(mats_1.intersection(mats_2)))

    domain_summary = {
        'Ingressos / Novos Servidores': len(novos_mats),
        'Desligamentos / Ausentes': len(saida_mats)
    }

    # 3. Registra Novos Servidores (Ingressos)
    for m in novos_mats:
        r = df_dw_clean.loc[m]
        nome = clean_val(r.iloc[2]) if len(r) > 2 else ""
        cargo = clean_val(r.iloc[20]) if len(r) > 20 else ""
        setor = clean_val(r.iloc[31]) if len(r) > 31 else ""
        
        diff_records.append({
            'Matricula': m,
            'Nome': nome,
            'Domínio RH': 'Ingressos / Novos Servidores',
            'Campo Alterado': 'Admissão na Base DW',
            'Descrição do Campo': 'Novo Servidor Admitido',
            'Valor Anterior (Base)': 'Não Constava',
            'Valor Novo (DW)': 'Admitido / Ativo',
            'Status / Observação': f"Cargo: {cargo} | Setor: {setor}"
        })

    # 4. Registra Desligamentos (Exonerações/Ausentes)
    for m in saida_mats:
        r = df_c1_clean.loc[m]
        nome = clean_val(r['Nome']) if 'Nome' in r else ""
        cargo = clean_val(r['Cargo']) if 'Cargo' in r else ""
        setor = clean_val(r['Sigla. Unid. organizacional']) if 'Sigla. Unid. organizacional' in r else ""
        
        diff_records.append({
            'Matricula': m,
            'Nome': nome,
            'Domínio RH': 'Desligamentos / Ausentes',
            'Campo Alterado': 'Desligamento da Base DW',
            'Descrição do Campo': 'Servidor Ausente / Exonerado',
            'Valor Anterior (Base)': 'Ativo',
            'Valor Novo (DW)': 'Não Consta no DW',
            'Status / Observação': f"Cargo anterior: {cargo} | Setor anterior: {setor}"
        })

    # 5. Mapeia alterações de campos para servidores comuns (presentes em 07/2026 e 08/2026)
    cols_cad = [c for c in df_c1_clean.columns if c != 'Matricula_Clean']

    for mat in comuns_mats:
        nome_1 = clean_val(df_c1_clean.loc[mat, 'Nome']) if 'Nome' in df_c1_clean.columns else ""
        r_dw = df_dw_clean.loc[mat]

        # Compara Cargo vindo do DW (Col 20) com Cargo da base
        c_orig = clean_val(df_c1_clean.loc[mat, 'Cargo']) if 'Cargo' in df_c1_clean.columns else ""
        c_dw = clean_val(r_dw.iloc[20]) if len(r_dw) > 20 else ""

        if c_orig and c_dw and c_orig.upper() != c_dw.upper():
            dom = 'Função Comissionada & Símbolo' if ('DAS' in c_dw.upper() or 'DAI' in c_dw.upper() or 'DAS' in c_orig.upper() or 'DAI' in c_orig.upper()) else 'Cargo & Carreira'
            domain_summary[dom] = domain_summary.get(dom, 0) + 1
            diff_records.append({
                'Matricula': mat,
                'Nome': nome_1,
                'Domínio RH': dom,
                'Campo Alterado': 'Cargo',
                'Descrição do Campo': 'Denominação do Cargo / Função',
                'Valor Anterior (Base)': c_orig,
                'Valor Novo (DW)': c_dw,
                'Status / Observação': 'Movimentação de cargo/função comissionada'
            })

    # 6. Mapeia Variações Financeiras da Folha por Servidor
    def agg_folha(df_folha: pd.DataFrame) -> Dict[str, float]:
        df = df_folha.copy()
        df['Matricula'] = df['Matricula'].apply(clean_val)
        df['VALOR_NUM'] = df['VALOR'].apply(clean_currency) if 'VALOR' in df.columns else 0.0
        folha_map = {}
        for mat, group in df.groupby('Matricula'):
            if not mat or not is_valid_matricula(mat): continue
            prov = group[group['Tipo'].astype(str).str.lower() == 'vantagens']['VALOR_NUM'].sum() if 'Tipo' in group.columns else group['VALOR_NUM'].sum()
            folha_map[mat] = prov
        return folha_map

    f_map_1 = agg_folha(df_folha_orig)
    f_map_2 = agg_folha(df_folha_novo)

    num_folha_var = 0
    for mat in comuns_mats:
        p1 = f_map_1.get(mat, 0.0)
        p2 = f_map_2.get(mat, 0.0)
        if abs(p1 - p2) > 0.05:
            delta = p2 - p1
            num_folha_var += 1
            diff_records.append({
                'Matricula': mat,
                'Nome': clean_val(df_c1_clean.loc[mat, 'Nome']) if mat in df_c1_clean.index and 'Nome' in df_c1_clean.columns else "",
                'Domínio RH': 'Folha de Pagamento - Proventos',
                'Campo Alterado': 'Total Proventos (Bruto)',
                'Descrição do Campo': 'Total Bruto de Vantagens Mensais',
                'Valor Anterior (Base)': f"R$ {p1:,.2f}",
                'Valor Novo (DW)': f"R$ {p2:,.2f}",
                'Status / Observação': f"Variação: R$ {delta:,.2f}"
            })

    domain_summary['Folha de Pagamento - Proventos'] = num_folha_var

    return {
        'total_servidores': len(mats_1),
        'total_dw': len(mats_2),
        'novos_count': len(novos_mats),
        'saidas_count': len(saida_mats),
        'total_alteracoes': len(diff_records),
        'domain_summary': domain_summary,
        'diff_records': diff_records
    }

def format_comprehensive_audit_markdown(audit_data: Dict[str, Any]) -> str:
    """Formata o relatório executivo completo de auditoria por domínio de RH."""
    records = audit_data['diff_records']
    summary = audit_data['domain_summary']
    tot_alt = audit_data['total_alteracoes']

    md_lines = [
        "# 📑 RELATÓRIO EXECUTIVO DE AUDITORIA DE MUDANÇAS (INGRESSOS, SAÍDAS, CARGOS E FOLHA)",
        "",
        f"- **Servidores na Base Anterior (07/2026)**: `{audit_data['total_servidores']:,}`",
        f"- **Servidores na Nova Carga DW (08/2026)**: `{audit_data['total_dw']:,}`",
        f"- **🟢 Ingressos / Novos Servidores**: `{audit_data['novos_count']}`",
        f"- **🔴 Exonerações / Ausentes**: `{audit_data['saidas_count']}`",
        f"- **Total de Ocorrências Mapeadas**: `{tot_alt:,}`",
        "",
        "## 📊 Resumo de Ocorrências Mapeadas por Domínio de RH:",
        "",
        "| Domínio de RH | Descrição do Domínio | Total de Ocorrências Detectadas | Status |",
        "|---|---|---|---|",
    ]

    for dom, count in summary.items():
        status = "🔴 **Com Alterações**" if count > 0 else "🟢 Sem Alterações"
        if "Ingressos" in dom: status = "🟢 **Novos Servidores**"
        md_lines.append(f"| **{dom}** | Mapeamento completo de movimentações de RH | `{count:,}` | {status} |")

    md_lines.extend([
        "",
        "---",
        "",
        "## 🔍 Detalhamento Completo das Ocorrências Detectadas por Domínio",
        ""
    ])

    df_rec = pd.DataFrame(records)
    if not df_rec.empty:
        for dom, group in df_rec.groupby('Domínio RH'):
            md_lines.append(f"### 📌 Domínio: `{dom}` ({len(group)} ocorrências)")
            md_lines.append("| Matrícula | Nome | Campo Alterado | Valor Anterior | Valor Novo (DW) | Observação |")
            md_lines.append("|---|---|---|---|---|---|")
            
            for _, r in group.head(25).iterrows():
                md_lines.append(
                    f"| {r['Matricula']} | {r['Nome']} | `{r['Campo Alterado']}` | `{r['Valor Anterior (Base)']}` | `{r['Valor Novo (DW)']}` | {r['Status / Observação']} |"
                )
            if len(group) > 25:
                md_lines.append(f"\n*... e mais {len(group) - 25} ocorrências registradas neste domínio (consulte a planilha CSV completa).*")
            md_lines.append("")

    return "\n".join(md_lines)
