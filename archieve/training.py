import spacy

# Load the trained model
nlp = spacy.load("./ner_model")

# Test dataset
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

# Check the tokenization
for input_text, true_label in TEST_DATA:
    doc = nlp(input_text)
    tokens = [token.text for token in doc]
    print(f"Text: {input_text}")
    print(f"Tokens: {tokens}")
    print(f"True Labels: {true_label}")
    print(f"Token Length: {len(tokens)}, Label Length: {len(true_label)}")
    print("===")
