import os
import unittest
import spacy

from supplier_data_standardization.ner_model import preprocess_dimensions


class TestPositionBasedNERModel(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Load the trained NER model
        model_dir = os.path.join(os.path.dirname(os.getcwd()), 'supplier_data_standardization', 'ner_model')
        cls.nlp = spacy.load(model_dir)

    def test_ner_prediction(self):
        # The input text to test
        test_text = "HDC 1x1000 HX300LAD+Z 140 MB O"

        # Preprocess the text if needed
        preprocessed_text = preprocess_dimensions(test_text)

        # Predict entities using the NER model
        doc = self.nlp(preprocessed_text)
        entities = [(ent.text, ent.label_) for ent in doc.ents]

        # Expected entities and labels
        expected_entities = [
            ("HDC", "MATERIAL_NAME"),
            ("1x1000", "DIMENSION"),
            ("HX300LAD+Z", "MATERIAL_GRADE"),
            ("140", "COATING_TYPE"),
            ("MB", "FINISH_TYPE"),
            ("O", "ADDITIONAL_SPEC")
        ]

        # Assert that the predicted entities match the expected ones
        self.assertEqual(entities, expected_entities)


if __name__ == '__main__':
    unittest.main()
