import spacy
from spacy.tokens import DocBin
from spacy.training.example import Example
from spacy.util import minibatch, compounding
import random

# Step 1: Define the training data
TRAIN_DATA = [
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

# Step 2: Load a blank model and customize the tokenizer
nlp = spacy.blank("en")

# Customize the tokenizer to treat hyphenated words as a single token
prefix_re = spacy.util.compile_prefix_regex(nlp.Defaults.prefixes)
suffix_re = spacy.util.compile_suffix_regex(nlp.Defaults.suffixes)
infix_re = spacy.util.compile_infix_regex([r'(?<=[A-Za-z])-(?=[A-Za-z0-9])'])

nlp.tokenizer = spacy.tokenizer.Tokenizer(
    nlp.vocab,
    prefix_search=prefix_re.search,
    suffix_search=suffix_re.search,
    infix_finditer=infix_re.finditer,
)

# Step 3: Convert the training data to spaCy's DocBin format
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

# Step 4: Create the NER component and add it to the pipeline
ner = nlp.add_pipe("ner")

# Add the labels to the NER component
for text, labels in TRAIN_DATA:
    for label in labels:
        ner.add_label(label)

# Step 5: Start training
optimizer = nlp.begin_training()

# Training loop
for itn in range(50):  # Number of iterations
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
            examples.append(Example.from_dict(doc, {"entities": [(ent.start_char, ent.end_char, ent.label_) for ent in doc.ents]}))
        nlp.update(examples, sgd=optimizer, drop=0.35, losses=losses)
    print(f"Iteration {itn + 1}, Losses: {losses}")

# Step 6: Save the model to disk
nlp.to_disk("./ner_model")

# Step 7: Load the trained model and test it
nlp = spacy.load("./ner_model")

# Test the model
test_text = "HDC 0.75x1010 GX-ES G10/10 MB O"
doc = nlp(test_text)

# Print the entities
for ent in doc.ents:
    print(f"Text: {ent.text}, Label: {ent.label_}")
