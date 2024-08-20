import re

def preprocess_dimensions(text):
    print(text)
    # Handle patterns like '9,99 * 1500' by removing spaces around '*'
    text = re.sub(r'(\d+,\d+)\s*\*\s*(\d+)', r'\1*\2', text)
    text = re.sub(r'(\d+)\s*\*\s*(\d+)', r'\1*\2', text)

    # Handle three-part dimensions with 'x' separators, ensuring units like 'mm' are attached
    three_dim_pattern = r'(\d+,\d+)\s*x\s*(\d+,\d+)\s*x\s*(\d+,\d+)\s*(mm|cm|m|kg|g)?'
    text = re.sub(three_dim_pattern, r'\1x\2x\3\4', text)

    # Handle two-part dimensions with 'x' separator and unit, ensuring the unit is attached
    two_dim_with_unit_pattern = r'(\d+,\d+|\d+)\s*x\s*(\d+,\d+|\d+)\s*(mm|cm|m|kg|g)?'
    text = re.sub(two_dim_with_unit_pattern, r'\1x\2\3', text)

    # Handle two-part dimensions with 'x' separator and no unit
    two_dim_no_unit_pattern = r'(\d+,\d+|\d+)\s*x\s*(\d+,\d+)'
    text = re.sub(two_dim_no_unit_pattern, r'\1x\2', text)

    # Handle dimensions with '*' separator and unit
    two_dim_star_with_unit_pattern = r'(\d+,\d+|\d+)\s*\*\s*(\d+)\s*(mm|cm|m|kg|g)?'
    text = re.sub(two_dim_star_with_unit_pattern, r'\1*\2\3', text)

    # Handle dimensions with '*' separator and no unit
    two_dim_star_no_unit_pattern = r'(\d+,\d+|\d+)\s*\*\s*(\d+)'
    text = re.sub(two_dim_star_no_unit_pattern, r'\1*\2', text)

    # Handle single part dimension with unit and a space (e.g., '1250,00 mm')
    single_dim_with_unit_pattern = r'(\d+,\d+|\d+)\s*(mm|cm|m|kg|g)'
    text = re.sub(single_dim_with_unit_pattern, r'\1\2', text)

    # Remove space after a digit if the next two characters are mm, cm, or m
    text = re.sub(r'(\d)\s+(?=mm|cm|m)', r'\1', text)

    # Ensure space between dimension and text part
    text = re.sub(r'(\d+x\d+)(\s*)([A-Za-z])', r'\1 \3', text)

    # Ensure space between text and dimension part
    text = re.sub(r'([A-Za-z]+)(\d+x\d+)', r'\1 \2', text)

    # Ensure space between text and dimension part with comma
    text = re.sub(r'([A-Za-z]+)(\d+,\d+x\d+,\d+)', r'\1 \2', text)

    # Ensure space between text and dimension part with comma and unit
    text = re.sub(r'([A-Za-z]+)(\d+,\d+x\d+,\d+\s*mm|cm|m|kg|g)', r'\1 \2', text)

    print(text)

    text = text.replace('*', 'x')
    print(text)
    return text

# Example usage
input_text = "DD11 geolied 2,00 x 92,00 mm"
output_text = preprocess_dimensions(input_text)
print("Output:", output_text)
