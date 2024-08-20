import re
import spacy
import pandas as pd
from spacy.matcher import Matcher
from spacy.tokens import DocBin
from spacy.training.example import Example
from spacy.language import Language
from spacy.util import minibatch, compounding
import random


def preprocess_dimensions(text):
    # print(text)
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


    text = text.replace('*', 'x')
    # print(text)
    return text



# Step 2: Define the training data with adjusted patterns for dimensions
TRAIN_DATA = [
    ("DX51D +Z140 Ma-C 1,50x1350,00x2850,00",
     ["MATERIAL_NAME", "COATING_TYPE", "FINISH_TYPE", "DIMENSIONS"]),
    ("DX51D +AZ150  Ma-C 1,00x1250,00mm AFP",
     ["MATERIAL_NAME", "COATING_TYPE", "FINISH_TYPE", "DIMENSIONS", "ADDITIONAL_SPEC"]),
    ("DTEST +Z1895 St-C 1,50x1350,00x1234,00",
     ["MATERIAL_NAME", "COATING_TYPE", "FINISH_TYPE", "DIMENSIONS"]),
    ("DY51D +Z15  Va-C 1,00x1250,00mm PPP",
     ["MATERIAL_NAME", "COATING_TYPE", "FINISH_TYPE", "DIMENSIONS", "ADDITIONAL_SPEC"]),
    ("S235JR geolied 1,75x1250,00mm",
     ["MATERIAL_NAME", "COATING_TYPE", "DIMENSIONS"]),
    ("DC01 licht geolied 2,50x1500mm",
     ["MATERIAL_NAME", "COATING_TYPE", "COATING_TYPE", "DIMENSIONS"]),
    ("DX51D +Z100 Ma-C 0,57x1250,00mm",
     ["MATERIAL_NAME", "COATING_TYPE", "FINISH_TYPE", "DIMENSIONS"]),
    ("S550 GD+ZM175 MAC 2x1070mm",
     ["MATERIAL_NAME", "COATING_TYPE", "FINISH_TYPE", "DIMENSIONS"]),
    ("S235  ongeb/ ongeol traan  5x1500mm",
     ["MATERIAL_NAME", "COATING_TYPE", "COATING_TYPE", "FINISH_TYPE", "DIMENSIONS"]),
    ("DX51D+Z275 0,75*1250",
     ["MATERIAL_NAME", "DIMENSIONS"]),
    ("CR 0.65x1080 XCV G7/7 MB O",
     ["MATERIAL_NAME", "DIMENSIONS", "MATERIAL_GRADE", "COATING_TYPE", "FINISH_TYPE", "ADDITIONAL_SPEC"]),
    ("HDC 0.75x1270 GXE G6/6 MB O",
     ["MATERIAL_NAME", "DIMENSIONS", "MATERIAL_GRADE", "COATING_TYPE", "FINISH_TYPE", "ADDITIONAL_SPEC"]),
    ("CR 1.5x1487 XE320D A O",
     ["MATERIAL_NAME", "DIMENSIONS", "MATERIAL_GRADE", "FINISH_TYPE", "ADDITIONAL_SPEC"]),
    ("HRP 2.2x1200 HE360D O",
     ["MATERIAL_NAME", "DIMENSIONS", "MATERIAL_GRADE", "ADDITIONAL_SPEC"]),
    ("HRP 2x1360 HR2 O",
     ["MATERIAL_NAME", "DIMENSIONS", "MATERIAL_GRADE", "ADDITIONAL_SPEC"]),
    ("HRP 2x193 HES O",
     ["MATERIAL_NAME", "DIMENSIONS", "MATERIAL_GRADE", "ADDITIONAL_SPEC"]),
    ("2ND QUALITY CR SLIT",
     ["MATERIAL_GRADE", "MATERIAL_GRADE", "MATERIAL_NAME", "ADDITIONAL_SPEC"]),
    ("HDC 0.75x1725 CR300LA-GI 60/60 MB O",
     ["MATERIAL_NAME", "DIMENSIONS", "MATERIAL_GRADE", "COATING_TYPE", "FINISH_TYPE", "ADDITIONAL_SPEC"]),
    # Additional examples
    ("DX51D +Z140 Ma-C 4,00x775,00x2850,00",
     ["MATERIAL_NAME", "COATING_TYPE", "FINISH_TYPE", "DIMENSIONS"]),
    ("DX51D +Z140 Ma-C 1,50x1350,00x2850,00mm",
     ["MATERIAL_NAME", "COATING_TYPE", "FINISH_TYPE", "DIMENSIONS"]),
    ("DD11 geolied 1,50x122,00mm",
     ["MATERIAL_NAME", "DIMENSIONS"]),
    ("CR3 1,5x1250,00mm",
     ["MATERIAL_NAME", "DIMENSIONS"]),
    ("DC01 licht geolied 2,50x1500 mm",
     ["MATERIAL_NAME", "COATING_TYPE", "COATING_TYPE", "DIMENSIONS"]),
    ("DC01 licht geolied 2,50x1500mm",
     ["MATERIAL_NAME", "COATING_TYPE", "COATING_TYPE", "DIMENSIONS"]),
    ("S235JR geolied 2,50x1465,00mm",
     ["MATERIAL_NAME", "COATING_TYPE", "DIMENSIONS"]),
    ("DD11 geolied 2,00x1250,00x3500,00mm",
     ["MATERIAL_NAME", "COATING_TYPE", "DIMENSIONS"]),
    ("S350GD +ZM310 Ma-C 3,00x165,00mm",
     ["MATERIAL_NAME", "COATING_TYPE", "FINISH_TYPE", "DIMENSIONS"]),
    ("HRP 2.2x1200 HE360D O",
     ["MATERIAL_NAME", "DIMENSIONS", "MATERIAL_GRADE", "ADDITIONAL_SPEC"]),
    ("HDC 1x1000 HX300LAD+Z 140 MB O",
     ["MATERIAL_NAME", "DIMENSIONS", "MATERIAL_GRADE", "COATING_TYPE", "FINISH_TYPE", "ADDITIONAL_SPEC"]),
    ("S500MC Oiled 9,99*1500",
     ["MATERIAL_NAME", "COATING_TYPE", "DIMENSIONS"])

]

