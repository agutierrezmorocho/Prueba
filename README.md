Markdown

# Microbial JSON Data Aggregator and Analyzer 🦠🔬

## 🌟 Overview

This Python project is a robust, modular command-line tool designed for **bioinformatics data processing**. Its primary function is to read, aggregate, transform, and visualize data extracted from multiple JSON reports, specifically focusing on microbial sequencing results.

The tool provides essential metrics on **microorganism presence** and **Antimicrobial Resistance (AMR) markers** across a batch of samples, generating professional Excel tables and analytical plots for immediate use.

### Key Features
* **Automated Data Extraction:** Recursively scans the current directory to identify and process all sample reports.
* **Data Consolidation:** Aggregates data from multiple samples into two clean, comprehensive Excel files (`.xlsx`).
* **Key Visualizations:** Generates plots for predicted presence, taxonomic class distribution, and normalized relative abundance per sample.
* **Professional Structure:** Code is split into `main.py` (orchestration/output) and `utils.py` (core data logic) for maintainability and testing.
* **Robust Logging:** Implements structured error logging to `processing_errors.log` to retain details of any issues (e.g., missing files, corrupted JSON) without crashing the main program.

## 📦 Project Structure

The repository follows a clean, standardized Python project layout:

/microbial-data-analyzer
├── main.py             # Main execution flow, plotting, and file movement
├── utils.py            # Core data loading and JSON processing logic
├── requirements.txt    # List of necessary Python libraries
├── README.md           # This documentation file
├── .gitignore          # Ignores generated files (e.g., Results/, logs)
└── /Example_Sample_01  # Directory containing input JSON reports
└── sample1.1.report.json


## 🚀 Installation

### 1. Prerequisites
You must have **Python 3.7+** and `git` installed on your system.

### 2. Clone the Repository
Start by cloning the project files from GitHub:

```bash
git clone [https://github.com/YourUsername/microbial-data-analyzer.git](https://github.com/YourUsername/microbial-data-analyzer.git)
cd microbial-data-analyzer
3. Install Dependencies
Install all required libraries using pip and the provided requirements.txt file:

Bash

pip install -r requirements.txt
⚙️ Usage
1. Prepare Your Data
Place your sample directories in the root folder of this project (/microbial-data-analyzer).

The script identifies samples based on a common prefix and a unique identifier. Ensure your folder and JSON file naming follows this pattern:

Sample Folder: [Common_Prefix][Sample_ID] (e.g., Run1_S1, Run1_S2)

JSON Report: sample[Sample_ID].[Sample_ID].report.json (e.g., sample1.1.report.json)

📊 Output and Results
The script automatically creates a Results/ directory to organize all generated outputs.

1. Tables (Results/Tables/)
The data is consolidated into two Excel workbooks:

File Name	Content
Microorganisms_table.xlsx	Aggregated data for microbial taxa, including Read Counts, ANI, RPKM, and Predicted Presence.
amrMarkers_table.xlsx	Aggregated data for Antimicrobial Resistance (AMR) genes, including Coverage, Depth, and Associated Microorganisms.

Exportar a Hojas de cálculo
2. Plots (Results/Plots/)
Visual summaries of the analysis:

predictedPresent.jpg: Bar chart showing the overall frequency of predicted present (True) vs. not present (False) microorganisms across all samples.

class.jpg: Bar chart summarizing the total count of microorganisms by taxonomic class (e.g., Viral, Bacterial, Fungal).

normalised_relativeAbundance_*.jpg: A separate bar chart for each analyzed sample, illustrating the relative abundance (%) of microorganisms predicted to be present.

🛠️ Code Architecture
The separation of the code is key to its maintainability and professional organization:

Module	Responsibility	Key Functions
main.py	Orchestration and Output	setup_environment(), plot_counts(), plot_relative_abundance(), move_results(), and the main execution block (main()).
utils.py	Core Data Transformation	extract_sample_info(), load_json_report() (handles file I/O errors), process_microorganisms(), process_amr_markers() (converts JSON arrays to DataFrames).

Exportar a Hojas de cálculo
🚨 Error and Debugging
All error messages (e.g., sample folders missing, JSON files corrupted, data extraction failures) are redirected to:

processing_errors.log
If the program completes successfully, you will see a confirmation message. If a fatal error occurs, check this log file first for detailed traceback information.
