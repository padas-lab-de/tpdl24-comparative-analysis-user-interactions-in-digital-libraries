# Comparative Analysis: User Interactions in Public and Private Digital Libraries Datasets

Source code for our paper :  
***Comparative Analysis: User Interactions in Public and Private Digital Libraries Datasets***


## Abstract

```
The scarcity of public datasets with detailed user interaction data in digital libraries underscores a significant research challenge. The complexity of effectively anonymizing such data without losing its utility further exacerbates this issue. This study conducts a comparative analysis of two datasets: EconBiz, a private dataset, and SUSS, a publicly available dataset, to investigate the differences in the granularity of user logs between them. The findings reveal that while EconBiz and SUSS share some similar patterns, EconBiz provides a more nuanced view of diverse user interactions compared to SUSS. These results emphasize the need for enhancing public datasets to maintain their value for research and real-world applications. Moreover, this paper briefly explores the potential of using few-shot prompting with large language models (LLMs) to simulate richer user interaction data while preserving user anonymity, thereby extending the utility of public datasets like SUSS. Addressing these issues is crucial for understanding the limitations of public datasets in reflecting real-world user behavior and proposing methods to mitigate these challenges, ultimately facilitating the development of more personalized and responsive digital library services.
```


## Repository Structure

```
project_root/
│
├── analysis/                   # Analysis modules
│   ├── data_processing.py      # Data processing functions
│   ├── session_analysis.py     # Session analysis functions
│   ├── session_generation.py   # Session generation functions
│   ├── suss_processing.py      # SUSS dataset processing functions
│   ├── visualization.py        # Data visualization functions
│   └── utils.py                # Utility functions used across the project
│
├── data/                       # Data directory (not tracked)
│   ├── econbiz/             
│   └── suss/ 
│
├── logs/                       # Logs directory (not tracked)
│   ├── econbiz/             
│   └── suss/ 
│
├── metrics/                    # Metrics directory (not tracked)
│   ├── econbiz/             
│   └── suss/ 
│
├── main.py                     # Main script to run analyses
└── README.md                   # This documentation file
```

## Installation

Instructions on how to install and set up your project. This might include steps to install Python, Poetry, and how to install dependencies using Poetry:

```bash
poetry install
```

## Data Availability and Download Instructions

### SUSS Dataset

The SUSS (Synthetic User Session Simulation) dataset is publicly available and can be used to complement the analysis alongside the synthetic sessions generated for the EconBiz data. This dataset has been designed to simulate user interaction patterns in digital libraries and can serve as a valuable resource for testing and validating user behavior models.

#### Downloading the SUSS Dataset

