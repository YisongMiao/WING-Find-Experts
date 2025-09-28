import json
import os
import sys
import argparse
from llm import qwen

def load_query_data(query_id):
    """Load query data for a specific ID"""
    query_file = f"data-query/test_query_{query_id}.json"
    with open(query_file, 'r') as f:
        return json.load(f)

def load_ae_list():
    """Load the list of available experts"""
    with open("data-AE/AE_list.txt", 'r') as f:
        return [line.strip() for line in f.readlines() if line.strip()]

def create_expert_finding_prompt(query_title, query_abstract, expert_list):
    """Create a comprehensive prompt for expert finding"""
    
    system_prompt = """You are an expert researcher matching system. Your task is to identify the top 3 most suitable experts from a given list based on a research query.

You should consider:
1. Research expertise and domain knowledge
2. Publication history and research focus
3. Methodological approaches
4. Theoretical frameworks
5. Practical applications

Return ONLY a JSON object with exactly 3 candidates in this format:
{
  "candidate1": {
    "name": "Expert Name",
    "rationale": "Detailed explanation of why this expert is suitable for the query"
  },
  "candidate2": {
    "name": "Expert Name", 
    "rationale": "Detailed explanation of why this expert is suitable for the query"
  },
  "candidate3": {
    "name": "Expert Name",
    "rationale": "Detailed explanation of why this expert is suitable for the query"
  }
}

Do not include any other text, explanations, or formatting. Return only the JSON object."""

    user_prompt = f"""Research Query:
Title: {query_title}

Abstract: {query_abstract}

Available Experts:
{chr(10).join(expert_list)}

Please identify the top 3 most suitable experts for this research query and provide your reasoning."""

    return system_prompt, user_prompt

def find_experts_with_gpt(query_id):
    """Find experts using GPT for a given query ID"""
    
    # Load query data
    query_data = load_query_data(query_id)
    query_title = query_data['title']
    query_abstract = query_data['abstract']
    
    # Load expert list
    expert_list = load_ae_list()
    
    # Create prompt
    system_prompt, user_prompt = create_expert_finding_prompt(query_title, query_abstract, expert_list)
    
    # Call GPT
    print(f"Querying GPT for experts for query ID {query_id}...")
    print(f"Query Title: {query_title}")
    print("=" * 50)
    
    try:
        response = qwen("gpt-4o-mini", system_prompt, user_prompt)
        
        # Parse JSON response
        try:
            experts_data = json.loads(response)
            
            # Save results
            output_file = f"results/GPT/experts_query_{query_id}.json"
            with open(output_file, 'w') as f:
                json.dump(experts_data, f, indent=2)
            
            print(f"Results saved to {output_file}")
            print("Selected experts:")
            for i, (key, expert) in enumerate(experts_data.items(), 1):
                print(f"{i}. {expert['name']}")
                print(f"   Rationale: {expert['rationale']}")
                print()
            
            return experts_data
            
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response: {e}")
            print(f"Raw response: {response}")
            return None
            
    except Exception as e:
        print(f"Error calling GPT: {e}")
        return None

def main():
    """Main function to run expert finding"""
    parser = argparse.ArgumentParser(
        description="Find experts using GPT for a given query ID",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python prompt_gpt.py --query-id 0
  python prompt_gpt.py -q 1
  python prompt_gpt.py  # Uses default query ID 0
        """
    )
    
    parser.add_argument(
        '--query-id', '-q',
        type=int,
        default=0,
        help='Query ID to process (default: 0)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        print(f"Starting expert finding process...")
        print(f"Query ID: {args.query_id}")
        print(f"Output directory: results/GPT/")
    
    print(f"Finding experts for query ID: {args.query_id}")
    experts = find_experts_with_gpt(args.query_id)
    
    if experts:
        print("Expert finding completed successfully!")
    else:
        print("Expert finding failed!")

if __name__ == "__main__":
    main()
