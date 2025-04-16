import json
import argparse

from process_data import build_author_profile

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_path", type=str, default="./database.jsonl", help="")
    parser.add_argument("--query_path", type=str, default="./query.json")
    parser.add_argument("--model", type=str, default="")
    args = parser.parse_args()
    return args

def read_jsonl(path: str):
    with open(path, "r") as f:
        database = [json.load(line) for line in f]
    return database

def augment_query(query_dict: dict):
    ...
    
def compute_fitness(query, author_info):
    ...
    
def generate_justification(query, author_info, score):
    ...

def main():
    args = get_args()
    
    # Input query and build database
    query_dict = json.load(args.query_path)
    database = read_jsonl(args.data_path)
    
    # Process the database so that each item provides more details of each author
    # TODO: design how to parse each publication and build profile for each 
    database = build_author_profile(database)
    
    # Process the query so that the query can be more specific
    # TODO: design how query should be processed
    query = augment_query(query_dict)
    
    # Compute fitness score
    results = []
    for item in database:
        score = compute_fitness(query, item)
        reason = generate_justification(query, item, score)
        results.append({
            "fitness": score,
            "explanation": reason
        })
    
    with open(args.output_path, "w") as f:
        for item in results:
            f.write(json.dumps(item) + "\n")