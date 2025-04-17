import re
import requests
from bs4 import BeautifulSoup
from xml.etree import ElementTree as ET

def get_arxiv_metadata(url: str):
    """
    This function requests paper title and abstract through arXiv API.
    
    Args:
        url (str): arXiv abs page URL, such as https://arxiv.org/abs/1706.03762
    
    Returns:
        paper_dict (dict[str, str]): A dict with the keys "title" and "abstract"
    """
    # Extract arXiv ID
    arxiv_id = re.search(r'arxiv\.org/abs/([\w\.-]+)', url).group(1)
    
    # Construct the request URL for arXiv API
    api_url = f"http://export.arxiv.org/api/query?id_list={arxiv_id}"
    
    # Request data
    response = requests.get(api_url, timeout=10)
    response.raise_for_status()
    
    # Parse XML response
    root = ET.fromstring(response.content)
    entry = root.find('{http://www.w3.org/2005/Atom}entry')
    
    # Get title and abstract
    title = entry.find('{http://www.w3.org/2005/Atom}title').text.strip()
    abstract = entry.find('{http://www.w3.org/2005/Atom}summary').text.strip()
    
    # Re-format title and abstract
    title = ' '.join(title.split())
    abstract = ' '.join(abstract.split())
    
    return {
        "title": title,
        "abstract": abstract
    }

def get_openreview_metadata(url):
    """
    This function requests paper title and abstract by parsing an openreview webpage.
    
    Args:
        url (str): openreview page URL, such as https://openreview.net/forum?id=BwR8t91yqh
    
    Returns:
        paper_dict (dict[str, str]): A dict with the keys "title" and "abstract"
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    # Request data
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    
    # Parse HTML
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Parse and re-format title and abstract
    title_meta = soup.find('meta', {'name': 'citation_title'})
    title = ' '.join(title_meta['content'].split()).strip()
    
    abstract_meta = soup.find('meta', {'name': 'citation_abstract'})
    abstract = ' '.join(abstract_meta['content'].split()).strip()
    
    return {
        'title': title,
        'abstract': abstract
    }
    
def get_neurips_metadata(url):
    """
    This function requests paper title and abstract by parsing a NeurIPS abstract webpage.
    
    Args:
        url (str): NeurIPS abs page URL, such as https://proceedings.neurips.cc/paper_files/paper/2024/hash/84bad835faaf48f24d990072bb5b80ee-Abstract-Conference.html
    
    Returns:
        paper_dict (dict[str, str]): A dict with the keys "title" and "abstract"
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
        
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # 检查请求是否成功
    
    # Parse HTML and locate the container involving title and abstract
    soup = BeautifulSoup(response.text, 'html.parser')
    container = soup.find('div', class_='col p-3')
    
    # Get the title (the first h4 element)
    title = ' '.join(container.find('h4').get_text(strip=True).split())
    
    # Get the abstract（through the <p> mark after the title `Abstract`）
    abstract = ""
    abstract_heading = container.find('h4', string='Abstract')
    abstract_p = abstract_heading.find_next_sibling('p')
    if abstract_p:
        abstract = ' '.join(abstract_p.stripped_strings)
    
    return {
        'title': title,
        'abstract': abstract or None
    }

def parse_url(url: str):
    """
    This function wraps functions that request paper title and abstract on different websites.
    If the provided website is not supported yet, this function will raise a `NotImplementedError`.
    
    Args:
        url (str): paper URL
    
    Returns:
        paper_dict (dict[str, str]): A dict with the keys "title" and "abstract"
    """
    # arXiv 
    if url.startswith("https://arxiv.org"):
        return get_arxiv_metadata(url)
    # openreview
    elif url.startswith("https://openreview.net"):
        return get_openreview_metadata(url)
    # NeurIPS
    elif url.startswith("https://proceedings.neurips.cc"):
        return get_neurips_metadata(url)
    else:
        raise NotImplementedError("Website not supported yet")
    
if __name__ == "__main__":
    # Test example
    import json
    import time
    from tqdm import tqdm
    
    with open("./data/test_database.jsonl", "r") as f:
        database = [json.loads(line) for line in f]
    
    with open('test.log', 'w') as f:
        for author_item in tqdm(database):
            f.write(author_item["name"] + "\n\n")
            for i, url in enumerate(author_item["publication_urls"]):
                paper_dict = parse_url(url)
                f.write(f"Title: {paper_dict['title']}\n")
                f.write(f"Abstract: {paper_dict['abstract']}\n\n")
                time.sleep(3)
            f.write("================\n\n")