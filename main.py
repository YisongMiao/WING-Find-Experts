import json
import argparse
import numpy as np
import torch

from tqdm import tqdm
from sentence_transformers import SentenceTransformer
from sentence_transformers.util import semantic_search

from process_data import build_author_profile
from generate_justification import generate_justification

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_path", type=str, default="./data/test_database.jsonl", help="")
    parser.add_argument("--query_path", type=str, default="./data/test_query.json")
    parser.add_argument("--llm", type=str, default="qwen2.5-72b-instruct")
    parser.add_argument("--embedding_model_name_or_path", type=str, default="")
    # TODO: Implement both multi-paper embedding aggregation and summarize-first embedding
    parser.add_argument("--author_embedding", type=str, choices=["aggregate", "summarize"], default="aggregate")
    parser.add_argument("--device", type=str, default="cpu")
    args = parser.parse_args()
    return args

def init_model(embedding_model_name_or_path: str, device: str):
    return SentenceTransformer(model_name_or_path=embedding_model_name_or_path).to(device)

def read_jsonl(path: str):
    with open(path, "r") as f:
        database = [json.load(line) for line in f]
    return database

def build_query(query_dict: dict):
    return f"Title: {query_dict['title']}\nAbstract: {query_dict['abstract']}"
    
def compute_fitness(model: SentenceTransformer, query, list_of_authors, args):
    query_embedding = model.encode(query, normalize_embeddings=True).unsqueeze(0)
    if args.author_embedding == "aggregate":
        # Compute the range of publications belonging to each author
        n_pub_per_author = [len(pubs) for pubs in list_of_authors]
        low, high = np.cumsum([0] + n_pub_per_author[:-1]), np.cumsum(n_pub_per_author)
        # Stack all publications together and compute embedding only once
        stacked_pubs = sum(list_of_authors, [])
        all_pub_embedding = model.encode_multi_process(stacked_pubs, normalize_embeddings=True)
        # Seperately aggregate the embedding of each author
        corpus_embedding = torch.stack([torch.mean(all_pub_embedding[l:h]) for l, h in zip(low, high)], dim=0)
    elif args.author_embedding == "summarize":
        corpus_embedding = model.encode_multi_process(list_of_authors, normalize_embeddings=True)
    else:
        raise NotImplementedError(f"Author Embedding:{args.author_embedding} method not implemented")
    return semantic_search(query_embedding, corpus_embedding, top_k=len(list_of_authors))

def main():
    args = get_args()
    
    # Initialize the embedding model
    model = init_model(args.embedding_model_name_or_path, args.device)
    
    # Input query and build database
    query_dict = json.load(args.query_path)
    database = read_jsonl(args.data_path)
    
    # Process the database so that each item provides more details of each author
    # TODO: design how to parse each publication and build profile for each author
    database = build_author_profile(database, args)
    
    # Process the query so that the query can be more specific
    # TODO: design how query should be processed
    query = build_query(query_dict)
    
    # Compute fitness score in batch
    list_of_authors = [item["content"] for item in database]
    sorted_id_and_scores = compute_fitness(model, query, list_of_authors, args)
    
    # Generate justification for each reviewer
    results = []
    for item in tqdm(sorted_id_and_scores):
        author_id, score = item["corpus_id"], item["score"]
        reason = generate_justification(query_dict, database[author_id]["summary"], round(score * 100))
        results.append({
            "fitness": score,
            "explanation": reason
        })
    
    with open(args.output_path, "w") as f:
        for item in results:
            f.write(json.dumps(item) + "\n")
            
if __name__ == "__main__":
    main()