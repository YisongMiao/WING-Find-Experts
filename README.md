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
pip install pandas
```

**💽 Set up API key:**
Current implementation uses OpenAI API, so an API key is required. You will need to run the following before running the program:

where `sk-yourrealkeyhere` should be your own API key for OpenAI.


- `vim ~/.bashrc` # open the bashrc file
- Write `export OPENAI_API_KEY="sk-yourrealkeyhere"` into the bashrc file.  # your own API key
- `source ~/.bashrc` # reload the bashrc file
- `echo $OPENAI_API_KEY` # check if the API key is set


**⚠️ And also make sure that never commit your API key to the repo.**


Here’s a more user-friendly, polished version of your instructions with emojis and a clearer structure:

````md
## 🚀 Running the Program

First, create the required folders:  
```bash
mkdir data-AE
mkdir data-query
````

### 📂 Data Setup

* **`data-AE`** → Contact our team to receive the **confidential data**.
  (Note: While action editor publications are public, their IDs remain private 🔒)

* **`data-query`** → You can create your own query file (e.g., [`test_query_barid.json`](data-query/test_query_barid.json)).
  Here’s the format:

  ```json
  {
      "title": "Title of the query",
      "abstract": "Abstract of the query"
  }
  ```

### ▶️ Running the Program

To run the program, use:

```bash
python main.py --query_index <query_index>
```

Example for **Barid’s query**:

```bash
python main.py --query_index barid
```

### ⚙️ Key Parameters for `main.py`

* `--data_path` → Path to the database file (📩 contact us for access).
* `--query_path` → Path to your query file (e.g., `test_query_barid.json`).
  Query file format:

  ```json
  {
      "title": "Title of the query",
      "abstract": "Abstract of the query"
  }
  ```

### 📑 Output

After execution, the program will generate a `.txt` file in the `--output_path` directory.

🔍 Example outputs:

* [results/aggregate/fitness_scores_query_barid.csv](results/aggregate/fitness_scores_query_barid.csv)
* [results/summarize/output_query_barid.txt](results/summarize/output_query_barid.txt)

✅ That’s it—you’re ready to go! 🎉

```

Would you like me to make it **even shorter and more “quick start” style** (just the essentials with step numbers), or keep this detailed but polished version?
```



## Other arguments
* `--output_path` specifies the path for output (default: `results`).
* `--llm` specifies the name of LLM to use (currently only OpenAI models are supported).
* `--embedding_model_name_or_path` specifies the path or name of `sentence_transformers` embedding model.
* `--author_embedding` specifies the method used to compute author embedding from multiple publications:
    + `summarize` means using an LLM to summarize all publications from one author. The embedding will be computed based on the summary.
    + `aggregate` means computing embeddings for each publication from one author and taking the average.
* `--device` specifies the device to store and run the embedding model.
