import time
from llm import qwen
from tqdm import tqdm
from typing import Any
from parse_pub import parse_url

system_prompt = "You are an academic expert. Given the information of several papers (title and abstract) from one author, summarize the main research contributions of this author."

def summarize_publication(list_of_publications: list[dict[str, str]], args):
    """
    This function asks the LLM to summarize the publications from an author into a paragraph describing his/her research directions.
    
    Args:
        list_of_publications (list[dict[str, str]]): A list of publications from an author. Each entry is a dict with keys `title` and `abstract`.
        args: args (:class:`argparse.Namespace`): A namespace of arguments. In this function we only require the `llm` field to determine the LLM to use.
    
    Returns:
        output (str): A string describing the research directions of the author.
    """
    user_prompt = "\n\n".join(
        [f"Title: {pub['title']}\nAbstract: {pub['abstract']}" for pub in list_of_publications]
    ) + "\n\nSummary of Research:"
    return qwen(args.llm, system_prompt, user_prompt)

def build_author_profile(database: list[dict[str, Any]], args):
    """
    This function creates the profile of each author by parsing their publications and summarizing.
    
    Args:
        database (list[dict[str, Any]]): A list of authors. Each entry is a dict with keys `name` and `publication_urls`.
        args (:class:`~argparse.Namespace`): A namespace of arguments. In this function we only require the `author_embedding` field to determine the way of aggregating publications for each author.
    
    Returns:
        database (list[dict[str, Any]]): A list of authors. Each entry will be augmented with an extra `summary` and `content` field.
    """
    for item in tqdm(database):
        list_of_publications = []
        for url in item["publication_urls"]:
            # Parse the publication url
            paper_dict = parse_url(url)
            list_of_publications.append(paper_dict)
            # Less frequent parsing to avoid being blocked
            time.sleep(3)
        # Summarize the overall research directions of this author
        item["summary"] = summarize_publication(list_of_publications)
        if args.author_embedding == "aggregate":
            item["content"] = list_of_publications
        elif args.author_embedding == "summarize":
            item["content"] = item["summary"]
        else:
            raise NotImplementedError(f"Author aggregation: {args.author_embedding} method not implemented")
    return database