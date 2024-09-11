import re
import spacy
import pandas as pd
import logging
import random
from spacy.matcher import Matcher
from spacy.tokens import DocBin
from spacy.training.example import Example
from spacy.language import Language
from spacy.util import minibatch, compounding
from supplier_data_standardization.utils import get_file_path, get_training_data, setup_logging


def preprocess_dimensions(text: str) -> str:
    """
    Preprocesses dimension-related text by normalizing the format.

    Parameters:
    text (str): The text to preprocess.

    Returns:
    str: The preprocessed text.
    """
    try:
        # Replace patterns like '9,99 * 1500' by removing spaces around '*'
        # This ensures dimensions like '9,99 * 1500' are standardized as '9,99*1500'
        text = re.sub(r'(\d+,\d+)\s*\*\s*(\d+)', r'\1*\2', text)

        # Replace patterns like '9 * 1500' by removing spaces around '*'
        # This ensures dimensions like '9 * 1500' are standardized as '9*1500'
        text = re.sub(r'(\d+)\s*\*\s*(\d+)', r'\1*\2', text)

        # Handle three-part dimensions with 'x' separators (e.g., '1,50 x 1350,00 x 2850,00')
        # The regex matches three comma-separated dimensions and attaches optional units like mm, cm, m, etc.
        three_dim_pattern = r'(\d+,\d+)\s*x\s*(\d+,\d+)\s*x\s*(\d+,\d+)\s*(mm|cm|m|kg|g)?'
        text = re.sub(three_dim_pattern, r'\1x\2x\3\4', text)

        # Handle two-part dimensions with 'x' separator, and ensure units like mm/cm/m are attached correctly
        # This ensures patterns like '9,99 x 1500 mm' are normalized without extra spaces (e.g., '9,99x1500mm')
        two_dim_with_unit_pattern = r'(\d+,\d+|\d+)\s*x\s*(\d+,\d+|\d+)\s*(mm|cm|m|kg|g)?'
        text = re.sub(two_dim_with_unit_pattern, r'\1x\2\3', text)

        # Handle two-part dimensions without units (e.g., '1,50 x 1500')
        # This ensures dimensions like '1,50 x 1500' are standardized as '1,50x1500'
        two_dim_no_unit_pattern = r'(\d+,\d+|\d+)\s*x\s*(\d+,\d+)'
        text = re.sub(two_dim_no_unit_pattern, r'\1x\2', text)

        # Handle dimensions with '*' separator and units attached
        # For example, it converts '1,50 * 1500 mm' to '1,50*1500mm'
        two_dim_star_with_unit_pattern = r'(\d+,\d+|\d+)\s*\*\s*(\d+)\s*(mm|cm|m|kg|g)?'
        text = re.sub(two_dim_star_with_unit_pattern, r'\1*\2\3', text)

        # Handle dimensions with '*' separator but no unit attached
        # For example, it converts '1,50 * 1500' to '1,50*1500'
        two_dim_star_no_unit_pattern = r'(\d+,\d+|\d+)\s*\*\s*(\d+)'
        text = re.sub(two_dim_star_no_unit_pattern, r'\1*\2', text)

        # Handle single-part dimension followed by a unit, ensuring no space between the number and unit
        # For example, '1250,00 mm' is converted to '1250,00mm'
        single_dim_with_unit_pattern = r'(\d+,\d+|\d+)\s*(mm|cm|m|kg|g)'
        text = re.sub(single_dim_with_unit_pattern, r'\1\2', text)

        # Remove any space before units like mm, cm, or m if there is a number followed by a space
        # For example, '1250 mm' becomes '1250mm'
        text = re.sub(r'(\d)\s+(?=mm|cm|m)', r'\1', text)

        # Ensure that a space exists between the last dimension and any trailing text part
        # For example, '1250x1500AFP' is converted to '1250x1500 AFP'
        text = re.sub(r'(\d+x\d+)(\s*)([A-Za-z])', r'\1 \3', text)

        # Replace '*' with 'x' to ensure consistency in the final output
        # For example, '1250*1500' becomes '1250x1500'
        text = text.replace('*', 'x')

        return text
    except Exception as e:
        logging.error(f"Error preprocessing dimensions for text: {text} - {e}")
        return text  # Return the original text if an error occurs


@Language.component("merge_hyphenated_words")
def merge_hyphenated_words(doc: spacy.tokens.Doc) -> spacy.tokens.Doc:
    """
    Merges hyphenated words and certain patterns in the document.

    Parameters:
    doc (spacy.tokens.Doc): The document to process.

    Returns:
    spacy.tokens.Doc: The processed document with merged tokens.
    """
    try:
        matcher = Matcher(doc.vocab)
        pattern = [{"TEXT": {"REGEX": "^[a-zA-Z0-9]+$"}}, {"ORTH": "-"}, {"TEXT": {"REGEX": "^[a-zA-Z0-9]+$"}}]
        plus_pattern = [{"ORTH": "+"}, {"TEXT": {"REGEX": "^[a-zA-Z0-9]+$"}}]
        slash_pattern = [{"TEXT": {"REGEX": "^[a-zA-Z0-9]+$"}}, {"ORTH": "/"}]

        matcher.add("PLUS_ALPHANUMERIC", [plus_pattern])
        matcher.add("SLASH_PATTERN", [slash_pattern])
        matcher.add("HYPHENATED", [pattern])
        matches = matcher(doc)
        with doc.retokenize() as retokenizer:
            for match_id, start, end in matches:
                span = doc[start:end]
                retokenizer.merge(span)
        return doc
    except Exception as e:
        logging.error(f"Error merging hyphenated words: {e}")
        return doc


