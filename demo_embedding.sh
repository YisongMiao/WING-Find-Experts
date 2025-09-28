#!/bin/bash

# Demo script to run through all queries (1-3) and both embedding modes (aggregate and summarize)
# Uses default settings for other parameters

echo "Starting demo run for all queries and embedding modes..."
echo "=================================================="

# Array of query indices to test
queries=(0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23)

# Array of embedding modes to test
modes=("aggregate" "summarize")

# Loop through each query
for query_idx in "${queries[@]}"; do
    echo ""
    echo "Processing Query $query_idx..."
    echo "================================"
    
    # Loop through each embedding mode
    for mode in "${modes[@]}"; do
        echo ""
        echo "Running with embedding mode: $mode"
        echo "--------------------------------"
        
        # Run the main script with current query and mode
        python main.py --query_index $query_idx --author_embedding $mode
        
        # Check if the command was successful
        if [ $? -eq 0 ]; then
            echo "✓ Successfully completed query $query_idx with $mode mode"
        else
            echo "✗ Failed to complete query $query_idx with $mode mode"
            exit 1
        fi
        
        echo "Waiting 2 seconds before next run..."
        sleep 2
    done
    
    echo ""
    echo "Completed all modes for query $query_idx"
    echo "========================================"
done

echo ""
echo "🎉 Demo completed successfully!"
echo "All queries (${queries[0]}-${queries[-1]}) processed with both ${modes[0]} and ${modes[1]} modes"
echo ""
echo "Output files generated:"
echo "- CSV files: results/fitness_scores_{mode}_query_{query}.csv"
echo "- TXT files: results/output_{mode}_query_{query}.txt"
echo ""
echo "Total runs completed: $(( ${#queries[@]} * ${#modes[@]} ))"
