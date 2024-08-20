import os
import logging
import pandas as pd
from typing import Optional
from datetime import datetime


def setup_logging():
    """
    Sets up logging to a file in the 'logs' directory with the current timestamp as the filename.
    """
    log_dir = os.path.join(os.path.dirname(os.getcwd()), 'logs')
    os.makedirs(log_dir, exist_ok=True)

    log_file = os.path.join(log_dir, f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )


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


def clean_headers(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans the DataFrame by removing rows that are headers, the row before them, and empty rows.

    Parameters:
    df (pd.DataFrame): The DataFrame to clean.

    Returns:
    pd.DataFrame: The cleaned DataFrame.
    """
    df.columns = df.iloc[0]  # Set the first row as header
    df = df[1:]  # Remove the first row as it is now the header

    # Strip spaces from column names
    df.columns = df.columns.str.strip()

    # Identify the rows with repeated headers
    header_indices = df.index[df['Article ID'] == 'Article ID '].tolist()

    # Remove the repeated headers and the row before them
    for index in reversed(header_indices):  # Reversed to avoid indexing issues
        df = df.drop([index, index - 1])

    # Remove any empty rows
    df = df.dropna(how='all')

    logging.info("Headers cleaned successfully.")
    return df


def validate_quantity_column(df: pd.DataFrame) -> pd.DataFrame:
    """
    Validates the 'quantity' column, replacing non-numeric values with empty strings.

    Parameters:
    df (pd.DataFrame): The DataFrame to validate.

    Returns:
    pd.DataFrame: The DataFrame with validated 'quantity' column.
    """
    df = df.copy()  # Create a copy to avoid SettingWithCopyWarning

    # Function to check if a value is numeric
    def is_numeric(value):
        try:
            float(value)
            return True
        except ValueError:
            return False

    # Apply the function to replace non-numeric values with empty strings
    df['quantity'] = df['quantity'].apply(lambda x: x if is_numeric(x) else '')

    logging.info("Quantity column validated successfully.")
    return df


def get_training_data():
    return [
        ("DX51D +Z140 Ma-C 1,50x1350,00x2850,00",
         ["MATERIAL_NAME", "COATING_TYPE", "FINISH_TYPE", "DIMENSION"]),
        ("DX51D +AZ150  Ma-C 1,00x1250,00mm AFP",
         ["MATERIAL_NAME", "COATING_TYPE", "FINISH_TYPE", "DIMENSION", "ADDITIONAL_SPEC"]),
        ("DTEST +Z1895 St-C 1,50x1350,00x1234,00",
         ["MATERIAL_NAME", "COATING_TYPE", "FINISH_TYPE", "DIMENSION"]),
        ("DY51D +Z15  Va-C 1,00x1250,00mm PPP",
         ["MATERIAL_NAME", "COATING_TYPE", "FINISH_TYPE", "DIMENSION", "ADDITIONAL_SPEC"]),
        ("S235JR geolied 1,75x1250,00mm",
         ["MATERIAL_NAME", "COATING_TYPE", "DIMENSION"]),
        ("DC01 licht geolied 2,50x1500mm",
         ["MATERIAL_NAME", "COATING_TYPE", "COATING_TYPE", "DIMENSION"]),
        ("DX51D +Z100 Ma-C 0,57x1250,00mm",
         ["MATERIAL_NAME", "COATING_TYPE", "FINISH_TYPE", "DIMENSION"]),
        ("S550 GD+ZM175 MAC 2x1070mm",
         ["MATERIAL_NAME", "COATING_TYPE", "FINISH_TYPE", "DIMENSION"]),
        ("S235  ongeb/ ongeol traan  5x1500mm",
         ["MATERIAL_NAME", "COATING_TYPE", "COATING_TYPE", "FINISH_TYPE", "DIMENSION"]),
        ("DX51D+Z275 0,75*1250",
         ["MATERIAL_NAME", "DIMENSION"]),
        ("CR 0.65x1080 XCV G7/7 MB O",
         ["MATERIAL_NAME", "DIMENSION", "MATERIAL_GRADE", "COATING_TYPE", "FINISH_TYPE", "ADDITIONAL_SPEC"]),
        ("HDC 0.75x1270 GXE G6/6 MB O",
         ["MATERIAL_NAME", "DIMENSION", "MATERIAL_GRADE", "COATING_TYPE", "FINISH_TYPE", "ADDITIONAL_SPEC"]),
        ("CR 1.5x1487 XE320D A O",
         ["MATERIAL_NAME", "DIMENSION", "MATERIAL_GRADE", "FINISH_TYPE", "ADDITIONAL_SPEC"]),
        ("HRP 2.2x1200 HE360D O",
         ["MATERIAL_NAME", "DIMENSION", "MATERIAL_GRADE", "ADDITIONAL_SPEC"]),
        ("HRP 2x1360 HR2 O",
         ["MATERIAL_NAME", "DIMENSION", "MATERIAL_GRADE", "ADDITIONAL_SPEC"]),
        ("HRP 2x193 HES O",
         ["MATERIAL_NAME", "DIMENSION", "MATERIAL_GRADE", "ADDITIONAL_SPEC"]),
        ("2ND QUALITY CR SLIT",
         ["MATERIAL_GRADE", "MATERIAL_GRADE", "MATERIAL_NAME", "ADDITIONAL_SPEC"]),
        ("HDC 0.75x1725 CR300LA-GI 60/60 MB O",
         ["MATERIAL_NAME", "DIMENSION", "MATERIAL_GRADE", "COATING_TYPE", "FINISH_TYPE", "ADDITIONAL_SPEC"]),
        # Additional examples
        ("DX51D +Z140 Ma-C 4,00x775,00x2850,00",
         ["MATERIAL_NAME", "COATING_TYPE", "FINISH_TYPE", "DIMENSION"]),
        ("DX51D +Z140 Ma-C 1,50x1350,00x2850,00mm",
         ["MATERIAL_NAME", "COATING_TYPE", "FINISH_TYPE", "DIMENSION"]),
        ("DD11 geolied 1,50x122,00mm",
         ["MATERIAL_NAME", "DIMENSION"]),
        ("CR3 1,5x1250,00mm",
         ["MATERIAL_NAME", "DIMENSION"]),
        ("DC01 licht geolied 2,50x1500 mm",
         ["MATERIAL_NAME", "COATING_TYPE", "COATING_TYPE", "DIMENSION"]),
        ("DC01 licht geolied 2,50x1500mm",
         ["MATERIAL_NAME", "COATING_TYPE", "COATING_TYPE", "DIMENSION"]),
        ("S235JR geolied 2,50x1465,00mm",
         ["MATERIAL_NAME", "COATING_TYPE", "DIMENSION"]),
        ("DD11 geolied 2,00x1250,00x3500,00mm",
         ["MATERIAL_NAME", "COATING_TYPE", "DIMENSION"]),
        ("S350GD +ZM310 Ma-C 3,00x165,00mm",
         ["MATERIAL_NAME", "COATING_TYPE", "FINISH_TYPE", "DIMENSION"]),
        ("HRP 2.2x1200 HE360D O",
         ["MATERIAL_NAME", "DIMENSION", "MATERIAL_GRADE", "ADDITIONAL_SPEC"]),
        ("HDC 1x1000 HX300LAD+Z 140 MB O",
         ["MATERIAL_NAME", "DIMENSION", "MATERIAL_GRADE", "COATING_TYPE", "FINISH_TYPE", "ADDITIONAL_SPEC"]),
        ("S500MC Oiled 9,99*1500",
         ["MATERIAL_NAME", "COATING_TYPE", "DIMENSION"])

    ]
