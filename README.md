# WING-Trial-Task (Software Engineering)

## Environment Setup

Run the following to install critical dependencies:
```bash
pip install torch sentence_transformers # Embedding model support
pip install openai                      # LLM API support
pip install requests bs4                # Required for URL parsing
pip install numpy tqdm
```

Current implementation uses QWen LLM API, so an API key is required. You will need to run the following before running the program:
```bash
export QWEN_API_KEY="$YOUR_API_KEY"
```
where `$YOUR_API_KEY` should be your own API key for QWen.

## Getting Started

The entry to this program is `main.py` --- you can use the default setting by simply running:
```bash
python main.py
```

I provide several parameters for `main.py`:
* `--data_path` specifies the path to the database file, whose format can be referred to [`data/test_database.jsonl`](data/test_database.jsonl).
* `--query_path` specifies the path to the input query, whose format can be referred to [`data/test_query.json`](data/test_query.json).
* `--output_path` specifies the path for output.
* `--llm` specifies the name of LLM to use (currently only QWen models are supported).
* `--embedding_model_name_or_path` specifies the path or name of `sentence_transformers` embedding model.
* `--author_embedding` specifies the method used to compute author embedding from multiple publications:
    + `summarize` means using an LLM to summarize all publications from one author. The embedding will be computed based on the summary.
    + `aggregate` means computing embeddings for each publication from one author and taking the average.
* `--device` specifies the device to store and run the embedding model.

You will obtain a `.txt` output file in the `--output_path` directory when code execution is complete.

## TODO (Extensions)

* Parse timestamp of publications to support decaying weights for older publications in embedding aggregation.
* Support error handling in publication parsing.
* Dynamic adaptation to new publications for authors.
* Curve the score to distinguish fitness better.