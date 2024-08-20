import unittest
import pandas as pd
from supplier_data_standardization.main import create_dimension_column

class TestCreateDimensionColumn(unittest.TestCase):

    def test_create_dimension_column(self):
        # Create a dummy DataFrame to test the function
        mock_data = pd.DataFrame({
            'Thickness': [5, 10, 15],
            'Width': [50, 100, 150]
        })

        # Expected DataFrame after creating the DIMENSION column
        expected_output = pd.DataFrame({
            'Thickness': [5, 10, 15],
            'Width': [50, 100, 150],
            'DIMENSION': ['5x50', '10x100', '15x150']
        })

        # Call the function under test
        result = create_dimension_column(mock_data, 'Thickness', 'Width')

        # Assert that the result matches the expected output
        pd.testing.assert_frame_equal(result, expected_output)

    def test_create_dimension_column_with_different_column_names(self):
        # Create a dummy DataFrame with different column names
        mock_data = pd.DataFrame({
            'T': [2, 4],
            'W': [20, 40]
        })

        # Expected DataFrame after creating the DIMENSION column
        expected_output = pd.DataFrame({
            'T': [2, 4],
            'W': [20, 40],
            'DIMENSION': ['2x20', '4x40']
        })

        # Call the function under test with different column names
        result = create_dimension_column(mock_data, 'T', 'W')

        # Assert that the result matches the expected output
        pd.testing.assert_frame_equal(result, expected_output)


if __name__ == '__main__':
    unittest.main()
