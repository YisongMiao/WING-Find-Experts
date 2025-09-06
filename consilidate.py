#!/usr/bin/env python3
"""
Consolidation script for organizing and consolidating expert finding results.
This script:
1. Creates subfolders for aggregate and summarize modes
2. Consolidates results in the format: index, name, rationale
3. Processes all queries (0-4)
"""

import os
import json
import csv
import shutil
from pathlib import Path


def create_subfolders():
    """
    Create subfolders for aggregate and summarize modes under the log directory.
    """
    log_dir = Path("log")
    
    # Create aggregate and summarize subfolders
    aggregate_dir = log_dir / "aggregate"
    summarize_dir = log_dir / "summarize"
    
    aggregate_dir.mkdir(exist_ok=True)
    summarize_dir.mkdir(exist_ok=True)
    
    print(f"✓ Created subfolders:")
    print(f"  - {aggregate_dir}")
    print(f"  - {summarize_dir}")
    
    return aggregate_dir, summarize_dir


def consolidate_results(mode="aggregate", queries=range(5)):
    """
    Consolidate results for a specific mode and range of queries.
    
    Args:
        mode (str): Either "aggregate" or "summarize"
        queries (range): Range of query indices to process
    """
    log_dir = Path("log")
    mode_dir = log_dir / mode
    
    print(f"\nProcessing {mode} mode...")
    print("=" * 50)
    
    for query_idx in queries:
        print(f"Processing query {query_idx}...")
        
        # Input files
        output_file = log_dir / f"output_{mode}_query_{query_idx}.txt"
        fitness_file = log_dir / f"fitness_scores_{mode}_query_{query_idx}.csv"
        
        # Output file
        consolidated_file = mode_dir / f"{query_idx}.csv"
        
        if not output_file.exists():
            print(f"  ⚠️  Warning: {output_file} not found, skipping query {query_idx}")
            continue
        
        # Read the output file
        results = []
        try:
            with open(output_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        result = json.loads(line)
                        results.append(result)
        except Exception as e:
            print(f"  ❌ Error reading {output_file}: {e}")
            continue
        
        # Read fitness scores if available
        fitness_scores = {}
        if fitness_file.exists():
            try:
                with open(fitness_file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        author_name = row['Author Name']
                        fitness_score = float(row['Fitness Score'])
                        fitness_scores[author_name] = fitness_score
            except Exception as e:
                print(f"  ⚠️  Warning: Could not read fitness scores from {fitness_file}: {e}")
        
        # Write consolidated CSV
        try:
            with open(consolidated_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f, delimiter=',', quoting=csv.QUOTE_ALL)
                writer.writerow(['index', 'name', 'fitness_score', 'rationale'])
                
                for result in results:
                    # Extract the explanation/rationale
                    rationale = result.get('explanation', '')
                    
                    # Clean up the rationale (remove all line breaks and excessive whitespace)
                    # Remove all types of line breaks and whitespace characters
                    rationale = rationale.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
                    rationale = rationale.replace('\f', ' ').replace('\v', ' ')  # Form feed and vertical tab
                    rationale = ' '.join(rationale.split())  # Remove multiple spaces and normalize whitespace
                    
                    # Ensure rationale is a string and handle any None values
                    if rationale is None:
                        rationale = ''
                    rationale = str(rationale).strip()
                    
                    # Get fitness score
                    author_name = result.get('name', '')
                    fitness_score = fitness_scores.get(author_name, result.get('fitness', ''))
                    
                    # Format fitness score to 2 decimal places
                    if fitness_score != '':
                        try:
                            fitness_score = f"{float(fitness_score):.2f}"
                        except (ValueError, TypeError):
                            fitness_score = ''
                    
                    writer.writerow([
                        result.get('rank', ''),
                        author_name,
                        fitness_score,
                        rationale
                    ])
            
            print(f"  ✓ Consolidated {len(results)} results to {consolidated_file}")
            
        except Exception as e:
            print(f"  ❌ Error writing {consolidated_file}: {e}")


def consolidate_all_results():
    """
    Consolidate results for all modes and queries.
    """
    print("Starting consolidation process...")
    print("=" * 60)
    
    # Create subfolders
    aggregate_dir, summarize_dir = create_subfolders()
    
    # Process all queries (0-4)
    queries = range(4)
    
    # Consolidate aggregate mode
    consolidate_results("aggregate", queries)
    
    # Consolidate summarize mode
    consolidate_results("summarize", queries)
    
    print("\n" + "=" * 60)
    print("🎉 Consolidation completed!")
    print("\nGenerated files:")
    
    # List generated files
    for mode in ["aggregate", "summarize"]:
        mode_dir = Path("log") / mode
        print(f"\n{mode.upper()} mode:")
        for query_idx in queries:
            csv_file = mode_dir / f"{query_idx}.csv"
            if csv_file.exists():
                print(f"  - {csv_file}")
            else:
                print(f"  - {csv_file} (not found)")


def move_existing_files():
    """
    Note: Fitness scores are now incorporated directly into consolidated files.
    This function is kept for potential future use but doesn't move files.
    """
    log_dir = Path("log")
    
    print("Fitness scores will be incorporated directly into consolidated files...")
    
    # Create subfolders if they don't exist
    for mode in ["aggregate", "summarize"]:
        mode_dir = log_dir / mode
        mode_dir.mkdir(exist_ok=True)


def main():
    """
    Main function to run the consolidation process.
    """
    print("Expert Finding Results Consolidation")
    print("=" * 60)
    
    # Move existing files first
    move_existing_files()
    
    # Consolidate all results
    consolidate_all_results()
    
    print("\n" + "=" * 60)
    print("Summary:")
    print("- Created aggregate/ and summarize/ subfolders")
    print("- Consolidated explanation results for queries 0-4")
    print("- Incorporated fitness scores directly into consolidated files")
    print("- All files follow the format: index, name, fitness_score, rationale")


if __name__ == "__main__":
    main()
