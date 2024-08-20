import os
import pandas as pd
import spacy
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.pipeline import Pipeline
from sklearn.svm import SVC
from sklearn.metrics import classification_report
from spacy.tokens import DocBin

# Load the CSV file
file_path = r'C:\Users\Vishwas\Desktop\Interview docs\Vanilla Steel\supplier_data_standardization_for_metal_trading\data\final_combined_output.csv'  # Replace with your file path
data = pd.read_csv(file_path)
data = pd.read_csv(file_path)

# Load the spaCy model for tokenization
nlp = spacy.load('en_core_web_sm')

# Function to tokenize the 'material' column
def tokenize_material(text):
    doc = nlp(text)
    return [token.text for token in doc]

# Apply tokenization to the 'material' column
data['tokens'] = data['material'].apply(tokenize_material)

# For demonstration purposes, we'll create some mock labels
# Assign labels based on the presence of certain keywords
def label_row(row):
    if "Z140" in row:
        return "material_name"
    elif "1350,00" in row:
        return "dimensions"
    elif "2850,00" in row:
        return "dimensions"
    else:
        return "other"

# Apply the mock labeling function
data['label'] = data['material'].apply(label_row)

# Ensure that there are at least two classes
print(data['label'].value_counts())

# Prepare the dataset for training
X_train, X_test, y_train, y_test = train_test_split(data['material'], data['label'], test_size=0.2, random_state=42)

# Use a simple pipeline with CountVectorizer and SVM for classification
pipeline = Pipeline([
    ('vectorizer', CountVectorizer()),
    ('classifier', SVC(kernel='linear'))
])

# Train the classifier
pipeline.fit(X_train, y_train)

# Predict on the test set
y_pred = pipeline.predict(X_test)

# Print classification report
print(classification_report(y_test, y_pred))

# Example on how to classify a new material
new_material = "DX51D +Z140 Ma-C 1,50 x 1350,00 x 2850,00"
predicted_label = pipeline.predict([new_material])
print(f"The predicted label for the material '{new_material}' is: {predicted_label[0]}")
