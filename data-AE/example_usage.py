#!/usr/bin/env python3
"""
Example script showing how to use the author profile summary program programmatically.
This script demonstrates how to call the functions directly instead of using the command line.
"""

import os
import json
from author_profile_summary import (
    load_author_profiles,
    process_authors,
    save_author_profiles
)


def load_author_profiles(input_file: str):
    """Load author profiles from a JSON file."""
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: Input file {input_file} not found")
        return None
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in {input_file}")
        return None


def example_batch_processing():
    """Example of processing authors in batches."""
    print("Example: Batch processing of authors")
    print("=" * 50)
    
    # Load author profiles
    input_file = "log/author_profile.json"
    authors_data = load_author_profiles(input_file)
    
    if not authors_data:
        print("Could not load author profiles. Make sure the input file exists.")
        return
    
    print(f"Loaded {len(authors_data)} authors")
    
    # Example 1: Process first 10 authors
    print("\nProcessing first 10 authors...")
    batch1 = process_authors(authors_data.copy(), 0, 10)
    
    # Save first batch
    save_author_profiles(batch1, "log/authors_0_9.json")
    
    # Example 2: Process authors 10-19
    print("\nProcessing authors 10-19...")
    batch2 = process_authors(authors_data.copy(), 10, 20)
    
    # Save second batch
    save_author_profiles(batch2, "log/authors_10_19.json")
    
    # Example 3: Process authors 20-29
    print("\nProcessing authors 20-29...")
    batch3 = process_authors(authors_data.copy(), 20, 30)
    
    # Save third batch
    save_author_profiles(batch3, "log/authors_20_29.json")
    
    print("\nBatch processing completed!")
    print("Output files:")
    print("- log/authors_0_9.json")
    print("- log/authors_10_19.json") 
    print("- log/authors_20_29.json")


def example_selective_processing():
    """Example of processing specific authors by index."""
    print("\nExample: Selective processing of specific authors")
    print("=" * 50)
    
    # Load author profiles
    input_file = "log/author_profile.json"
    authors_data = load_author_profiles(input_file)
    
    if not authors_data:
        print("Could not load author profiles. Make sure the input file exists.")
        return
    
    # Process specific authors (e.g., authors at indices 50, 100, 150)
    specific_indices = [50, 100, 150]
    
    for idx in specific_indices:
        if idx < len(authors_data):
            print(f"\nProcessing author at index {idx}: {authors_data[idx]['name']}")
            
            # Process just this author
            batch = process_authors(authors_data.copy(), idx, idx + 1)
            
            # Save to individual file
            output_file = f"log/author_{idx}_{authors_data[idx]['name'].replace(' ', '_')}.json"
            save_author_profiles(batch, output_file)
            print(f"Saved to {output_file}")
        else:
            print(f"Index {idx} is out of range (max: {len(authors_data) - 1})")


def example_resume_processing():
    """Example of resuming processing from where you left off."""
    print("\nExample: Resuming processing from a checkpoint")
    print("=" * 50)
    
    # Load author profiles
    input_file = "log/author_profile.json"
    authors_data = load_author_profiles(input_file)
    
    if not authors_data:
        print("Could not load author profiles. Make sure the input file exists.")
        return
    
    # Check which authors already have summaries
    authors_with_summaries = []
    authors_without_summaries = []
    
    for i, author in enumerate(authors_data):
        if author.get("summary") and author["summary"].strip():
            authors_with_summaries.append(i)
        else:
            authors_without_summaries.append(i)
    
    print(f"Authors with summaries: {len(authors_with_summaries)}")
    print(f"Authors without summaries: {len(authors_without_summaries)}")
    
    if authors_without_summaries:
        print(f"\nProcessing authors without summaries...")
        start_idx = min(authors_without_summaries)
        end_idx = max(authors_without_summaries) + 1
        
        # Process only authors without summaries
        updated_authors = process_authors(authors_data.copy(), start_idx, end_idx, "log/author_profile_completed.json")
        
        # Save updated profiles
        save_author_profiles(updated_authors, "log/author_profile_completed.json")
        print("Resume processing completed!")
    else:
        print("All authors already have summaries!")


def main():
    """Run all examples."""
    print("Author Profile Summary - Example Usage")
    print("=" * 50)
    
    # Check if OpenAI API key is set
    if "OPENAI_API_KEY" not in os.environ:
        print("Warning: OPENAI_API_KEY environment variable not set")
        print("The examples will show the structure but won't make actual API calls")
        print("Set your API key to test the full functionality")
        print()
    
    examples = [
        example_batch_processing,
        example_selective_processing,
        example_resume_processing
    ]
    
    for example in examples:
        try:
            example()
            print("\n" + "="*70 + "\n")
        except Exception as e:
            print(f"Example failed: {e}")
            print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    main()
