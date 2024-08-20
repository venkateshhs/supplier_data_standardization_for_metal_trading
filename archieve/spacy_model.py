import spacy
from spacy.training import Example
from spacy.pipeline.textcat import Config, Config, Config
from spacy.training import Example
import pandas as pd
import os

# Load pre-trained spaCy model
nlp = spacy.load("en_core_web_sm")

# Add a new NER component to the pipeline
if "ner" not in nlp.pipe_names:
    ner = nlp.add_pipe("ner", last=True)
else:
    ner = nlp.get_pipe("ner")

# Add new labels to the NER component
labels = ["MATERIAL_ID", "MATERIAL_NAME", "QUANTITY", "UNIT", "DIMENSIONS", "SUPPLIER", "MATERIAL_TYPE", "GRADE", "COATING", "FINISH", "ADDITIONAL_SPEC"]
for label in labels:
    ner.add_label(label)

# Prepare training data
def create_training_data(df):
    training_data = []
    for _, row in df.iterrows():
        text = row['Parsed']
        entities = {
            "entities": []
        }
        for label in labels:
            # Dummy implementation, replace with actual logic to find entities
            start = text.find(label)  # Find the position of the label
            if start != -1:
                end = start + len(label)
                entities["entities"].append((start, end, label))
        training_data.append((text, entities))
    return training_data

# Load data
data_folder = os.path.join(os.path.dirname(os.getcwd()), 'data')
file3_path = os.path.join(data_folder, 'source_3_description')
df = pd.read_csv(file3_path)

# Create training data
train_data = create_training_data(df)

# Training the model
optimizer = nlp.begin_training()
for epoch in range(10):
    losses = {}
    for text, annotations in train_data:
        doc = nlp.make_doc(text)
        example = Example.from_dict(doc, annotations)
        nlp.update([example], drop=0.5, losses=losses)
    print(f"Epoch {epoch}: Losses {losses}")

# Save the model
output_path = os.path.join(data_folder, 'custom_ner_model')
nlp.to_disk(output_path)
