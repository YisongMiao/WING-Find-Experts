from llm import qwen

system_prompt = "You are an academic chair of a conference. Given the information of a paper (title and abstract) and a reviewer (), explain why the reviewer is a good or bad fit to review the paper according to the provided fitness score."

user_prompt = """
Paper Title: $title
Paper Abstract: $abstract
Summary of Research by the Reviewer: $author_info
Fitness Score (out of 100): $score

Explain whether the reviewer is a good fit to review the paper based on the given fitness score:
"""

def generate_justification(query: dict[str, str], author_info: str, score: int, args):
    """
    This function generates the explanation for the fitness score between paper and reviewer.
    
    Args:
        query (dict[str, str]): A dict with keys `title` and `abstract` for the paper.
        author_info (str): A paragraph describing the research directions of the reviewer.
        score (int): A number indicating the fitness between paper and reviewer.
        args (:class:`~argparse.Namespace`): A namespace of arguments. In this function we only require the `llm` field to determine the LLM to use.
    
    Returns:
        output (str): A paragraph explaning why the reviewer is or is not a good fit to review the paper.
    """
    prompt = user_prompt.replace("$title", query["title"])
    prompt = prompt.replace("$abstract", query["abstract"])
    prompt = prompt.replace("$author_info", author_info)
    prompt = prompt.replace("$score", str(score))
    
    return qwen(args.llm, system_prompt, prompt)