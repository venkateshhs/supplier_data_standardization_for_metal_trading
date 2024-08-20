import spacy
from spacy.training import Example
from sklearn.metrics import precision_score, recall_score, f1_score

# Step 1: Load the trained model
nlp = spacy.load("./ner_model")

# Step 2: Define a token-based test dataset
TEST_DATA = [
    ("DX51D +Z140 Ma-C 1,50 x 1350,00 x 2850,00",
     ["MATERIAL_ID", "MATERIAL_ID", "MATERIAL_NAME", "DIMENSIONS", "DIMENSIONS", "DIMENSIONS", "DIMENSIONS"]),
    ("S235JR geolied 1,75 x 1250,00 mm",
     ["MATERIAL_ID", "MATERIAL_NAME", "DIMENSIONS", "DIMENSIONS", "DIMENSIONS"]),
    ("CR 0.65x1080 XCV G7/7 MB O",
     ["MATERIAL_ID", "DIMENSIONS", "MATERIAL_NAME", "MATERIAL_NAME", "MATERIAL_NAME", "MATERIAL_NAME"]),
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
]
# Step 3: Define a function to evaluate the model
def evaluate_model(nlp, examples):
    true_labels = []
    pred_labels = []

    for input_text, true_label in examples:
        doc = nlp(input_text)

        # Ensure the number of true labels matches the number of tokens in the doc
        if len(true_label) != len(doc):
            print(f"Warning: Token length mismatch in '{input_text}'")
            continue

        true_labels.extend(true_label)

        # Get the predicted labels from the doc
        pred_label = []
        for token in doc:
            if token.ent_type_:
                pred_label.append(token.ent_type_)
            else:
                pred_label.append("O")  # "O" for tokens outside any entity
        pred_labels.extend(pred_label)

    # Ensure the lengths of true_labels and pred_labels match
    assert len(true_labels) == len(pred_labels), "Label lengths do not match!"

    # Calculate precision, recall, and F1-score
    precision = precision_score(true_labels, pred_labels, average='weighted', zero_division=0)
    recall = recall_score(true_labels, pred_labels, average='weighted', zero_division=0)
    f1 = f1_score(true_labels, pred_labels, average='weighted', zero_division=0)

    return {"precision": precision, "recall": recall, "f1": f1}

# Step 4: Evaluate the model on the test dataset
scores = evaluate_model(nlp, TEST_DATA)

# Step 5: Print the evaluation results
print(f"Precision: {scores['precision']:.3f}")
print(f"Recall: {scores['recall']:.3f}")
print(f"F1-Score: {scores['f1']:.3f}")