The SUSS dataset is hosted by GESIS and can be accessed through the following link: [SDN-10.7802-1380 on GESIS](https://search.gesis.org/research_data/SDN-10.7802-1380). 

#### Organizing the SUSS Dataset

Once downloaded, the SUSS dataset files should be organized within your project to facilitate easy access and processing. Here is how to properly place the files:

```
project_root/
├── data/                 # Data directory (not tracked)
│   └── suss/             # SUSS dataset
│       ├── action_mapping.csv
│       ├── amur_log_data.csv  
│       └── table_description.csv 
```

### EconBiz Data

The EconBiz dataset used in this project is private and, therefore, not shared within this repository due to confidentiality agreements. The dataset includes detailed user interaction data from the EconBiz digital library, which is crucial for our analysis but sensitive in nature.

### Synthetic Sessions Data

To facilitate research and allow for reproducibility of our results under similar conditions, we are sharing a set of synthetic session data. These synthetic sessions were generated using the few-shot Large Language Model (LLM) method described in our paper. This approach allows us to simulate user interaction data that closely mirrors real-world patterns observed in the EconBiz dataset while ensuring user privacy and data confidentiality.

#### Downloading Synthetic Data

The synthetic sessions are available in the `data/econbiz/synthetic_sessions/` directory of this repository. For users interested in generating additional synthetic data, we recommend referring to the methodology outlined in our paper. While we cannot provide direct access to the EconBiz dataset, this synthetic data offers a valuable alternative for experimentation and analysis.

Please note that while the synthetic data does not represent real user interactions, it has been crafted to closely resemble the characteristics and complexities of the interactions found in the EconBiz dataset, making it a useful resource for research and development purposes.


## Usage

### Processing the SUSS Dataset

To process the SUSS dataset from a CSV file and save the sessions to JSON files, use the `--process-suss` flag along with `--csv-file-path` and `--output-dir` to specify the input CSV file and the output directory for the JSON files, respectively.

```bash
poetry run python main.py --process-suss --csv-file-path <path_to_csv_file> --output-dir <path_to_output_directory>
```

This command parses the SUSS dataset CSV file, extracting session information and actions, and saves each session as a separate JSON file in the specified output directory. Ensure that the paths provided to the flags are correct and accessible.

#### Example

Assuming you have a CSV file named `amur_log_data.csv` in the `data/suss/` directory and you want to save the processed sessions into the `data/suss/sessions/` directory, you would run:

```bash
poetry run python main.py --process-suss --csv-file-path data/suss/amur_log_data.csv --output-dir data/suss/sessions/
```

This will process the SUSS dataset, creating individual JSON files for each session in the specified output directory.

### Processing JSON to CSV (ONLY for EconBiz data)

To convert a JSON file to a CSV file, use the `--json-to-csv` flag. This triggers the `process_large_json_to_csv_ndjson` function, which processes a specified JSON file and outputs a CSV file.

```bash
poetry run python main.py --json-to-csv
```

Ensure the `file_path` and `output_csv_path` variables in `main.py` are set to your specific JSON file and desired output CSV file location, respectively.



### Generating Boxplots

To generate boxplots for session analysis, use the `--generate-boxplots` flag. This function reads data from a specified CSV file and generates boxplots for various metrics, saving the output image to a specified path.

```bash
poetry run python main.py --generate-boxplots
```

Before running, adjust the `csv_file_path` and `output_image_path` variables in the `analysis/visualization.py` module or pass them as arguments to your functions.


### Parsing and Saving Session Data

To parse session data from a JSON file and save the processed sessions to JSON files, use the `--process-sessions` flag along with `--json-file-path` and `--output-dir` to specify the input file and output directory, respectively.

```bash
poetry run python main.py --process-sessions --json-file-path <path_to_json_file> --output-dir <path_to_output_directory>
```

This command parses the session data, applying any necessary transformations, and saves each session as a separate JSON file in the specified output directory.


### Parsing and Saving Session Data

To parse session data from JSON files and save the processed sessions to a CSV file, use the `--process-classification` flag followed by specifying the directory containing JSON files and the output CSV file path:

```bash
poetry run python main.py --process-classification --directory data/suss/sessions/ --csv-file-path logs/suss/sessions_processed.csv
```

### Generating Synthetic Sessions

To generate synthetic sessions based on the original session data and synthetic topics, use the `--generate-synthetic` flag. This process reads original session files, selects a random topic, and generates a synthetic session for each original session file.

```bash
poetry run python main.py --generate-synthetic
```

Ensure the `original_sessions_dir` and `synthetic_sessions_dir` variables in `main.py` are set to your specific directories for original session files and where you want to save synthetic sessions, respectively.

### Comparative Analysis

To perform a comparative analysis between the EconBiz and SUSS datasets, use the following flags. Each flag triggers a specific comparison function that analyzes different aspects of the datasets.

#### Comparing Basic Session Information

```bash
poetry run python main.py --compare-sessions
```

This command compares the basic session information, such as the number of sessions, between the two datasets.

#### Comparing Session Lengths

```bash
poetry run python main.py --compare-length
```

Use this flag to compare the session lengths between the EconBiz and SUSS datasets, including average, maximum, and minimum session lengths.

#### Comparing Actions Per Session

```bash
poetry run python main.py --compare-actions
```

This command triggers a comparison of the average, maximum, and minimum number of actions per session between the two datasets.

#### Comparing Unique Users

```bash
poetry run python main.py --compare-users
```

To compare the number of unique users between the EconBiz and SUSS datasets, use this flag.

#### Comparing Action Distribution

```bash
poetry run python main.py --compare-distribution
```

This flag allows for the comparison of action distributions between the datasets, visualizing the differences in user interactions.

### Loading Datasets

The `load_datasets` function is utilized internally to load and preprocess the datasets before performing any comparisons. This function ensures that all necessary data is prepared and available for analysis.


### Visualizing Data

To visualize the distribution of queries per user and the distribution of query lengths by the number of tokens, use the `--visualize` flag. This triggers the visualization functions that generate and save plots based on the processed session data.

```bash
poetry run python main.py --visualize
```

Before running this command, ensure that the data for visualization is prepared and accessible by the visualization functions. The visualization functions plot the distributions and save the plots to specified paths within the project directory. Adjust the paths and data inputs as necessary to fit your project's structure and data.

#### Example

To visualize data distributions for the SUSS and EconBiz datasets, assuming you have processed these datasets and have the necessary data arrays ready, you would run:

```bash
poetry run python main.py --visualize
```

This command will generate plots for the combined distribution of queries per user and the combined distribution of query lengths by the number of tokens, saving the plots to the `metrics/` directory. 


### Additional Notes

- Ensure that the paths provided to the flags are correct and accessible.
- You may need to adjust the flags and paths according to your specific project setup and requirements.
- The flags are designed to trigger specific functionalities within the project, allowing for modular and flexible analysis workflows.



