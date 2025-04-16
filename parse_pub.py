import re
import requests
from bs4 import BeautifulSoup
from xml.etree import ElementTree as ET

def get_arxiv_metadata(url):
    """
    通过arXiv API获取标题和摘要
    参数：arxiv_url (str) - arXiv抽象页面URL，如：https://arxiv.org/abs/1706.03762
    返回：字典包含标题、摘要和arXiv ID
    """
    # 提取arXiv ID
    arxiv_id = re.search(r'arxiv\.org/abs/([\w\.-]+)', url).group(1)
    
    # 构造API请求URL
    api_url = f"http://export.arxiv.org/api/query?id_list={arxiv_id}"
    
    response = requests.get(api_url, timeout=10)
    response.raise_for_status()
    
    # 解析XML响应
    root = ET.fromstring(response.content)
    entry = root.find('{http://www.w3.org/2005/Atom}entry')
    
    title = ' '.join(entry.find('{http://www.w3.org/2005/Atom}title').text.strip().split())
    abstract = entry.find('{http://www.w3.org/2005/Atom}summary').text.strip()
    
    # 清理换行和多余空格
    abstract = ' '.join(abstract.split())
    
    return {
        "title": title,
        "abstract": abstract
    }

def get_openreview_metadata(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # 检查请求是否成功
    
    # 解析HTML
    soup = BeautifulSoup(response.text, 'html.parser')
    title_meta = soup.find('meta', {'name': 'citation_title'})
    title = ' '.join(title_meta['content'].split()).strip()
    
    abstract_meta = soup.find('meta', {'name': 'citation_abstract'})
    # 清理换行和多余空格
    abstract = ' '.join(abstract_meta['content'].split()).strip()
    
    return {
        'title': title,
        'abstract': abstract
    }
    
def get_neurips_metadata(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
        
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # 检查请求是否成功
    
    soup = BeautifulSoup(response.text, 'html.parser')
    container = soup.find('div', class_='col p-3')  # 定位主要内容容器
    
    # 提取标题（第一个h4元素）
    title = ' '.join(container.find('h4').get_text(strip=True).split())
    
    # 提取摘要（定位Abstract标题后的p标签）
    abstract = ""
    abstract_heading = container.find('h4', string='Abstract')
    abstract_p = abstract_heading.find_next_sibling('p')
    if abstract_p:
        # 处理嵌套的p标签情况
        abstract = ' '.join(abstract_p.stripped_strings)
    
    return {
        'title': title,
        'abstract': abstract or "摘要未找到"
    }

# TODO: parse paper url and extract title and abstract of each paper
def parse_url(url: str):
    if url.startswith("https://arxiv.org"):
        return get_arxiv_metadata(url)
    elif url.startswith("https://openreview.net"):
        return get_openreview_metadata(url)
    elif url.startswith("https://proceedings.neurips.cc"):
        return get_neurips_metadata(url)
    else:
        raise NotImplementedError("Website not supported yet")
    
if __name__ == "__main__":
    # 使用示例
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