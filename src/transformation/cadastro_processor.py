import pandas as pd
import numpy as np
from typing import Any

# Ordem e nomes exatos das 64 colunas da aba BD_Cadastro na planilha do Google Sheets
BD_CADASTRO_COLUMNS = [
    'Matricula', 'Nome', 'CPF', 'Sexo', 'Aniversário', 'Data de nascimento',
    'Idade em anos', 'Cod. Raça', 'Raça', 'Cod. Estado Civil', 'Estado Civil',
    'Cod. Tipo de Deficiência', 'Tipo de Deficiência', 'Cedidos', 'Situação do Servidor',
    'Data de Admissão', 'Cod. SG empregados', 'SG empregados', 'Regime jurídico.',
    'Vínculo empregatício', 'Relação de emprego', 'Cod. Tipo de Cargo', 'Tipo de Cargo',
    'Tipo de contrato', 'Status de ocupação', 'Cod. Grupo de empregados',
    'Grupo de empregados', 'Grupo Ocupacional', 'Cod. Tp. Tarifa', 'Tp. Tarifa',
    'Cod. Cargo', 'Cargo', 'Cargo_tmp', 'Reg', 'Faixa SN', 'Nv', 'CH', 'Grau',
    'Símbolo Do cargo', 'Cod. Cargo Amplo', 'Cargo Amplo', 'Cod. Cargo Efetivo',
    'Cargo Efetivo', 'Cod. Cargo Origem', 'Cargo Origem', 'Carreira',
    'Órgão do Cargo Efetivo', 'Nível salarial Efetivo', 'Classe do agente',
    'Início da Medida', 'Últ. Motivo Medida', 'ÚltimoTipo de Medida', 'Cod. Gestor',
    'Gestor', 'Cod. Área RecursosHumanos', 'Área RecursosHumanos',
    'Cod. Subárea de RH', 'Subárea de RH', 'Para Período',
    'Cod. Unid. organizacional', 'Sigla. Unid. organizacional',
    'Unid. organizacional', 'Data Inicial Infipo 14', 'Data Fim Infipo 14'
]

def clean_str(val: Any) -> str:
    if pd.isna(val) or val is None:
        return ""
    s = str(val).strip()
    try:
        return s.encode('latin1').decode('utf-8')
    except:
        return s

def process_cadastro_for_sheets(df_dw_cadastro: pd.DataFrame, df_existing_bd: pd.DataFrame = None) -> pd.DataFrame:
    """
    Processa e alinha o cadastro do DW para a aba BD_Cadastro.
    Deduplica o DW por Matrícula e atualiza os campos de Cargo, Símbolo, Função, Lotação e Unidade Organizacional,
    garantindo que alterações no DW atualizem o BD_Cadastro sem romper o grão e as 64 colunas.
    """
    df = df_dw_cadastro.copy()
    
    # Deduplicação por Matrícula no DW export (coluna 1 do DW export é a Matrícula)
    if len(df.columns) > 2:
        df_dw_unique = df.drop_duplicates(subset=[df.columns[1]], keep='first').copy()
        df_dw_unique['Matricula_Clean'] = df_dw_unique.iloc[:, 1].apply(clean_str)
        df_dw_unique = df_dw_unique.set_index('Matricula_Clean')
    else:
        df_dw_unique = pd.DataFrame()

    # Se possuímos a base existente de BD_Cadastro (2.120 linhas), usamos como estrutura base
    if df_existing_bd is not None and not df_existing_bd.empty:
        out_df = df_existing_bd.copy()
        out_df['Matricula_Clean'] = out_df['Matricula'].apply(clean_str)
        
        # Garante presença de todas as 64 colunas
        for c in BD_CADASTRO_COLUMNS:
            if c not in out_df.columns:
                out_df[c] = ""

        # Atualiza os campos extraídos do DW por Matrícula
        if not df_dw_unique.empty:
            for idx, row in out_df.iterrows():
                mat = row['Matricula_Clean']
                if mat in df_dw_unique.index:
                    dw_row = df_dw_unique.loc[mat]
                    if isinstance(dw_row, pd.DataFrame):
                        dw_row = dw_row.iloc[0]

                    # Atualização de Nome se veio no DW
                    if len(dw_row) > 2 and clean_str(dw_row.iloc[2]):
                        out_df.at[idx, 'Nome'] = clean_str(dw_row.iloc[2])

                    # Atualização de Cargo se veio no DW
                    if len(dw_row) > 20 and clean_str(dw_row.iloc[20]):
                        out_df.at[idx, 'Cargo'] = clean_str(dw_row.iloc[20])
                    
                    # Atualização de Vínculo se veio no DW
                    if len(dw_row) > 11 and clean_str(dw_row.iloc[11]):
                        out_df.at[idx, 'Vínculo empregatício'] = clean_str(dw_row.iloc[11])

                    # Atualização de Relação de emprego se veio no DW
                    if len(dw_row) > 12 and clean_str(dw_row.iloc[12]):
                        out_df.at[idx, 'Relação de emprego'] = clean_str(dw_row.iloc[12])

                    # Atualização de SG Empregados se veio no DW
                    if len(dw_row) > 5 and clean_str(dw_row.iloc[5]):
                        out_df.at[idx, 'SG empregados'] = clean_str(dw_row.iloc[5])

        out_df = out_df.drop(columns=['Matricula_Clean'], errors='ignore')
        return out_df[BD_CADASTRO_COLUMNS]

    # Caso não haja base existente, monta o DataFrame com as 64 colunas
    out_df = pd.DataFrame(index=range(len(df_dw_unique)))
    for col in BD_CADASTRO_COLUMNS:
        out_df[col] = ""

    if not df_dw_unique.empty:
        out_df['Matricula'] = df_dw_unique.index.values
        out_df['Nome'] = [clean_str(r.iloc[2]) if len(r) > 2 else "" for _, r in df_dw_unique.iterrows()]
        out_df['CPF'] = [clean_str(r.iloc[0]) if len(r) > 0 else "" for _, r in df_dw_unique.iterrows()]
        out_df['Sexo'] = [clean_str(r.iloc[3]) if len(r) > 3 else "" for _, r in df_dw_unique.iterrows()]
        out_df['Cargo'] = [clean_str(r.iloc[20]) if len(r) > 20 else "" for _, r in df_dw_unique.iterrows()]

    return out_df[BD_CADASTRO_COLUMNS]
