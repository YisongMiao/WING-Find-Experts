#!/bin/bash

# Demo script to run GPT-based expert finding for multiple queries
# Directly calls GPT to find experts without embedding models

echo "Starting GPT-based expert finding demo..."
echo "========================================"

# Array of query indices to test
queries=(0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23)

# Loop through each query
for query_idx in "${queries[@]}"; do
    echo ""
    echo "Processing Query $query_idx with GPT..."
    echo "====================================="
    
    # Run the GPT-based expert finding script
    python prompt_gpt.py --query-id $query_idx --verbose
    
    # Check if the command was successful
    if [ $? -eq 0 ]; then
        echo "✓ Successfully completed query $query_idx with GPT"
    else
        echo "✗ Failed to complete query $query_idx with GPT"
        exit 1
    fi
    
    echo "Waiting 3 seconds before next run..."
    sleep 3
done

echo ""
echo "🎉 GPT demo completed successfully!"
echo "All queries (${queries[0]}-${queries[-1]}) processed with GPT-4o-mini"
echo ""
echo "Output files generated:"
echo "- JSON files: results/GPT/experts_query_{query}.json"
echo ""
echo "Total runs completed: ${#queries[@]}"
echo ""
echo "To view results:"
echo "ls -la results/GPT/"
