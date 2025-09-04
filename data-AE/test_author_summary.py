#!/usr/bin/env python3
"""
Test script for author profile summary functionality.
This script tests the core functions without making actual API calls.
"""

import json
import tempfile
import os
from author_profile_summary import (
    create_author_summary_prompt,
    generate_author_summary,
    process_authors,
    save_author_profiles
)


def test_prompt_creation():
    """Test the prompt creation function."""
    print("Testing prompt creation...")
    
    test_publications = [
        {
            "title": "Test Paper 1",
            "abstract": "This is a test abstract for paper 1."
        },
        {
            "title": "Test Paper 2", 
            "abstract": "This is a test abstract for paper 2."
        }
    ]
    
    prompt = create_author_summary_prompt("Test Author", test_publications)
    print("Generated prompt:")
    print(prompt)
    print("\n" + "="*50 + "\n")
    
    return True


def test_with_mock_gpt():
    """Test the summary generation with a mock GPT response."""
    print("Testing summary generation with mock GPT...")
    
    # Mock the call_gpt function
    def mock_call_gpt(system_prompt, user_prompt):
        return "This is a mock summary for Test Author based on their publications."
    
    # Temporarily replace the call_gpt function
    import author_profile_summary
    original_call_gpt = author_profile_summary.call_gpt
    author_profile_summary.call_gpt = mock_call_gpt
    
    try:
        test_publications = [
            {
                "title": "Test Paper 1",
                "abstract": "This is a test abstract for paper 1."
            },
            {
                "title": "Test Paper 2",
                "abstract": "This is a test abstract for paper 2."
            }
        ]
        
        summary = generate_author_summary("Test Author", test_publications)
        print(f"Generated summary: {summary}")
        print("\n" + "="*50 + "\n")
        
    finally:
        # Restore original function
        author_profile_summary.call_gpt = original_call_gpt
    
    return True


def test_processing_functions():
    """Test the processing and saving functions."""
    print("Testing processing and saving functions...")
    
    # Create test data
    test_authors = [
        {
            "name": "Author 1",
            "publication_urls": ["url1", "url2"],
            "list_of_pubs": [
                {"title": "Paper 1", "abstract": "Abstract 1"},
                {"title": "Paper 2", "abstract": "Abstract 2"}
            ],
            "summary": ""
        },
        {
            "name": "Author 2",
            "publication_urls": ["url3"],
            "list_of_pubs": [
                {"title": "Paper 3", "abstract": "Abstract 3"}
            ],
            "summary": "Already has summary"
        }
    ]
    
    # Mock the call_gpt function for testing
    def mock_call_gpt(system_prompt, user_prompt):
        return f"Mock summary for {user_prompt.split('Author: ')[1].split('\n')[0]}"
    
    import author_profile_summary
    original_call_gpt = author_profile_summary.call_gpt
    author_profile_summary.call_gpt = mock_call_gpt
    
    try:
        # Test processing
        processed_authors = process_authors(test_authors, 0, 2, "temp_test_output.json")
        
        # Test saving
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_file = f.name
        
        try:
            save_author_profiles(processed_authors, temp_file)
            
            # Verify the file was created and contains data
            with open(temp_file, 'r') as f:
                saved_data = json.load(f)
            
            print(f"Saved {len(saved_data)} authors to temporary file")
            print(f"Author 1 summary: {saved_data[0]['summary']}")
            print(f"Author 2 summary: {saved_data[1]['summary']}")
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_file):
                os.unlink(temp_file)
        
        print("\n" + "="*50 + "\n")
        
    finally:
        # Restore original function
        author_profile_summary.call_gpt = original_call_gpt
    
    return True


def main():
    """Run all tests."""
    print("Running tests for author profile summary functionality...\n")
    
    tests = [
        test_prompt_creation,
        test_with_mock_gpt,
        test_processing_functions
    ]
    
    for test in tests:
        try:
            test()
        except Exception as e:
            print(f"Test failed: {e}")
            return False
    
    print("All tests completed successfully!")
    return True


if __name__ == "__main__":
    main()