# Step 3: Load the CSV file
file_path = r'C:\Users\Vishwas\Desktop\Interview docs\Vanilla Steel\supplier_data_standardization_for_metal_trading\data\final_combined_output.csv'
df = pd.read_csv(file_path)

# Preprocess the 'material' column
df['material'] = df['material'].apply(preprocess_dimensions)

# Step 4: Load a blank model
nlp = spacy.blank("en")

# Step 5: Define the custom component to merge hyphenated words
@Language.component("merge_hyphenated_words")
def merge_hyphenated_words(doc):
    matcher = Matcher(nlp.vocab)
    pattern = [
        {"TEXT": {"REGEX": "^[a-zA-Z0-9]+$"}},  # Alphanumeric before hyphen
        {"ORTH": "-"},  # Hyphen
        {"TEXT": {"REGEX": "^[a-zA-Z0-9]+$"}}  # Alphanumeric after hyphen
    ]
    # Pattern for "+" sign followed by alphanumeric (e.g., "+Z140")
    plus_pattern = [
        {"ORTH": "+"},  # Plus sign
        {"TEXT": {"REGEX": "^[a-zA-Z0-9]+$"}}  # Alphanumeric after plus sign
    ]

    slash_pattern = [
        {"TEXT": {"REGEX": "^[a-zA-Z0-9]+$"}},  # Alphanumeric after plus sign
         {"ORTH": "/"}  # Plus sign
    ]

    matcher.add("PLUS_ALPHANUMERIC", [plus_pattern])
    matcher.add("SLASH_PATTERN", [slash_pattern])
    matcher.add("HYPHENATED", [pattern])
    matches = matcher(doc)
    with doc.retokenize() as retokenizer:
        for match_id, start, end in matches:
            span = doc[start:end]
            retokenizer.merge(span)
    return doc

