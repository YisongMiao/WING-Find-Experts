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
    """
    This function parses the arguments for this run.
    
    Returns:
        args (:class:`~argparse.Namespace`): A namespace of arguments.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_path", type=str, default="./data/test_database.jsonl", help="Path to the database file")
    parser.add_argument("--query_path", type=str, default="./data/test_query.json", help="Path to the query file")
    parser.add_argument("--llm", type=str, default="qwen2.5-72b-instruct", help="LLM to generate justification of fitness score.")
    parser.add_argument("--embedding_model_name_or_path", type=str, default="all-MiniLM-L6-v2", help="Embedding model name or path.")
    parser.add_argument("--author_embedding", type=str, choices=["aggregate", "summarize"], default="aggregate", help="Method to aggregate multiple publications for one author.")
    parser.add_argument("--device", type=str, default="cpu", help="Computation device to store the embedding model and compute embeddings.")
    args = parser.parse_args()
    return args

def init_model(embedding_model_name_or_path: str, device: str):
    """
    This function initializes the embedding model.
    
    Args:
        embedding_model_name_or_path (str): The path to or the name of embedding model.
        device (str): The device to store and run the embedding model.
    
    Returns:
        model (:class:`~SentenceTransformer`): A sentence embedding model.
    """
    return SentenceTransformer(model_name_or_path=embedding_model_name_or_path).to(device)

def read_jsonl(path: str):
    """
    This function reads the database file and initialize the database with author names and publication URLs.
    
    Args:
        path (str): The path to the database file.
        
    Returns:
        database (list[str, Any]): A list of authors. Each entry is a dict with keys `name` and `publication_urls`.
    """
    with open(path, "r") as f:
        database = [json.loads(line) for line in f]
    return database

def build_query(query_dict: dict[str, str]):
    """
    This function constructs the input string to encode for embedding.
    
    Args:
        query_dict (dict[str, str]): A dict with keys `title` and `abstract`.
    
    Returns:
        query (str): A string serving as query for retrieval.
    """
    return f"Title: {query_dict['title']}\nAbstract: {query_dict['abstract']}"
    
def compute_fitness(model: SentenceTransformer, query: str, list_of_authors: list[str], args):
    """
    This function computes the fitness scores for each author available as reviewer.
    
    Args:
        model (:class:`SentenceTransformer`): The sentence embedding model.
        query (str): The input information of a paper as retrieval query.
        list_of_authors (list[str]): A list of authors. Each entry is the information of an author as retrieval key.
        args (:class:`argparse.Namespace`): A namespace of arguments. In this function we only require the `author_embedding` field to determine the way of aggregating publications for each author.
    
    Returns:
        search_dict (list[dict[str, Union[int, float]]]): A list of dict with the keys 'corpus_id' and 'score', sorted by decreasing cosine similarity scores.
    """
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
    return semantic_search(query_embedding, corpus_embedding, top_k=len(list_of_authors))[0]

def main():
    args = get_args()
    
    # Initialize the embedding model
    model = init_model(args.embedding_model_name_or_path, args.device)
    
    # Input query and build database
    query_dict = json.load(args.query_path)
    database = read_jsonl(args.data_path)
    
    # Process the database so that each item provides more details of each author
    database = build_author_profile(database, args)
    
    # Process the query so that the query can be more specific
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