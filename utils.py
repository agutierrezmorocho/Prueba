# utils.py
import os
import json
import pandas as pd
import logging
from natsort import natsorted
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

# ----------------------------------------------------------------------------------
# --- DATA EXTRACTION UTILITIES ---
# ----------------------------------------------------------------------------------

def extract_sample_info() -> Tuple[List[str], str]:
    """Identifies sample directories and the common prefix."""
    files = os.listdir(".")
    results_file = "Results"
    
    # Filter out the 'Results' folder and non-directories
    file_names = [
        f for f in files
        if os.path.isdir(f) and not f.startswith(results_file)
    ]

    file_names_ord = natsorted(file_names)
    common_prefix = os.path.commonprefix(file_names_ord)
    
    sample_names = []
    for file in file_names_ord:
        # Extract the variable part of the name
        sample_names.append(file[len(common_prefix):])
        
    return sample_names, common_prefix

def load_json_report(sample_i: str, common_prefix: str) -> Optional[Dict[str, Any]]:
    """Loads the JSON report for a given sample."""
    sample_folder = f"{common_prefix}{sample_i}"
    # The original report name structure was "sample{i}.{i}.report.json"
    report_name = f"sample{sample_i}.{sample_i}.report.json"
    report_path = os.path.join(sample_folder, report_name)
    
    try:
        with open(report_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error(f"FileNotFoundError: Report not found for sample {sample_i} at {report_path}")
        return None
    except json.JSONDecodeError as e:
        logger.error(f"JSONDecodeError: Failed to decode report for sample {sample_i}. Error: {e}")
        return None
    except Exception as e:
        logger.error(f"An unexpected error occurred while reading report for sample {sample_i}: {e}")
        return None

# ----------------------------------------------------------------------------------
# --- PROCESSING FUNCTIONS ---
# ----------------------------------------------------------------------------------

def process_microorganisms(sample_i: str, common_prefix: str) -> Optional[pd.DataFrame]:
    """Extracts, transforms, and returns the Microorganisms DataFrame."""
    report = load_json_report(sample_i, common_prefix)
    if report is None:
        return None
        
    try:
        trmo = report.get('targetReport', {}).get('microorganisms', [])
        if not trmo:
            logger.warning(f"No microorganism data found for sample {sample_i}.")
            return None

        data_rows = []
        for item in trmo:
            ani = item.get('ani', 0)
            rpkm = item.get('rpkm', 0)
            aligned_count = item.get('alignedReadCount', 0)
            predicted_present = item.get('explifyInterpretation', {}).get('predictedPresent', False)
            
            data_rows.append({
                'Sample': f"sample{sample_i}",
                'Name': item.get('name'),
                'alignedReadCount': aligned_count,
                'ani': round(ani, 2),
                'rpkm': round(rpkm, 2),
                'class': item.get('class'),
                'phenotypicGroup': item.get('phenotypicGroup'),
                'predictedPresent': predicted_present,
                # Replicated original logic: predictedPresent OR alignedReadCount > 5
                'Presence': predicted_present or (aligned_count > 5) 
            })
            
        return pd.DataFrame(data_rows)
        
    except Exception as e:
        logger.error(f"Error processing microorganism data for sample {sample_i}: {e}")
        return None

def process_amr_markers(sample_i: str, common_prefix: str) -> Optional[pd.DataFrame]:
    """Extracts, transforms, and returns the AMR Markers DataFrame."""
    report = load_json_report(sample_i, common_prefix)
    if report is None:
        return None
        
    try:
        tramr = report.get('targetReport', {}).get('amrMarkers', [])
        if not tramr:
            logger.warning(f"No AMR markers data found for sample {sample_i}.")
            return None

        data_rows = []
        for item in tramr:
            coverage = item.get('coverage', 0)
            
            # The original code takes the first element of 'all' list
            associated_mo = item.get('associatedMicroorganisms', {}).get('all', [None])[0]

            data_rows.append({
                'SampleID': f"sample{sample_i}",
                'GeneName': item.get('name'),
                'Class': item.get('class'),
                'geneFamily': item.get('geneFamily'),
                'Coverage': round(coverage, 2),
                'medianDepth': item.get('medianDepth'),
                'associatedMicroorganisms': associated_mo,
                'predictedPresent': item.get('explifyInterpretation', {}).get('predictedPresent', False)
            })
            
        return pd.DataFrame(data_rows)
        
    except Exception as e:
        logger.error(f"Error processing AMR marker data for sample {sample_i}: {e}")
        return None
