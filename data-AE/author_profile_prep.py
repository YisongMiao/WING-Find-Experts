import os
import json
from typing import List, Dict


def build_author_profile_from_publist(publist_path: str) -> Dict:
    with open(publist_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    author_name = data.get("author", "").strip()
    results: List[Dict] = data.get("results", [])

    publication_urls = []
    list_of_pubs = []

    for item in results:
        title = (item.get("title") or "").strip()
        abstract = (item.get("abstract") or "").strip()
        url = (item.get("url") or "").strip()
        if url:
            publication_urls.append(url)
        list_of_pubs.append({
            "title": title,
            "abstract": abstract,
        })

    return {
        "name": author_name,
        "publication_urls": publication_urls,
        "summary": "",
        "list_of_pubs": list_of_pubs,
    }


def main() -> None:
    repo_root = "/home/yisong/WING-Find-Experts"
    publist_dir = os.path.join(repo_root, "data-AE", "publist")
    output_dir = os.path.join(repo_root, "log")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "author_profile.json")

    profiles: List[Dict] = []

    if not os.path.isdir(publist_dir):
        raise FileNotFoundError(f"Publist directory not found: {publist_dir}")

    for fname in sorted(os.listdir(publist_dir)):
        if not fname.lower().endswith(".json"):
            continue
        fpath = os.path.join(publist_dir, fname)
        try:
            profile = build_author_profile_from_publist(fpath)
            # Skip if no name detected
            if profile.get("name"):
                profiles.append(profile)
        except Exception as exc:  # noqa: BLE001
            # Continue processing others even if one fails
            print(f"Failed to process {fpath}: {exc}")

    with open(output_path, "w", encoding="utf-8") as out:
        json.dump(profiles, out, ensure_ascii=False, indent=2)

    print(f"Wrote {len(profiles)} author profiles to {output_path}")


if __name__ == "__main__":
    main()
