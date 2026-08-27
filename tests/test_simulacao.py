import unittest
from src.transformation.simulacao_engine import compute_base_calculo, process_simulacao_engine
import pandas as pd

class TestSimulacaoEngine(unittest.TestCase):

    def test_compute_base_calculo(self):
        # Exceção Técnico Específico -> BC = Valor do Símbolo
        bc1 = compute_base_calculo("Técnico Específico", valor_simbolo=3605.26, venc_basico=2000.0, das_dai=3605.26)
        self.assertEqual(bc1, 3605.26)

        # Cenário 1: DAS/DAI == Valor do Símbolo -> BC = DAS/DAI
        bc2 = compute_base_calculo("Assessor Especial", valor_simbolo=3605.26, venc_basico=2000.0, das_dai=3605.26)
        self.assertEqual(bc2, 3605.26)

        # Cenário 2: DAS/DAI != Valor do Símbolo -> BC = Vencimento Básico
        bc3 = compute_base_calculo("Assessor Chefe", valor_simbolo=3605.26, venc_basico=4000.0, das_dai=2763.10)
        self.assertEqual(bc3, 4000.0)

    def test_process_simulacao_engine(self):
        sample_data = [{
            'Matrícula': '9381641',
            'Cargo': 'DAS2D COORDENADOR CONTROLE INTERNO II',
            'Grupo_Gestão': '4. Assessor em ascensão',
            'Valor_Simbolo': 'R$ 2.763,10',
            'Vencimento_Basico(2)': 'R$ 7.688,18',
            'DAS ou DAI': 'R$ 2.763,10',
            'GSTU': 'R$ 3.283,63',
            'RTI_CET': 'R$ 1.845,10',
            '%RTI_CET': '50,00%',
        }]
        df_in = pd.DataFrame(sample_data)
        df_out = process_simulacao_engine(df_in, grupo_acrescimos={'4.': 5.0})
        
        self.assertEqual(len(df_out), 1)
        self.assertIn('Melhor Caso', df_out.columns)
        self.assertIn('Cenário_1\n(Vencimento + 30% Símbolo + GSTU)', df_out.columns)

if __name__ == "__main__":
    unittest.main()
