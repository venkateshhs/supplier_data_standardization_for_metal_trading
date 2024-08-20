import spacy
import pandas as pd
from spacy.language import Language
from spacy.matcher import Matcher

# Step 1: Define the custom component to merge hyphenated words
@Language.component("merge_hyphenated_words")
def merge_hyphenated_words(doc):
    matcher = Matcher(nlp.vocab)

    # Define the pattern to match an alphanumeric sequence followed by a hyphen and another alphanumeric sequence
    pattern = [
        {"TEXT": {"REGEX": "^[a-zA-Z0-9]+$"}},  # Alphanumeric before hyphen
        {"ORTH": "-"},                         # Hyphen
        {"TEXT": {"REGEX": "^[a-zA-Z0-9]+$"}}  # Alphanumeric after hyphen
    ]

    matcher.add("HYPHENATED", [pattern])
    matches = matcher(doc)

    with doc.retokenize() as retokenizer:
        for match_id, start, end in matches:
            span = doc[start:end]
            retokenizer.merge(span)

    return doc

# Step 2: Load the trained model after registering the custom component
nlp = spacy.load("./ner_model")

# Step 3: Load the CSV file
file_path = r"C:\Users\Vishwas\Desktop\Interview docs\Vanilla Steel\supplier_data_standardization_for_metal_trading\data\final_combined_output.csv"  # Update with the correct file path
df = pd.read_csv(file_path)

# Step 4: Extract entities from the 'material' column
materials = df['material'].astype(str)

# Function to extract entities and assign them to the respective columns
def extract_entities(text):
    doc = nlp(text)
    entities = {'MATERIAL_ID': '', 'MATERIAL_NAME': '', 'DIMENSIONS': '', 'MATERIAL_GRADE': '',
                'COATING_TYPE': '', 'FINISH_TYPE': '', 'ADDITIONAL_SPEC': ''}
    for ent in doc.ents:
        if ent.label_ in entities:
            entities[ent.label_] = ent.text
    return entities

# Step 5: Apply the function to each material entry and store the results
extracted_entities = materials.apply(extract_entities)
extracted_df = pd.DataFrame(extracted_entities.tolist())

# Combine the extracted columns with the original DataFrame
final_df = pd.concat([df, extracted_df], axis=1)

# Step 6: Save the final DataFrame to a new CSV file
output_file_path = r"C:\Users\Vishwas\Desktop\Interview docs\Vanilla Steel\supplier_data_standardization_for_metal_trading\data\final_combined_output_with_entities.csv"  # Update the file path as needed
final_df.to_csv(output_file_path, index=False)

print(f"Entities extracted and saved to: {output_file_path}")
