import os
import pandas as pd

# Load the data from source3.xlsx
data_folder = os.path.join(os.path.dirname(os.getcwd()), 'data')
file3_path = os.path.join(data_folder, 'source3.xlsx')
data3 = pd.read_excel(file3_path)

# Rename the columns as requested
data3.columns = ['quantity', 'article id', 'material', 'Unit', 'weight']

# Convert weight to kilograms based on the unit
def convert_to_kg(row):
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

# Apply the conversion function to each row in the dataframe
data3['weight'] = data3.apply(convert_to_kg, axis=1)

# Filter out rows where weight is 0 or less
data3 = data3[data3['weight'] > 0]

# Select only the required columns
data3_filtered = data3[['material', 'weight', 'article id', 'quantity']]

# Load the data from source2.xlsx
file2_path = os.path.join(data_folder, 'source2.xlsx')
xls = pd.ExcelFile(file2_path)

# Read the sheets into DataFrames
df_first_choice = pd.read_excel(xls, 'First choice ')
df_second_choice = pd.read_excel(xls, '2nd choice ')

# Function to clean the data by removing rows that are headers, the row before them, and empty rows
def clean_headers(df):
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

    return df

# Function to validate the "quantity" column and replace non-numeric values with empty strings
def validate_quantity_column(df):
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

    return df

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

# Combine the filtered data from source2.xlsx with the filtered data from source3.xlsx
final_combined_df = pd.concat([combined_df_source2, data3_filtered], ignore_index=True)

# Remove any empty rows after merging
final_combined_df = final_combined_df.dropna(how='all')

# Save the final combined DataFrame to a CSV file
final_output_path = os.path.join(data_folder, "final_combined_output.csv")
final_combined_df.to_csv(final_output_path, index=False)

# Print the resulting DataFrame
print(f"Final Combined CSV file saved to: {final_output_path}")
print(final_combined_df)
