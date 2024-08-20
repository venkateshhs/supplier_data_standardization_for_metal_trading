import os
import sys
import unittest
import spacy
from spacy.language import Language

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


@Language.component("merge_hyphenated_words")
class TestMergeHyphenatedWords(unittest.TestCase):

    def setUp(self):
        self.nlp = spacy.blank("en")
        self.nlp.add_pipe("merge_hyphenated_words")

    def test_merge_hyphenated_words(self):
        text = "This is a well-known issue."
        doc = self.nlp(text)
        tokens = [token.text for token in doc]
        expected_tokens = ["This", "is", "a", "well-known", "issue", "."]
        self.assertEqual(tokens, expected_tokens)

    def test_merge_plus_pattern(self):
        text = "The cost is +50 dollars."
        doc = self.nlp(text)
        tokens = [token.text for token in doc]
        expected_tokens = ["The", "cost", "is", "+50", "dollars", "."]
        self.assertEqual(tokens, expected_tokens)

    def test_merge_no_match(self):
        text = "This text has no hyphenated words."
        doc = self.nlp(text)
        tokens = [token.text for token in doc]
        expected_tokens = ["This", "text", "has", "no", "hyphenated", "words", "."]
        self.assertEqual(tokens, expected_tokens)


if __name__ == '__main__':
    unittest.main()
