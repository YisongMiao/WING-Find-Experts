# WING's Tool for Expert Finding

This repo contains the code from Ruiwen Zhou's trial task for the expert finding task. We credit a lot to his efforts. \
Ruiwen's source: https://github.com/SkyRiver-2000/WING-Trial-Task


## Environment Setup


Run the following to install critical dependencies: `
First setup a new environment:

**💽 Create a new environment and activate it:**
```bash
python --version
conda create --name findexpert python=3.10
conda activate findexpert
```

**💽 Install dependencies:**
```bash
pip install torch sentence_transformers # Embedding model support
pip install openai                      # LLM API support
pip install requests bs4                # Required for URL parsing
pip install numpy tqdm
```

**💽 Set up API key:**
Current implementation uses OpenAI API, so an API key is required. You will need to run the following before running the program:

where `sk-yourrealkeyhere` should be your own API key for OpenAI.


- `vim ~/.bashrc` # open the bashrc file
- Write `export OPENAI_API_KEY="sk-yourrealkeyhere"` into the bashrc file.  # your own API key
- `source ~/.bashrc` # reload the bashrc file
- `echo $OPENAI_API_KEY` # check if the API key is set


**⚠️ And also make sure that never commit your API key to the repo.**

## Getting Started

The entry to this program is `main.py` --- you can use the default setting by simply running:
```bash
python main.py
```

I provide several parameters for `main.py`:
* `--data_path` specifies the path to the database file, whose format can be referred to [`data/test_database.jsonl`](data/test_database.jsonl).
* `--query_path` specifies the path to the input query, whose format can be referred to [`data/test_query.json`](data/test_query.json).
* `--output_path` specifies the path for output.
* `--llm` specifies the name of LLM to use (currently only OpenAI models are supported).
* `--embedding_model_name_or_path` specifies the path or name of `sentence_transformers` embedding model.
* `--author_embedding` specifies the method used to compute author embedding from multiple publications:
    + `summarize` means using an LLM to summarize all publications from one author. The embedding will be computed based on the summary.
    + `aggregate` means computing embeddings for each publication from one author and taking the average.
* `--device` specifies the device to store and run the embedding model.

You will obtain a `.txt` output file in the `--output_path` directory when code execution is complete. Sample outputs are shown as [`log/output_aggregate.txt`](log/output_aggregate.txt) and [`log/output_summarize.txt`](log/output_summarize.txt)

## TODO (Extensions)

* Parse timestamp of publications to support decaying weights for older publications in embedding aggregation.
* Support error handling in publication parsing.
* Dynamic adaptation to new publications for authors.
* Curve the score to distinguish fitness better.