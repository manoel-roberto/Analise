import unittest
import os
from src.ingestion.dw_parser import parse_dw_cadastro, parse_dw_folha, find_latest_dw_files

class TestDWParser(unittest.TestCase):

    def setUp(self):
        self.import_dir = "import"
        self.bd_file, self.folha_file = find_latest_dw_files(self.import_dir)

    def test_find_latest_dw_files(self):
        self.assertIsNotNone(self.bd_file)
        self.assertIsNotNone(self.folha_file)

    def test_parse_dw_cadastro(self):
        if self.bd_file and os.path.exists(self.bd_file):
            df_bd = parse_dw_cadastro(self.bd_file)
            self.assertGreater(len(df_bd), 100)
            self.assertGreater(len(df_bd.columns), 10)

    def test_parse_dw_folha(self):
        if self.folha_file and os.path.exists(self.folha_file):
            df_folha = parse_dw_folha(self.folha_file)
            self.assertGreater(len(df_folha), 100)
            self.assertEqual(df_folha.shape[1], 8)

if __name__ == "__main__":
    unittest.main()
