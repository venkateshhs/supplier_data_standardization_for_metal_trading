import os
import sys
import unittest
import pandas as pd
from supplier_data_standardization.main import convert_to_kg

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class TestDataProcessing(unittest.TestCase):

    def test_convert_to_kg(self):
        # Test grams conversion
        row = pd.Series({'Unit': 'g', 'weight': 1000})
        self.assertEqual(convert_to_kg(row), 1.0)

        # Test milligrams conversion
        row = pd.Series({'Unit': 'mg', 'weight': 1000000})
        self.assertEqual(convert_to_kg(row), 1.0)

        # Test pounds conversion
        row = pd.Series({'Unit': 'lbs', 'weight': 2.20462})
        self.assertAlmostEqual(convert_to_kg(row), 1.0, places=4)

        # Test kilograms (no conversion)
        row = pd.Series({'Unit': 'kg', 'weight': 1})
        self.assertEqual(convert_to_kg(row), 1.0)

        # Test invalid unit
        row = pd.Series({'Unit': 'unknown', 'weight': 1})
        with self.assertRaises(ValueError):
            convert_to_kg(row)


if __name__ == '__main__':
    unittest.main()
