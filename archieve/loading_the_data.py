import os
import pandas as pd

# Load the Excel file
data_folder = os.path.join(os.path.dirname(os.getcwd()), 'data')
file3_path = os.path.join(data_folder, 'source3.xlsx')
data3 = pd.read_excel(file3_path)

# Rename the columns as requested
data3.columns = ['Number', 'article id', 'material', 'Unit', 'Weight']

# Step 2: Convert weight to kilograms based on the unit
def convert_to_kg(row):
    unit = row['Unit']
    weight = row['Weight']

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
data3['Weight'] = data3.apply(convert_to_kg, axis=1)

# Filter out rows where weight is 0 or less
data3 = data3[data3['Weight'] > 0]

# Select only the required columns
data3_filtered = data3[['material', 'Weight', 'article id', 'Number']]

# Rename 'Number' to 'quantity'
data3_filtered = data3_filtered.rename(columns={'Number': 'quantity'})

# Save the filtered DataFrame to a new CSV file
output_file_path = os.path.join(data_folder, "source_3_description_filtered.csv")
data3_filtered.to_csv(output_file_path, index=False)

# Print the resulting DataFrame
print(data3_filtered)
