# **Supplier Data Standardization for Metal Trading**

This project is designed to standardize and process supplier data in the metal trading industry. It leverages Python libraries such as `pandas` and `spaCy` to preprocess data, extract entities using Natural Language Processing (NLP), and produce a standardized output.
## **Setup**

1. **Clone the repository**:
   ```bash
   git clone https://github.com/venkateshhs/supplier_data_standardization_for_metal_trading.git
   cd supplier_data_standardization_for_metal_trading
   
2. **Create a virtual environment:**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows, use `venv\\Scripts\\activate`

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
   python main.py
```

This script:
Reads the input data from the data directory.
Processes the data by merging and cleaning it.
Saves the processed data in the data/final_combined_output.csv file.

2. **Step 2: Run the NER Model**
After processing the data with the main script, the NER (Named Entity Recognition) model is applied to extract specific entities from the material column.
```bash
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


## Detailed Explanation
1. **Data Processing (main.py)**
This script handles:

Reading Input Files: From the data directory.
Data Cleaning: Standardizing columns, merging different sheets, and ensuring that data is in a consistent format.
Saving Intermediate Output: The processed data is saved as final_combined_output.csv in the data directory.
NER Model (ner_model.py)
This script is responsible for:

2. **Applying NLP Techniques**: 
Using spaCy's NER model to identify and extract specific entities from the material column.
Updating the Original Data: Adding the extracted entities back into the DataFrame.
Saving Final Output: The final data, with all entities extracted and columns standardized, is saved as final_combined_output_with_entities.csv.
3. 
## Logging
Logs: All significant actions, errors, and warnings are logged in the logs/ directory.
Log Files: Each run of the scripts generates a log file, named with the current timestamp.
