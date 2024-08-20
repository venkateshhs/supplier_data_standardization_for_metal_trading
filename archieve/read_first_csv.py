import pandas as pd
import os
import logging
from typing import Optional

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def get_file_path(file_name: str) -> str:
    """
    Constructs the file path by finding the 'data' directory in the current working directory
    and appending the file name to it.

    Parameters:
    file_name (str): The name of the Excel file.

    Returns:
    str: The full path to the Excel file.
    """

    # Find the 'data' directory in the current working directory
    data_directory = os.path.join(os.path.dirname(os.getcwd()), 'data')

    # Append the file name to get the full file path
    file_path = os.path.join(data_directory, file_name)

    return file_path


def read_data(file_name: str) -> Optional[pd.DataFrame]:
    """
    Reads the Excel file from the data directory and returns a DataFrame.

    Parameters:
    file_name (str): The name of the Excel file to read.

    Returns:
    Optional[pd.DataFrame]: The DataFrame containing the data from the Excel file, or None if the file cannot be read.
    """
    try:
        # Get the full file path
        file_path = get_file_path(file_name)

        # Load the Excel file
        df = pd.read_excel(file_path)
        logging.info(f"File {file_name} successfully read from {file_path}.")
        return df
    except Exception as e:
        logging.error(f"Failed to read {file_name}: {e}")
        return None


def process_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Processes the DataFrame by renaming columns, merging dimensions, and dropping NaN values.

    Parameters:
    df (pd.DataFrame): The DataFrame to process.

    Returns:
    pd.DataFrame: The processed DataFrame with selected columns.
    """
    # Rename the columns
    df = df.rename(columns={
        'Quality/Choice': 'MATERIAL_GRADE',
        'Grade': 'MATERIAL_NAME',
        'Finish': 'COATING_TYPE',
        'Gross weight (kg)': 'WEIGHT'
    })
    logging.info("Columns renamed successfully.")

    # Merge 'Thickness (mm)' and 'Width (mm)' into a new column 'DIMENSION'
    df['DIMENSION'] = df['Thickness (mm)'].astype(str) + 'x' + df['Width (mm)'].astype(str)
    logging.info("Dimensions merged successfully.")

    # Drop the original 'Thickness (mm)' and 'Width (mm)' columns if no longer needed
    df = df.drop(columns=['Thickness (mm)', 'Width (mm)'])

    # Select the specified columns
    selected_columns_df = df[['MATERIAL_GRADE', 'MATERIAL_NAME', 'COATING_TYPE', 'DIMENSION', 'weight']]

    # Drop rows with NaN values
    rest_df = selected_columns_df.dropna()
    logging.info("NaN values dropped successfully.")

    return rest_df


def main():
    """
    The main function that orchestrates reading, processing, and displaying the data.
    """
    # File name
    file_name = 'source1.xlsx'

    # Read the data
    df = read_data(file_name)

    if df is not None:
        # Process the data
        processed_df = process_data(df)

        # Print the processed data
        print(processed_df)
    else:
        logging.error("No data to process.")


if __name__ == "__main__":
    main()
