import unittest

from supplier_data_standardization.ner_model import preprocess_dimensions


class TestPreprocessDimensions(unittest.TestCase):

    def test_preprocess_dimensions(self):
        input_text = "1,00x1250,00mm"
        expected_output = "1,00x1250,00mm"
        self.assertEqual(preprocess_dimensions(input_text), expected_output)

    def test_preprocess_three_dimensions(self):
        input_text = "9,99*1500"
        expected_output = "9,99x1500"
        self.assertEqual(preprocess_dimensions(input_text), expected_output)

    def test_preprocess_with_no_match(self):
        input_text = "No dimensions here"
        expected_output = "No dimensions here"
        self.assertEqual(preprocess_dimensions(input_text), expected_output)

    def test_preprocess_with_no_match(self):
        input_text = "1,75 x 1250,00"
        expected_output = "1,75x1250,00"
        self.assertEqual(preprocess_dimensions(input_text), expected_output)


if __name__ == '__main__':
    unittest.main()
