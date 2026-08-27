import pandas as pd
import numpy as np
from typing import Dict, Tuple
from ..ingestion.normalizer import clean_currency, clean_percent

def compute_base_calculo(cargo: str, valor_simbolo: float, venc_basico: float, das_dai: float) -> float:
    """
    Calcula a Base de Cálculo (BC) idêntica à regra do Apps Script (obterBaseCalculo):
    - Exceção: Se Cargo contiver 'Técnico Específico' => BC = Valor do Símbolo
    - Cenário 1: Se DAS/DAI == Valor do Símbolo => BC = DAS/DAI
    - Cenário 2: Se DAS/DAI != Valor do Símbolo => BC = Vencimento Básico
    """
    cargo_str = str(cargo).strip().lower() if pd.notnull(cargo) else ''
    if 'técnico específico' in cargo_str or 'tecnico especifico' in cargo_str:
        return valor_simbolo
    
    if abs(das_dai - valor_simbolo) < 0.01:
        return das_dai
    return venc_basico

def process_simulacao_engine(
    df_simulacao: pd.DataFrame,
    grupo_acrescimos: Dict[str, float] = None
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Reprocessa o motor de simulação orçamentária (Analise_Simulacao) e atualiza
    os 4 Cenários Comparativos e o Melhor Caso. Retorna (df_simulacao_atualizado, df_visao_atualizado).
    """
    if grupo_acrescimos is None:
        grupo_acrescimos = {'1.': 0.0, '2.': 0.0, '3.': 0.0, '4.': 0.0, '5.': 0.0, '6.': 0.0}

    df = df_simulacao.copy()
    
    out_rows = []
    for idx, row in df.iterrows():
        cargo = str(row.get('Cargo', ''))
        grupo = str(row.get('Grupo_Gestão', ''))
        
        valor_simbolo = clean_currency(row.get('Valor_Simbolo', 0))
        venc_basico = clean_currency(row.get('Vencimento_Basico(2)', 0))
        das_dai = clean_currency(row.get('DAS ou DAI', 0))
        gstu = clean_currency(row.get('GSTU', 0))
        rti_atual = clean_currency(row.get('RTI_CET', 0))
        perc_rti_atual = clean_percent(row.get('%RTI_CET', 0))
        
        # Base de Cálculo
        bc = compute_base_calculo(cargo, valor_simbolo, venc_basico, das_dai)
        
        # Identifica acréscimo do grupo
        acrescimo = 0.0
        for prefix, pct in grupo_acrescimos.items():
            if grupo.startswith(prefix):
                acrescimo = float(pct) / 100.0 if float(pct) > 1.0 else float(pct)
                break
                
        novo_perc = perc_rti_atual + acrescimo
        novo_valor_rti = bc * novo_perc
        
        # 4 Cenários Comparativos
        c1 = venc_basico + (0.30 * valor_simbolo) + gstu
        c2 = venc_basico + (0.30 * valor_simbolo) + novo_valor_rti
        c3 = (1.00 * valor_simbolo) + gstu
        c4 = (1.00 * valor_simbolo) + novo_valor_rti
        
        melhor_caso = max(c1, c2, c3, c4)
        cenario_atual = venc_basico + rti_atual
        cenario_simulado = venc_basico + novo_valor_rti
        dif_atual_simulado = cenario_simulado - cenario_atual
        
        row_dict = row.to_dict()
        row_dict['% RTI'] = f"{novo_perc * 100:.2f}%"
        row_dict['R$ RTI'] = f"R$ {novo_valor_rti:,.2f}"
        row_dict['%Aumento Simulado'] = f"{acrescimo * 100:.2f}%"
        row_dict['Cenário_1\n(Vencimento + 30% Símbolo + GSTU)'] = f"R$ {c1:,.2f}"
        row_dict['Cenário_2\n(Vencimento + 30% Símbolo + RTI)'] = f"R$ {c2:,.2f}"
        row_dict['Cenário_3\n(100% Símbolo + GSTU)'] = f"R$ {c3:,.2f}"
        row_dict['Cenário_4\n(100% Símbolo + RTI)'] = f"R$ {c4:,.2f}"
        row_dict['Melhor Caso'] = f"R$ {melhor_caso:,.2f}"
        row_dict['Cenário Atual'] = f"R$ {cenario_atual:,.2f}"
        row_dict['Cenário Simulado'] = f"R$ {cenario_simulado:,.2f}"
        row_dict['DIF. Atual - Simulado'] = f"R$ {dif_atual_simulado:,.2f}"
        
        out_rows.append(row_dict)
        
    df_sim_out = pd.DataFrame(out_rows)
    return df_sim_out
