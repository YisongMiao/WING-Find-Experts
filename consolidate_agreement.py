#!/usr/bin/env python3
"""
Agreement calculation script for expert finding results.
This script calculates the overlap between the top 10 names from different systems
across multiple documents and generates a CSV with pairwise agreement scores.

Systems: gpt, gemini, summarize, aggregate
Documents: 0, 1, 2 (3 documents total)
Pairs: 6 total (gpt-gem, gpt-sum, gpt-agg, gem-sum, gem-agg, sum-agg)
"""

import pandas as pd
import os
from pathlib import Path
from itertools import combinations


def read_top_names(file_path, top_n=10):
    """
    Read the top N names from a CSV file.
    
    Args:
        file_path (str): Path to the CSV file
        top_n (int): Number of top names to extract
        
    Returns:
        list: List of top N names
    """
    try:
        # First try to read with standard pandas CSV reader
        # But only for well-formed CSV files (like aggregate and summarize)
        try:
            df = pd.read_csv(file_path, skipinitialspace=True, on_bad_lines='skip')
            df.columns = df.columns.str.strip()
            
            if 'name' in df.columns and len(df) > 0:
                # Check if we got reasonable data
                first_name = str(df.iloc[0]['name']).strip()
                # Check if it looks like a person's name (contains capital letters and spaces, not just lowercase words)
                # Also check that it's not a long descriptive text
                looks_like_name = (first_name and 
                                 len(first_name) < 50 and  # Shorter length for names
                                 ',' not in first_name and
                                 any(c.isupper() for c in first_name) and  # Has capital letters
                                 ' ' in first_name and  # Has spaces (first and last name)
                                 not first_name.islower() and  # Not all lowercase
                                 not any(word in first_name.lower() for word in ['expert', 'researcher', 'specialist', 'leading', 'known', 'prominent']))  # Not descriptive text
                
                if looks_like_name:
                    top_names = df.head(top_n)['name'].tolist()
                    return [str(name).strip() for name in top_names if pd.notna(name)]
        except:
            pass
        
        # If standard CSV reading fails, try regex-based parsing
        import re
        
        names = []
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Use simple regex to extract names from malformed CSV
        # Pattern: number, name, (rest of line)
        pattern = r'(\d+),\s*([^,]+),'
        matches = re.findall(pattern, content)
        
        for num, name in matches[:top_n]:
            name = name.strip().strip('"')
            if name and len(name) < 100:  # Reasonable name length
                names.append(name)
        
        return names[:top_n]
        
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return []


def calculate_overlap(list1, list2):
    """
    Calculate the overlap between two lists of names.
    
    Args:
        list1 (list): First list of names
        list2 (list): Second list of names
        
    Returns:
        int: Number of overlapping names
    """
    set1 = set(list1)
    set2 = set(list2)
    return len(set1.intersection(set2))


def calculate_agreement_for_doc(doc_id, systems=['gpt', 'gemini', 'summarize', 'aggregate']):
    """
    Calculate pairwise agreements for a specific document.
    
    Args:
        doc_id (str): Document ID (0, 1, or 2)
        systems (list): List of system names
        
    Returns:
        dict: Dictionary with pairwise agreement scores
    """
    log_dir = Path("log")
    
    # Read top 10 names from each system for this document
    system_names = {}
    for system in systems:
        file_path = log_dir / system / f"{doc_id}.csv"
        if file_path.exists():
            system_names[system] = read_top_names(file_path)
        else:
            print(f"Warning: {file_path} not found")
            system_names[system] = []
    
    # Calculate pairwise agreements
    agreements = {}
    system_pairs = list(combinations(systems, 2))
    
    for sys1, sys2 in system_pairs:
        # Create abbreviated pair names to match expected format
        sys1_short = sys1[:3] if sys1 != 'gemini' else 'gem'
        sys2_short = sys2[:3] if sys2 != 'gemini' else 'gem'
        pair_name = f"{sys1_short}-{sys2_short}"
        overlap = calculate_overlap(system_names[sys1], system_names[sys2])
        agreements[pair_name] = overlap
    
    return agreements


def main():
    """
    Main function to calculate agreements across all documents and systems.
    """
    print("Expert Finding Agreement Calculation")
    print("=" * 50)
    
    systems = ['gpt', 'gemini', 'summarize', 'aggregate']
    documents = ['0', '1', '2', '3']  # 4 documents
    
    # Create list to store results
    results = []
    
    for doc_id in documents:
        print(f"\nProcessing document {doc_id}...")
        
        # Calculate agreements for this document
        agreements = calculate_agreement_for_doc(doc_id, systems)
        
        # Create result row
        result_row = {'docID': doc_id}
        result_row.update(agreements)
        results.append(result_row)
        
        # Print agreements for this document
        for pair, overlap in agreements.items():
            print(f"  {pair}: {overlap}/10 overlap")
    
    # Create DataFrame and save to CSV
    df = pd.DataFrame(results)
    
    # Reorder columns to match the requested format
    column_order = ['docID', 'gpt-gem', 'gpt-sum', 'gpt-agg', 'gem-sum', 'gem-agg', 'sum-agg']
    df = df[column_order]
    
    # Add average row
    avg_row = {'docID': 'average'}
    for col in column_order[1:]:  # Skip docID column
        avg_value = df[col].mean()
        avg_row[col] = round(avg_value, 2)
    
    # Add the average row to the DataFrame
    df = pd.concat([df, pd.DataFrame([avg_row])], ignore_index=True)
    
    # Save to CSV
    output_file = "agreement_report.csv"
    df.to_csv(output_file, index=False)
    
    print(f"\n" + "=" * 50)
    print(f"Agreement report saved to: {output_file}")
    print("\nSummary:")
    print(df.to_string(index=False))
    
    # Calculate average agreements across all documents
    print(f"\nAverage agreements across all documents:")
    for col in column_order[1:]:  # Skip docID column
        avg_agreement = df[col].mean()
        print(f"  {col}: {avg_agreement:.2f}/10")


if __name__ == "__main__":
    main()
