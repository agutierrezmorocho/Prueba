# main.py
import os
import shutil
import logging
import pandas as pd
import matplotlib.pyplot as plt
from natsort import natsorted
from typing import List, Dict, Any, Tuple

# --- Local Module Import ---
# Assuming the data processing functions are in a file named 'utils.py'
try:
    from utils import (
        extract_sample_info, 
        process_microorganisms, 
        process_amr_markers
    )
except ImportError:
    print("Error: Could not import 'utils.py'. Please ensure it is in the same directory.")
    exit(1)

# --- Configuration ---
LOG_FILE = 'processing_errors.log'
TABLES_DIR = os.path.join("Results", "Tables")
PLOTS_DIR = os.path.join("Results", "Plots")
RESULTS_DIR = "Results"

# Configure logging
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ----------------------------------------------------------------------------------
# --- ENVIRONMENT SETUP ---
# ----------------------------------------------------------------------------------

def setup_environment():
    """Ensures the Results directory structure exists."""
    try:
        if not os.path.exists(RESULTS_DIR):
            os.mkdir(RESULTS_DIR)
        
        if not os.path.exists(TABLES_DIR):
            os.mkdir(TABLES_DIR)
        
        if not os.path.exists(PLOTS_DIR):
            os.mkdir(PLOTS_DIR)
        
        logger.info("Result directories created/verified successfully.")
    except Exception as e:
        logger.error(f"Failed to set up environment directories: {e}")
        raise

# ----------------------------------------------------------------------------------
# --- PLOTTING FUNCTIONS ---
# ----------------------------------------------------------------------------------

def plot_counts(df: pd.DataFrame, column: str, title: str, filename: str, labels: List[str] = None, colors: List[str] = None):
    """Creates and saves a bar plot for value counts of a column."""
    try:
        count_data = df[column].value_counts()
        
        plt.figure(figsize=(7, 5))
        count_data.plot(
            kind='bar', 
            color=colors if colors else ['gray'],
            edgecolor='black',
            linewidth=2
        )
        
        plt.title(title, size='x-large', weight='bold')
        plt.ylabel('Quantity', weight='bold', rotation='vertical', size='large')
        
        if labels:
            plt.xticks(ticks=range(len(labels)), labels=labels, weight='bold', rotation='horizontal', size='large')
        else:
            plt.xticks(weight='bold', rotation='horizontal', size='large')

        filepath = f"{filename}.jpg"
        plt.savefig(filepath)
        plt.close()
        return filepath
    except Exception as e:
        logger.error(f"Error creating plot for {filename}: {e}")
        return None

def plot_relative_abundance(df: pd.DataFrame, total_reads_dict: Dict[str, int]) -> List[str]:
    """Calculates relative abundance for present organisms and plots per sample."""
    plot_paths = []
    
    df_present_mo = df[df['predictedPresent'] == True]
    sample_with_present_mo = df_present_mo['Sample'].unique()

    for sample_name in sample_with_present_mo:
        try:
            sample_df = df_present_mo[df_present_mo['Sample'] == sample_name][['Sample', 'Name', 'alignedReadCount']]
            total_reads = total_reads_dict.get(sample_name)
            
            if total_reads and total_reads > 0:
                sample_df['relativeAbundance(%)'] = (sample_df['alignedReadCount'] / total_reads) * 100
                sample_df = sample_df.sort_values('relativeAbundance(%)', ascending=False)

                plt.figure(figsize=(7, 11))
                plt.bar(sample_df['Name'], sample_df['relativeAbundance(%)'], 
                        color="indianred", edgecolor='black', linewidth=2)

                plt.title(f"Normalised Relative Abundance \n of Present Microorganisms \n {sample_name}", 
                          size='x-large', weight='bold')
                plt.ylabel('Normalised Relative Abundance (%)', weight='bold', size='large')
                plt.xticks(weight='bold', size='large', rotation=75)
                plt.tight_layout()

                filename = f"normalised_relativeAbundance_{sample_name}.jpg"
                plt.savefig(filename)
                plt.close()
                plot_paths.append(filename)
            else:
                logger.warning(f"Skipping relative abundance plot for {sample_name}: Total reads not found or zero.")
        except Exception as e:
            logger.error(f"Error plotting relative abundance for sample {sample_name}: {e}")
            continue
            
    return plot_paths

