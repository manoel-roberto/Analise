import unittest
from src.ingestion.normalizer import clean_currency, clean_percent, normalize_dataframe
import pandas as pd

class TestNormalizer(unittest.TestCase):

    def test_clean_currency(self):
        self.assertEqual(clean_currency("R$ 1.234,56"), 1234.56)
        self.assertEqual(clean_currency("-R$ 500,00"), -500.0)
        self.assertEqual(clean_currency("100"), 100.0)
        self.assertEqual(clean_currency(""), 0.0)
        self.assertEqual(clean_currency(None), 0.0)

    def test_clean_percent(self):
        self.assertEqual(clean_percent("50,00%"), 0.50)
        self.assertEqual(clean_percent("105%"), 1.05)
        self.assertEqual(clean_percent("0.30"), 0.30)
        self.assertEqual(clean_percent(""), 0.0)

    def test_normalize_dataframe(self):
        df = pd.DataFrame({"a": ["  teste  ", "nan", None], "b": [1, 2, 3]})
        df_clean = normalize_dataframe(df)
        self.assertEqual(df_clean["a"].iloc[0], "teste")
        self.assertEqual(df_clean["a"].iloc[1], "")

if __name__ == "__main__":
    unittest.main()
