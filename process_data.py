from parse_pub import parse_url

def build_author_profile(database: list[dict]):
    for item in database:
        list_of_publications = []
        for url in item["publication_urls"]:
            title, abstract = parse_url(url)
            list_of_publications.append({"title": title, "abstract": abstract})
        # TODO: utilize `list_of_publications` to build author profile
        ...
    return database