# ----------------------------------------------------------------------------------
# --- FILE MANAGEMENT ---
# ----------------------------------------------------------------------------------

def move_results(file_paths: List[str], target_dir: str):
    """Moves generated files to the target directory, handling existing files."""
    for path in file_paths:
        final_path = os.path.join(target_dir, os.path.basename(path))
        
        try:
            if os.path.exists(final_path):
                os.remove(final_path)
            
            if os.path.exists(path):
                shutil.move(path, final_path)
            else:
                logger.error(f"Source file not found for move operation: {path}")

        except Exception as e:
            logger.error(f"Error moving file {os.path.basename(path)} to {target_dir}: {e}")

# ----------------------------------------------------------------------------------
# --- MAIN EXECUTION ---
# ----------------------------------------------------------------------------------

def main():
    """Main execution function."""
    try:
        setup_environment()
        
        # 1. Extract Sample Info
        sample_names, common_prefix = extract_sample_info()
        if not sample_names:
            logger.warning("No sample directories found. Exiting.")
            return

        all_mo_tables: List[pd.DataFrame] = []
        all_amr_tables: List[pd.DataFrame] = []

        # 2. Process Data for All Samples
        for sample_i in sample_names:
            try:
                mo_table = process_microorganisms(sample_i, common_prefix)
                amr_table = process_amr_markers(sample_i, common_prefix)
                
                if mo_table is not None:
                    all_mo_tables.append(mo_table)
                if amr_table is not None:
                    all_amr_tables.append(amr_table)
            except Exception as e:
                logger.error(f"Critical error processing sample {sample_i}: {e}")
                continue # Skip this sample and continue with the next
                
        if not all_mo_tables and not all_amr_tables:
            logger.error("No data could be processed from any sample. Exiting.")
            return

        # 3. Concatenate and Export Tables
        final_mo_df = pd.concat(all_mo_tables, ignore_index=True)
        final_amr_df = pd.concat(all_amr_tables, ignore_index=True)

        final_mo_df.to_excel("Microorganisms_table.xlsx", sheet_name='Sheet_1', index=False)
        final_amr_df.to_excel("amrMarkers_table.xlsx", sheet_name='Sheet_1', index=False)
        table_paths = ["Microorganisms_table.xlsx", "amrMarkers_table.xlsx"]
        
        # 4. Generate Plots
        total_reads_dict = final_mo_df.groupby('Sample')['alignedReadCount'].sum().to_dict()

        plot_paths = []
        
        # Plot 1: Predicted Presence
        pp_path = plot_counts(
            final_mo_df, 'predictedPresent', 'Predicted Presence of Microorganisms', 
            'predictedPresent', labels=['Not present', 'Present'], colors=['red', 'green']
        )
        if pp_path: plot_paths.append(pp_path)
        
        # Plot 2: Microorganisms Class
        class_path = plot_counts(
            final_mo_df, 'class', 'Microorganisms Class', 
            'class', colors=['yellow', 'cyan', 'magenta'] # Note: You'll need to verify order matches categories
        )
        if class_path: plot_paths.append(class_path)
        
        # Plot 3: Normalised Relative Abundance per Sample
        plot_paths.extend(plot_relative_abundance(final_mo_df, total_reads_dict))

        # 5. Move Results
        move_results(table_paths, TABLES_DIR)
        move_results(plot_paths, PLOTS_DIR)

        logger.info("Processing complete. Check 'processing_errors.log' for details.")
        print(f"✅ Success! Results saved to '{RESULTS_DIR}'. Errors logged to '{LOG_FILE}'.")

    except Exception as e:
        logger.critical(f"A fatal error occurred during main execution: {e}")
        print(f"❌ A fatal error occurred. Check '{LOG_FILE}' for details.")

if __name__ == "__main__":
    main()
