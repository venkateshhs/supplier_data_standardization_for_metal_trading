# **Table of Contents**

1. [Supplier Data Standardization for Metal Trading](#supplier-data-standardization-for-metal-trading)
2. [Setup](#setup)
   - [Clone the repository](#clone-the-repository)
   - [Create a virtual environment](#create-a-virtual-environment)
   - [Install the required dependencies](#install-the-required-dependencies)
   - [Download Spacy](#download-spacy)
3. [Running the Project](#running-the-project)
   - [Step 1: Run the Main Script](#step-1-run-the-main-script)
   - [Step 2: Run the NER Model](#step-2-run-the-ner-model)
4. [Data Requirements](#data-requirements)
5. [Running Tests](#running-tests)
6. [Data Processing and NLP Training Overview](#data-processing-and-nlp-training-overview)
   - [Data Processing Steps](#data-processing-steps)
     - [Source1.xlsx](#source1xlsx)
     - [Source2.xlsx](#source2xlsx)
     - [Source3.xlsx](#source3xlsx)
   - [Dimension Processing](#dimension-processing)
   - [NLP Model Training](#nlp-model-training)
     - [Special Patterns](#special-patterns)
   - [Training Loop and Model Saving](#training-loop-and-model-saving)
   - [Entity Extraction and Final Output](#entity-extraction-and-final-output)
7. [Logging](#logging)
8. [TODOs and Future Enhancements](#todos-and-future-enhancements)
   - [Consideration of Additional Columns](#consideration-of-additional-columns)
   - [Article ID Standardization](#article-id-standardization)
   - [Standardized Dictionary for COATING_TYPE and FINISH_TYPE](#standardized-dictionary-for-coating_type-and-finish_type)
   - [Standardized Material Grade](#standardized-material-grade)
   - [Improve NER Training](#improve-ner-training)
   - [Dimension Processing Errors](#dimension-processing-errors)
   - [Tokenization and Prediction Mismatches](#tokenization-and-prediction-mismatches)
   - [Exploring GPT Embeddings for Improved Accuracy](#exploring-gpt-embeddings-for-improved-accuracy)


# **Supplier Data Standardization for Metal Trading**

This project is designed to standardize and process supplier data in the metal trading industry. It leverages Python libraries such as `pandas` and `spaCy` to preprocess data, extract entities using Natural Language Processing (NLP), and produce a standardized output.
Final output CSV file can be found here : https://github.com/venkateshhs/supplier_data_standardization_for_metal_trading/blob/main/data/final_combined_output_with_entities.csv
## **Setup**

1. **Clone the repository**:
   ```bash
   git clone https://github.com/venkateshhs/supplier_data_standardization_for_metal_trading.git
   cd supplier_data_standardization_for_metal_trading
   
2. **Create a virtual environment:**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows, use `.\venv\Scripts\activate`

3. **Install the required dependencies:**:
   ```bash
   pip install -r requirements.txt

4. **Download Spacy:**:
   ```bash
   python -m spacy download en_core_web_sm
   
## **Running the Project**
1. **Step 1: Run the Main Script**
The main script is responsible for processing the raw data files, performing initial data cleaning, and merging the data from multiple sources.
```bash
   set PYTHONPATH=your_folder_path\supplier_data_standardization_for_metal_trading
   cd supplier_data_standardization
   python main.py
```

This script:
Reads the input data from the data directory.
Processes the data by merging and cleaning it.
Saves the processed data in the data/final_combined_output.csv file.

2. **Step 2: Run the NER Model**
After processing the data with the main script, the NER (Named Entity Recognition) model is applied to extract specific entities from the material column.
```bash
   set PYTHONPATH=your_folder_path\supplier_data_standardization_for_metal_trading
   cd supplier_data_standardization
   python ner_model.py
```

This script:
Reads the processed data from data/final_combined_output.csv.
Applies the spaCy NER model to extract entities.
Merges the extracted entities back into the original data.
Saves the final output to data/final_combined_output_with_entities.csv.

## Data Requirements
Data Files: Ensure that the required data files (source1.xlsx, source2.xlsx, source3.xlsx) are present in the data directory.
Output: The processed files will be saved back into the data directory.

## Running Tests
The project includes unit tests to validate its functionality. The tests are located in the unittest/ directory.

```bash
   python -m unittest unittest.merge_hyphenated_words
```


If there is any error either run the Unit test through pycharm or any IDE or set  

```bash
   set PYTHONPATH=your_folder_path\supplier_data_standardization_for_metal_trading
   python -m unittest nlp_test.py
```

# Data Processing and NLP Training Overview

This project involves processing and standardizing data from multiple Excel sources, followed by training a Named Entity Recognition (NER) model to identify and categorize components within material descriptions.

## Data Processing Steps

1. **Source1.xlsx**:
   - **Column Renaming**: Columns were renamed to standardize the data:
     - `'Quality/Choice'` ➜ `'MATERIAL_GRADE'`
     - `'Grade'` ➜ `'MATERIAL_NAME'`
     - `'Finish'` ➜ `'COATING_TYPE'`
     - `'Gross weight (kg)'` ➜ `'weight'`
     - `'Thickness (mm)'` and `'Width (mm)'` were used to create a new `DIMENSION` column.
   - **Dimension Creation**: The `Thickness` and `Width` columns were merged into a single `DIMENSION` column, such as `5x50` for a 5mm thickness and 50mm width.
   - **Data Cleaning**: Rows with missing values (`NaN`) were dropped to ensure data quality.

2. **Source2.xlsx**:
   - **Multiple Sheets Handling**: Data was read from two sheets—"First choice" and "2nd choice".
   - **Header Cleaning**: Headers in both sheets were cleaned and standardized, with any repeated headers removed.
   - **Data Filtering**: Only necessary columns were selected, and rows with `NaN` values in critical columns were removed.

3. **Source3.xlsx**:
   - **Column Renaming**: Columns were renamed to standardize the data.
   - **Unit Conversion**: The `weight` column was recalculated in kilograms based on the provided unit (grams, milligrams, pounds, etc.), and the `Unit` column was removed.
   - **Column Selection**: Only key columns were retained after processing for further analysis.

## Dimension Processing

Dimension-related data (e.g., measurements in millimeters, centimeters, or meters) was carefully processed to ensure consistency across the dataset. The `preprocess_dimensions` function was used to standardize different formats of dimension expressions into a unified format. This included:

- **Replacing Symbols**: Dimensions separated by different symbols like `*` or `x` were unified into a consistent format (e.g., `5*50` became `5x50`).
- **Handling Units**: Dimension measurements were normalized regardless of whether they included units like `mm` or `cm`.
- **Merging Dimensions**: Dimensions with multiple components (e.g., `Length x Width x Height`) were merged into a single string.

This preprocessing step ensured that all dimensions were uniformly formatted before they were fed into the NER model for entity recognition.

## NLP Model Training

After merging the processed data from all sources, the `material` column was used to train an NER model. This model was trained to recognize and label different components within the material descriptions. Here are some examples of the training data:

- **Example 1**:
  - Input: `"DX51D +Z140 Ma-C 1,50x1350,00x2850,00"`
  - Labels: `["MATERIAL_NAME", "COATING_TYPE", "FINISH_TYPE", "DIMENSION"]`
  
- **Example 2**:
  - Input: `"S235JR geolied 2,50x1465,00mm"`
  - Labels: `["MATERIAL_NAME", "COATING_TYPE", "DIMENSION"]`

### Special Patterns

During the training, several special patterns were added to the model's pipeline to enhance its recognition capabilities:
- **`PLUS_ALPHANUMERIC`**: Handles cases like `+Z140`.
- **`SLASH_PATTERN`**: Recognizes patterns like `Ma-C`.
- **`HYPHENATED`**: Merges hyphenated words like `geolied`.

## Training Loop and Model Saving

The NER model was trained iteratively over 50 cycles (iterations). During each iteration:

- **Data Shuffling and Batching**: The training data was shuffled to ensure that the model does not learn patterns specific to the order of the data. The data was then divided into smaller batches to improve the training process's efficiency and stability.

- **Loss Calculation**: After each batch, the model's performance was evaluated by calculating the loss, which measures how far the model's predictions are from the actual labels. This loss is crucial for adjusting the model during training.

- **Model Updates**: The model was updated after processing each batch, using the calculated losses to refine its understanding of the data.

- **Early Stopping**: To prevent overfitting, the training process included an "early stopping" mechanism. If the model's performance did not improve for several consecutive iterations (indicating that it had learned as much as it could from the data), the training process was halted early.

- **Model Saving**: After completing the training, the final NER model was saved to disk as `ner_model`. This model is then ready to be used for predicting entities in new data.

## Entity Extraction and Final Output

Once the model was trained, the script used it to extract entities from the `material` column in the `final_combined_output.csv` file. The steps involved in this process were:

1. **Preprocessing**: Before passing the material descriptions to the NER model, the text was standardized using the `preprocess_dimensions` function. This step ensured that all dimensions and relevant details were in a consistent format.

2. **Entity Extraction**: The trained NER model was then applied to the preprocessed material descriptions. The model identified and labeled various components, such as material names, grades, dimensions, and coatings, based on the patterns it learned during training.

3. **Saving the Output**: The extracted entities were added as new columns to the original DataFrame, preserving all rows. The final DataFrame was then saved to a new CSV file, `final_combined_output_with_entities.csv`, which contains both the original material descriptions and the newly extracted structured data.


## Logging
Logs: All significant actions, errors, and warnings are logged in the logs/ directory.
Log Files: Each run of the scripts generates a log file, named with the current timestamp.

# TODOs and Future Enhancements

This section outlines the areas that need improvement and further development to enhance the accuracy, consistency, and performance of the data processing and Named Entity Recognition (NER) model.

## 1. Consideration of Additional Columns

Currently, only the following columns are being considered:
- `article id`
- `MATERIAL_NAME`
- `weight`
- `quantity`
- `material`
- `MATERIAL_GRADE`
- `COATING_TYPE`
- `FINISH_TYPE`
- `DIMENSION`
- `ADDITIONAL_SPEC`

There is much more information available in the dataset that could be utilized. Expanding the number of columns considered could provide a more comprehensive understanding of the data and improve the model's performance.

## 2. Article ID Standardization

Some rows do not have an `article id`, and the format of the `article id` is inconsistent across the dataset. A standardized format for `article id` needs to be enforced to ensure consistency and improve data integrity.

## 3. Standardized Dictionary for `COATING_TYPE` and `FINISH_TYPE`

Currently, `COATING_TYPE` and `FINISH_TYPE` are being used with varying terms, such as "ungebeizt, nicht geglüht" or "gebeizt und geglüht". A standardized dictionary should be created to unify these terms across the dataset. This will not only improve data consistency but also enhance the NER model's ability to correctly identify and categorize these attributes.

## 4. Standardized Material Grade

The `MATERIAL_GRADE` column also requires standardization. For instance, the term "2nd" is used inconsistently. Establishing a standard set of terms for material grades will improve data quality and the accuracy of the NER model.

## 5. Improve NER Training

The current NER model is not 100% accurate, and there is significant room for improvement. Enhancing the training process, possibly by incorporating more training data, refining the model's architecture, or using advanced techniques, can greatly improve the model's accuracy.

## 6. Dimension Processing Errors

There are still some errors in dimension processing. For example, "DD11 geolied" is incorrectly processed as "DD11geolied". This issue needs to be addressed to ensure that dimensions and material names are correctly tokenized and recognized by the NER model.

## 7. Tokenization and Prediction Mismatches

There are mismatches between tokenization and prediction, leading to incorrect entity recognition. This issue should be investigated and resolved to ensure that the NER model correctly identifies and labels entities in the data.

## 8. Exploring GPT Embeddings for Improved Accuracy

One potential approach to improving accuracy is to use GPT embeddings to convert every word (split by space) in the material descriptions into embeddings. These embeddings can then be clustered using an unsupervised machine learning algorithm like K-means clustering. Once the clusters are correctly identified, GPT can be used to predict class names such as "MATERIAL_NAME", "COATING_TYPE", etc. This approach could potentially lead to a significant improvement in the model's accuracy.

