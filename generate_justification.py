from llm import qwen

system_prompt = "You are an academic chair of a conference. Given the information of a paper (title and abstract) and a reviewer (), explain why the reviewer is a good or bad fit to review the paper according to the provided fitness score."

user_prompt = """
Paper Title: $title
Paper Abstract: $abstract
Summary of Research by the Reviewer: $author_info
Fitness Score (out of 100): $score

Explain whether the reviewer is a good fit to review the paper:
"""

def generate_justification(query: dict[str, str], author_info: str, score: int, args):
    prompt = user_prompt.replace("$title", query["title"])
    prompt = prompt.replace("$abstract", query["abstract"])
    prompt = prompt.replace("$author_info", author_info)
    prompt = prompt.replace("$score", score)
    
    return qwen(args.llm, system_prompt, prompt)