# Add the merge_hyphenated_words function to the pipeline before adding 'ner'
nlp.add_pipe("merge_hyphenated_words")

# Step 6: Create the NER component and add it to the pipeline
ner = nlp.add_pipe("ner")

# Step 7: Convert the training data to spaCy's DocBin format
db = DocBin()

for text, labels in TRAIN_DATA:
    doc = nlp.make_doc(text)
    ents = []
    for i, token in enumerate(doc):
        if i < len(labels):
            label = labels[i]
            span = doc.char_span(token.idx, token.idx + len(token), label=label)
            if span is not None:
                ents.append(span)
    doc.ents = ents
    db.add(doc)

db.to_disk("./train.spacy")

# Add the labels to the NER component
for text, labels in TRAIN_DATA:
    for label in labels:
        ner.add_label(label)

# Step 8: Start training
optimizer = nlp.begin_training()


best_loss = float('inf')
patience = 5  # Number of iterations to wait before stopping if no improvement
patience_counter = 0

# Training loop with early stopping
for itn in range(50):  # Set initial maximum number of iterations
    random.shuffle(TRAIN_DATA)
    losses = {}
    batches = minibatch(TRAIN_DATA, size=compounding(4.0, 32.0, 1.001))

    for batch in batches:
        texts, labels = zip(*batch)
        examples = []
        for text, label in zip(texts, labels):
            doc = nlp.make_doc(text)
            ents = []
            for i, token in enumerate(doc):
                if i < len(label):
                    ents.append((token.idx, token.idx + len(token), label[i]))
            spans = [doc.char_span(start, end, label=l) for start, end, l in ents]
            doc.ents = [span for span in spans if span is not None]
            examples.append(
                Example.from_dict(doc, {"entities": [(ent.start_char, ent.end_char, ent.label_) for ent in doc.ents]}))
        nlp.update(examples, sgd=optimizer, drop=0.35, losses=losses)

    print(f"Iteration {itn + 1}, Losses: {losses}")

    # Early stopping logic
    current_loss = sum(losses.values())
    if current_loss < best_loss:
        best_loss = current_loss
        patience_counter = 0  # Reset the counter
    else:
        patience_counter += 1

    if patience_counter >= patience:
        print("Early stopping: No improvement in loss for the last 5 iterations.")
        break

# Step 9: Save the model to disk
nlp.to_disk("./ner_model")

# Step 10: Load the trained model and test it
nlp = spacy.load("./ner_model")

# Step 11: Apply the model to the CSV data and save the results
extracted_entities = []

for material in df['material']:
    doc = nlp(material)
    entities = {}

    for ent in doc.ents:
        print("ent", ent)
        if ent.label_ in entities:
            # If the label already exists, append the new entity text to it
            print("ent.text", ent.text,"ent.label_", ent.label_)
            entities[ent.label_] += f" {ent.text}"
        else:
            print("ent.text", ent.text,"ent.label_", ent.label_)
            entities[ent.label_] = f" {ent.text}"

    extracted_entities.append(entities)

# Convert extracted entities to a DataFrame
entities_df = pd.DataFrame(extracted_entities)

# Combine with the original DataFrame
final_df = pd.concat([df, entities_df], axis=1)

# Save the final DataFrame to a CSV file
output_file_path = r'C:\Users\Vishwas\Desktop\Interview docs\Vanilla Steel\supplier_data_standardization_for_metal_trading\data\final_combined_output_with_entities.csv'  # Update the file path as needed
final_df.to_csv(output_file_path, index=False)

print(f"Entities extracted and saved to: {output_file_path}")
