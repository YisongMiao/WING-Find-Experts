#!/usr/bin/env python3
"""
Evaluation script for expert finding system.
Calculates MRR@1, MRR@3, MRR@5, and MRR@10 for three modes:
- aggregate: CSV files with ranked lists
- summarize: CSV files with ranked lists  
- GPT: JSON files with candidate rankings
"""

import json
import csv
import os
from typing import Dict, List, Tuple
import pandas as pd

def load_groundtruth(groundtruth_path: str) -> Dict[str, str]:
    """Load groundtruth data and return mapping of query_id to AE name."""
    with open(groundtruth_path, 'r') as f:
        data = json.load(f)
    
    groundtruth = {}
    for query_id, info in data.items():
        groundtruth[query_id] = info['AE']
    
    return groundtruth

def calculate_mrr(ranked_list: List[str], groundtruth_name: str, k: int = None) -> float:
    """
    Calculate MRR@k for a ranked list.
    
    Args:
        ranked_list: List of author names in ranked order
        groundtruth_name: The correct author name
        k: Cutoff for MRR calculation (None for full list)
    
    Returns:
        MRR score (0.0 if not found in top-k)
    """
    if k is not None:
        ranked_list = ranked_list[:k]
    
    for i, author_name in enumerate(ranked_list):
        if author_name == groundtruth_name:
            return 1.0 / (i + 1)
    
    return 0.0

def load_csv_rankings(csv_path: str) -> List[str]:
    """Load author names from CSV file in ranked order."""
    df = pd.read_csv(csv_path)
    return df['Author Name'].tolist()

def load_json_rankings(json_path: str) -> List[str]:
    """Load author names from JSON file in ranked order."""
    with open(json_path, 'r') as f:
        data = json.load(f)
    
    # Extract names in order (candidate1, candidate2, ..., candidate10)
    ranked_list = []
    for i in range(1, 11):  # candidate1 to candidate10
        candidate_key = f"candidate{i}"
        if candidate_key in data:
            ranked_list.append(data[candidate_key]['name'])
    
    return ranked_list

def evaluate_mode(mode: str, groundtruth: Dict[str, str], num_queries: int = 24) -> Dict[str, float]:
    """
    Evaluate a specific mode (aggregate, summarize, or GPT).
    
    Args:
        mode: Mode name ('aggregate', 'summarize', or 'GPT')
        groundtruth: Groundtruth mapping
        num_queries: Number of queries to evaluate (0 to num_queries-1)
    
    Returns:
        Dictionary with MRR@1, MRR@3, MRR@5, MRR@10 scores
    """
    mrr_scores = {1: [], 3: [], 5: [], 10: []}
    
    for query_id in range(num_queries):
        query_str = str(query_id)
        
        if query_str not in groundtruth:
            print(f"Warning: No groundtruth for query {query_id}")
            continue
        
        groundtruth_name = groundtruth[query_str]
        
        try:
            if mode == 'GPT':
                json_path = f"results/{mode}/experts_query_{query_id}.json"
                ranked_list = load_json_rankings(json_path)
            else:
                csv_path = f"results/{mode}/fitness_scores_query_{query_id}.csv"
                ranked_list = load_csv_rankings(csv_path)
            
            # Calculate MRR for different cutoffs
            for k in [1, 3, 5, 10]:
                mrr = calculate_mrr(ranked_list, groundtruth_name, k)
                mrr_scores[k].append(mrr)
                
        except FileNotFoundError as e:
            print(f"Warning: {e}")
            # Add zeros for missing files
            for k in [1, 3, 5, 10]:
                mrr_scores[k].append(0.0)
        except Exception as e:
            print(f"Error processing query {query_id} for mode {mode}: {e}")
            # Add zeros for errors
            for k in [1, 3, 5, 10]:
                mrr_scores[k].append(0.0)
    
    # Calculate average MRR scores
    results = {}
    for k in [1, 3, 5, 10]:
        if mrr_scores[k]:
            results[f'MRR@{k}'] = sum(mrr_scores[k]) / len(mrr_scores[k])
        else:
            results[f'MRR@{k}'] = 0.0
    
    return results

def save_results(mode: str, results: Dict[str, float]):
    """Save MRR results to the respective results folder."""
    results_dir = f"results/{mode}"
    os.makedirs(results_dir, exist_ok=True)
    
    # Save as JSON
    json_path = f"{results_dir}/mrr_evaluation.json"
    with open(json_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    # Save as CSV
    csv_path = f"{results_dir}/mrr_evaluation.csv"
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Metric', 'Score'])
        for metric, score in results.items():
            writer.writerow([metric, f"{score:.4f}"])
    
    print(f"Results saved to {json_path} and {csv_path}")

def main():
    """Main evaluation function."""
    print("Starting expert finding system evaluation...")
    
    # Load groundtruth
    groundtruth_path = "data-query/groundtruth.json"
    groundtruth = load_groundtruth(groundtruth_path)
    print(f"Loaded groundtruth for {len(groundtruth)} queries")
    
    # Evaluate all three modes
    modes = ['aggregate', 'summarize', 'GPT']
    all_results = {}
    
    for mode in modes:
        print(f"\nEvaluating {mode} mode...")
        results = evaluate_mode(mode, groundtruth)
        all_results[mode] = results
        
        # Print results
        print(f"{mode.upper()} Results:")
        for metric, score in results.items():
            print(f"  {metric}: {score:.4f}")
        
        # Save results
        save_results(mode, results)
    
    # Print summary
    print("\n" + "="*50)
    print("EVALUATION SUMMARY")
    print("="*50)
    
    for mode in modes:
        print(f"\n{mode.upper()}:")
        for metric in ['MRR@1', 'MRR@3', 'MRR@5', 'MRR@10']:
            score = all_results[mode][metric]
            print(f"  {metric}: {score:.4f}")
    
    print("\nEvaluation completed!")

if __name__ == "__main__":
    main()
