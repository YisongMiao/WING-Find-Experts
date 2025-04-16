from llm import qwen
from tqdm import tqdm
from parse_pub import parse_url

system_prompt = "You are an academic expert. Given the information of several papers (title and abstract) from one author, summarize the main research contributions of this author."

def summarize_publication(list_of_publications, args):
    user_prompt = "\n\n".join(
        [f"Title: {pub['title']}\nAbstract: {pub['abstract']}" for pub in list_of_publications]
    ) + "\n\nSummary of Research:"
    summary = qwen(args.llm, system_prompt, user_prompt)

def build_author_profile(database: list[dict], args):
    for item in tqdm(database):
        list_of_publications = []
        for url in item["publication_urls"]:
            title, abstract = parse_url(url)
            list_of_publications.append({"title": title, "abstract": abstract})
        # TODO: utilize `list_of_publications` to build author profile
        item["summary"] = summarize_publication(list_of_publications)
        if args.author_embedding == "aggregate":
            item["content"] = list_of_publications
        elif args.author_embedding == "summarize":
            item["content"] = item["summary"]
        else:
            raise NotImplementedError(f"Author Embedding:{args.author_embedding} method not implemented")
    return database