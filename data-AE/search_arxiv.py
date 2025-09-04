import os
import re
import csv
import json
import time
import random
from html import unescape
from typing import List, Dict, Optional
from urllib.parse import quote_plus
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError


def search_arxiv_author(author_name: str, output_path: Optional[str] = None, size: int = 50, timeout_seconds: int = 20) -> str:
    """Fetch the first page of arXiv search results for an author and save the HTML.

    Args:
        author_name: The author full name to search on arXiv.
        output_path: Optional explicit path to save the HTML file. If not provided,
            a file named like "arxiv_author_<Author_Name>.html" will be saved in the
            same directory as this script.
        size: Max results per page to request (arXiv supports up to 50 for one page).
        timeout_seconds: Network timeout in seconds.

    Returns:
        The absolute path to the saved HTML file.
    """

    if size <= 0 or size > 50:
        size = 50

    base_url = "https://arxiv.org/search/"
    # Build query for author search, showing abstracts, newest first, single page up to `size` results
    query_params = (
        f"?query={quote_plus(author_name)}"
        f"&searchtype=author"
        f"&abstracts=show"
        f"&order=-announced_date_first"
        f"&size={size}"
    )
    url = base_url + query_params

    # Prepare request with a reasonable user agent
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }

    request = Request(url, headers=headers)

    # Simple retry strategy for transient issues, with backoff and jitter
    last_error: Optional[Exception] = None
    for attempt in range(5):
        try:
            with urlopen(request, timeout=timeout_seconds) as response:
                html_bytes = response.read()
            break
        except HTTPError as exc:
            last_error = exc
            if exc.code in (429, 500, 502, 503, 504):
                sleep_s = 2.0 * (attempt + 1) + random.uniform(0.0, 1.0)
                time.sleep(sleep_s)
                continue
            raise
        except URLError as exc:
            last_error = exc
            sleep_s = 1.5 * (attempt + 1) + random.uniform(0.0, 0.5)
            time.sleep(sleep_s)
        except Exception as exc:  # noqa: BLE001 - broad to allow retry on any network error
            last_error = exc
            time.sleep(1.0 + attempt * 0.5)
    else:
        raise RuntimeError(f"Failed to fetch arXiv page after retries: {last_error}")

    # Determine output path (save under htmls/)
    if output_path is None:
        safe_author = "_".join(part for part in author_name.split())
        filename = f"arxiv_author_{safe_author}.html"
        script_dir = os.path.dirname(os.path.abspath(__file__))
        htmls_dir = os.path.join(script_dir, "htmls")
        os.makedirs(htmls_dir, exist_ok=True)
        output_path = os.path.join(htmls_dir, filename)

    # Write HTML bytes as-is to preserve source
    with open(output_path, "wb") as f:
        f.write(html_bytes)

    return os.path.abspath(output_path)


def _strip_html(text: str) -> str:
    # Remove tags and collapse whitespace
    text = re.sub(r"<[^>]+>", " ", text)
    text = unescape(text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def parse_arxiv_author_html(html_bytes: bytes) -> List[Dict[str, str]]:
    """Parse arXiv author search HTML and extract title, abstract-full, and URL per result.

    This avoids external dependencies (like BeautifulSoup) by using regex heuristics tailored
    to arXiv's current markup (as of 2024/2025). It may require updates if arXiv changes.
    """
    html_text = html_bytes.decode("utf-8", errors="replace")

    # Split by each result item
    result_blocks = re.split(r'<li\s+class="arxiv-result"[^>]*>', html_text)
    parsed: List[Dict[str, str]] = []

    for block in result_blocks:
        # Title
        title_match = re.search(r'<p\s+class="title[^"]*"[^>]*>(.*?)</p>', block, flags=re.DOTALL | re.IGNORECASE)
        if not title_match:
            continue
        raw_title = title_match.group(1)
        title = _strip_html(raw_title)

        # URL (from list-title link)
        url = ""
        url_match = re.search(r'<p\s+class="list-title[^"]*"[^>]*>\s*<a\s+href="([^"]+)"', block, flags=re.DOTALL | re.IGNORECASE)
        if url_match:
            url = url_match.group(1).strip()

        # Abstract full
        abs_match = re.search(r'<span\s+class="abstract-full[^"]*"[^>]*>(.*?)</span>', block, flags=re.DOTALL | re.IGNORECASE)
        abstract = ""
        if abs_match:
            raw_abs = abs_match.group(1)
            # Remove leading 'Abstract: ' if present after stripping
            abstract = _strip_html(raw_abs)
            if abstract.lower().startswith("abstract: "):
                abstract = abstract[len("Abstract: "):].strip()

        if title:
            parsed.append({"title": title, "abstract": abstract, "url": url})

    return parsed


def parse_and_save_json_from_html(html_path: str, author_name: str, output_json_path: Optional[str] = None) -> str:
    with open(html_path, "rb") as f:
        html_bytes = f.read()

    items = parse_arxiv_author_html(html_bytes)

    if output_json_path is None:
        output_json_path = os.path.join("/home/yisong/WING-Find-Experts/data-AE/publist", f"{author_name}.json")

    with open(output_json_path, "w", encoding="utf-8") as f:
        json.dump({"author": author_name, "results": items}, f, ensure_ascii=False, indent=2)

    return os.path.abspath(output_json_path)


if __name__ == "__main__":
    ae_list_path = "/home/yisong/WING-Find-Experts/data-AE/AE_list.txt"
    script_dir = os.path.dirname(os.path.abspath(__file__))
    htmls_dir = os.path.join(script_dir, "htmls")
    publist_dir = "/home/yisong/WING-Find-Experts/data-AE/publist"
    os.makedirs(htmls_dir, exist_ok=True)
    os.makedirs(publist_dir, exist_ok=True)

    # CSV summary path
    csv_summary = "/home/yisong/WING-Find-Experts/data-AE/arxiv_fetch_summary.csv"

    # Load experts
    with open(ae_list_path, "r", encoding="utf-8") as f:
        experts = [line.strip() for line in f if line.strip()]

    total = len(experts)
    done = 0

    # Prepare CSV header if file doesn't exist
    csv_exists = os.path.exists(csv_summary)
    with open(csv_summary, "a", encoding="utf-8", newline="") as csvfile:
        writer = csv.writer(csvfile)
        if not csv_exists:
            writer.writerow(["author", "html_saved", "json_saved", "num_results", "error"]) 

    for idx, author in enumerate(experts, start=1):
        error_msg = ""
        html_saved = ""
        json_saved = ""
        num_results = 0

        # Polite base delay with jitter between requests
        time.sleep(2.0 + random.uniform(0.0, 1.0))

        try:
            html_path = search_arxiv_author(author)
            html_saved = html_path

            json_path = parse_and_save_json_from_html(html_path, author)
            json_saved = json_path

            # Count items for stats
            with open(json_path, "r", encoding="utf-8") as jf:
                data = json.load(jf)
                num_results = len(data.get("results", []))

        except Exception as exc:  # noqa: BLE001
            error_msg = str(exc)
        finally:
            with open(csv_summary, "a", encoding="utf-8", newline="") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow([author, html_saved, json_saved, num_results, error_msg])

        done += 1
        print(f"Progress: {done}/{total} experts processed")

    print(f"Completed processing {done} experts. Summary written to: {csv_summary}")
