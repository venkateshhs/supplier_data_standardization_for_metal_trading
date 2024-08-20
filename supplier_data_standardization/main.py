import os
import pandas as pd
import logging
from supplier_data_standardization.utils import get_file_path, read_data, setup_logging, clean_headers, \
    validate_quantity_column


def create_dimension_column(dataframe, thickness_col='Thickness', width_col='Width'):
    """
    Creates a DIMENSION column in the given DataFrame by combining the thickness and width columns.

    Parameters:
    dataframe (pd.DataFrame): The DataFrame containing the thickness and width columns.
    thickness_col (str): The name of the thickness column.
    width_col (str): The name of the width column.

    Returns:
    pd.DataFrame: The DataFrame with the added DIMENSION column.
    """
    dataframe['DIMENSION'] = dataframe[thickness_col].astype(str) + 'x' + dataframe[width_col].astype(str)
    return dataframe


def process_source1():
    """
    Processes the data from source1.xlsx.

    Returns:
    pd.DataFrame: The filtered and processed DataFrame.
    """
    data1 = read_data('source1.xlsx')
    if data1 is not None:
        # Rename columns and process as needed
        data1 = data1.rename(columns={
            'Quality/Choice': 'MATERIAL_GRADE',
            'Grade': 'MATERIAL_NAME',
            'Finish': 'COATING_TYPE',
            'Gross weight (kg)': 'weight',
            'Thickness (mm)': 'Thickness',
            'Width (mm)': 'Width'
        })

        data1 = create_dimension_column(data1, thickness_col='Thickness', width_col='Width')

        # Drop original Thickness and Width columns
        data1 = data1.drop(columns=['Thickness', 'Width'])

        # Select only the required columns
        data1_filtered = data1[['MATERIAL_GRADE', 'MATERIAL_NAME', 'COATING_TYPE', 'DIMENSION', 'weight']]

        # Drop rows with NaN values
        data1_filtered = data1_filtered.dropna()
        logging.info("source1.xlsx processed successfully.")
        return data1_filtered
    else:
        logging.error("Failed to process source1.xlsx.")
        return pd.DataFrame()


def process_source2(file_path=None):
    """
    Processes the data from source2.xlsx.

    Parameters:
    file_path (str): Path to the source2.xlsx file.

    Returns:
    pd.DataFrame: The combined and processed DataFrame.
    """
    if file_path is None:
        file_path = get_file_path('source2.xlsx')

    xls = pd.ExcelFile(file_path)

    df_first_choice = pd.read_excel(xls, 'First choice ')
    df_second_choice = pd.read_excel(xls, '2nd choice ')

    # Clean headers in both sheets
    df_first_choice_cleaned = clean_headers(df_first_choice)
    df_second_choice_cleaned = clean_headers(df_second_choice)

    # Normalize the case of the columns
    df_first_choice_cleaned.columns = df_first_choice_cleaned.columns.str.lower()
    df_second_choice_cleaned.columns = df_second_choice_cleaned.columns.str.lower()

    # Select only the required columns
    df_first_choice_filtered = df_first_choice_cleaned[['material', 'article id', 'weight', 'quantity']]
    df_second_choice_filtered = df_second_choice_cleaned[['material', 'article id', 'weight', 'quantity']]

    # Validate the "quantity" column in both dataframes
    df_first_choice_filtered = validate_quantity_column(df_first_choice_filtered)
    df_second_choice_filtered = validate_quantity_column(df_second_choice_filtered)

    # Combine the two DataFrames based on the columns
    combined_df_source2 = pd.concat([df_first_choice_filtered, df_second_choice_filtered], ignore_index=True)

    return combined_df_source2


def process_source3():
    """
    Processes the data from source3.xlsx.

    Returns:
    pd.DataFrame: The filtered and processed DataFrame.
    """
    data3 = read_data('source3.xlsx')
    if data3 is not None:
        # Rename the columns
        data3.columns = ['quantity', 'article id', 'material', 'Unit', 'weight']

        # Apply the conversion function to each row in the dataframe
        data3['weight'] = data3.apply(convert_to_kg, axis=1)

        # Filter out rows where weight is 0 or less
        data3 = data3[data3['weight'] > 0]

        # Select only the required columns
        data3_filtered = data3[['material', 'weight', 'article id', 'quantity']]
        return data3_filtered
    else:
        logging.error("Failed to process source3.xlsx.")
        return pd.DataFrame()


def convert_to_kg(row):
    """
    Converts weight to kilograms based on the unit.

    Parameters:
    row (pd.Series): A row of the DataFrame.

    Returns:
    float: The weight converted to kilograms.
    """
    unit = row['Unit']
    weight = row['weight']

    if unit.lower() == 'g':  # If the unit is grams
        return weight / 1000  # Convert grams to kilograms
    elif unit.lower() == 'mg':  # If the unit is milligrams
        return weight / 1e6  # Convert milligrams to kilograms
    elif unit.lower() == 'lbs':  # If the unit is pounds
        return weight * 0.453592  # Convert pounds to kilograms
    elif unit.lower() == 'kg':  # If the unit is already kilograms
        return weight  # No conversion needed
    elif unit == 'EA':  # "EA" likely stands for "Each," not a weight unit
        return 0
    else:
        raise ValueError(f"Unknown unit: {unit}")  # Handle unexpected units


def merge_csv_files(data_folder: str) -> pd.DataFrame:
    """
    Reads and merges all CSV files in the specified folder.

    Parameters:
    data_folder (str): The directory containing the CSV files.

    Returns:
    pd.DataFrame: The merged DataFrame containing data from all CSV files.
    """
    # List all CSV files in the directory
    csv_files = [f for f in os.listdir(data_folder) if f.endswith('.csv')]

    # Initialize an empty list to hold the DataFrames
    df_list = []

    # Loop through each file and read it into a DataFrame
    for file in csv_files:
        file_path = os.path.join(data_folder, file)
        df = pd.read_csv(file_path)
        df_list.append(df)
        logging.info(f"CSV file {file} read successfully.")

    # Concatenate all DataFrames in the list
    combined_csv_df = pd.concat(df_list, ignore_index=True)
    logging.info("All CSV files merged successfully.")

    return combined_csv_df


def main():
    """
    The main function that orchestrates reading, processing, and displaying the data.
    """
    # Set up logging
    setup_logging()

    # Process data from source1.xlsx, source2.xlsx, and source3.xlsx
    source1_df = process_source1()
    source2_df = process_source2()
    source3_df = process_source3()

    # Combine the filtered data from all sources
    final_combined_df = pd.concat([source1_df, source2_df, source3_df], ignore_index=True)

    # Remove any empty rows after merging
    final_combined_df = final_combined_df.dropna(how='all')

    # Save the final combined DataFrame to a CSV file
    final_output_path = get_file_path("final_combined_output.csv")
    final_combined_df.to_csv(final_output_path, index=False)

    # Log and print the result
    logging.info(f"Final Combined CSV file saved to: {final_output_path}")
    print(f"Final Combined CSV file saved to: {final_output_path}")
    print(final_combined_df)

    # Now, merge all CSV files in the 'data' directory
    data_folder = os.path.dirname(final_output_path)
    merged_csv_df = merge_csv_files(data_folder)

    # Save the final merged CSV data
    # merged_output_path = get_file_path("final_merged_csv_output.csv")
    # merged_csv_df.to_csv(merged_output_path, index=False)

    # Log and print the result
    # logging.info(f"All CSV files merged and saved to: {merged_output_path}")
    # print(f"All CSV files merged and saved to: {merged_output_path}")
    # print(merged_csv_df)


if __name__ == "__main__":
    main()