def train_ner_model(train_data: list) -> spacy.Language:
    """
    Trains an NER model using the provided training data.

    Parameters:
    train_data (list): A list of tuples containing text and labels for training.

    Returns:
    spacy.Language: The trained spaCy NER model.
    """
    try:
        nlp = spacy.blank("en")
        nlp.add_pipe("merge_hyphenated_words")
        ner = nlp.add_pipe("ner")

        db = DocBin()

        for text, labels in train_data:
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

        for text, labels in train_data:
            for label in labels:
                ner.add_label(label)

        optimizer = nlp.begin_training()
        best_loss = float('inf')
        patience = 5
        patience_counter = 0

        for itn in range(50):
            random.shuffle(train_data)
            losses = {}
            batches = minibatch(train_data, size=compounding(4.0, 32.0, 1.001))

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
                            Example.from_dict(doc, {
                                "entities": [(ent.start_char, ent.end_char, ent.label_) for ent in doc.ents]}))
                    nlp.update(examples, sgd=optimizer, drop=0.35, losses=losses)

            logging.info(f"Iteration {itn + 1}, Losses: {losses}")

            current_loss = sum(losses.values())
            if current_loss < best_loss:
                best_loss = current_loss
                patience_counter = 0
            else:
                patience_counter += 1

            if patience_counter >= patience:
                logging.info("Early stopping: No improvement in loss for the last 5 iterations.")
                break

        nlp.to_disk("./ner_model")
        return nlp
    except Exception as e:
        logging.error(f"Error training NER model: {e}")
        return None


def combine_dataframes(df1: pd.DataFrame, df2: pd.DataFrame) -> pd.DataFrame:
    """
    Combines two DataFrames by aligning columns and appending rows.

    Parameters:
    df1 (pd.DataFrame): The first DataFrame.
    df2 (pd.DataFrame): The second DataFrame, which will be appended to the first.

    Returns:
    pd.DataFrame: The combined DataFrame with values from the second DataFrame appended to the first.
    """
    # Align the DataFrames based on the index
    combined_df = pd.concat([df1, df2], axis=1)

    # Combine overlapping columns by filling NaNs in df1 with values from df2
    for column in df2.columns:
        if column in df1.columns:
            combined_df[column] = combined_df[column].combine_first(df2[column])

    return combined_df


def extract_entities_from_csv(nlp: spacy.Language, csv_path: str, output_path: str) -> None:
    """
    Applies the trained NER model to extract entities from the 'material' column of a CSV file,
    then merges the results back into the original DataFrame, preserving all rows.

    Parameters:
    nlp (spacy.Language): The trained spaCy NER model.
    csv_path (str): The path to the CSV file to process.
    output_path (str): The path to save the CSV file with extracted entities.
    """
    try:
        nlp = spacy.load("./ner_model")
        df = pd.read_csv(csv_path)
        print(df.columns)
        # Add the missing columns with empty strings
        df['ADDITIONAL_SPEC'] = ''
        df['FINISH_TYPE'] = ''
        print(df.columns)

        # Iterate over each row in the DataFrame
        for index, row in df.iterrows():
            if pd.notna(row['material']):
                # Preprocess the material column
                material = preprocess_dimensions(row['material'])

                # Apply the NER model
                doc = nlp(material)
                entities = {}

                for ent in doc.ents:
                    if ent.label_ in entities:
                        entities[ent.label_] += f" {ent.text}"
                    else:
                        entities[ent.label_] = f" {ent.text}"

                # Update the row with extracted entities
                for label, value in entities.items():
                    df.at[index, label] = value

        # Reorder the columns as required
        column_order = [
            'article id', 'MATERIAL_NAME', 'weight', 'quantity', 'material',
            'MATERIAL_GRADE', 'COATING_TYPE', 'FINISH_TYPE', 'DIMENSION', 'ADDITIONAL_SPEC'
        ]

        # Ensure all columns are present in final_df before reordering
        final_df = df.reindex(columns=column_order)

        # Save the final DataFrame to a CSV file
        final_df.to_csv(output_path, index=False)

        logging.info(f"Entities extracted and saved to: {output_path}")
    except Exception as e:
        logging.error(f"Error extracting entities from CSV: {e}")


def main():
    """
    The main function that orchestrates NER training and entity extraction.
    """
    try:
        setup_logging()

        # Step 2: Define the training data with adjusted patterns for dimensions
        TRAIN_DATA = get_training_data()

        # Train the NER model
        nlp = train_ner_model(TRAIN_DATA)

        if nlp is not None:
            # Extract entities from the CSV file and save the output
            csv_input_path = get_file_path("final_combined_output.csv")
            csv_output_path = get_file_path("final_combined_output_with_entities.csv")
            extract_entities_from_csv(nlp, csv_input_path, csv_output_path)

            logging.info(f"Entities extracted and saved to: {csv_output_path}")
        else:
            logging.error("NER model training failed. Skipping entity extraction.")

    except Exception as e:
        logging.error(f"Error in main execution: {e}")


if __name__ == "__main__":
    main()
