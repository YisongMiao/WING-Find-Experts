# Author Profile Summary Generator

This program generates research summaries for authors based on their publications using GPT API.

## Features

- Loads author profiles from JSON files
- Generates comprehensive research summaries using GPT-4
- Supports programmable starting and ending indices for batch processing
- Includes error handling and retry logic for API calls
- Saves updated profiles to new JSON files

## Prerequisites

1. Set your OpenAI API key as an environment variable:
   ```bash
   export OPENAI_API_KEY="your-api-key-here"
   ```

2. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Basic Usage
```bash
python author_profile_summary.py
```

This will process all authors in the default input file (`log/author_profile.json`) and save results to `log/author_profile_updated.json`.

### Custom Input/Output Files
```bash
python author_profile_summary.py --input path/to/input.json --output path/to/output.json
```

### Process Specific Range of Authors
```bash
# Process authors from index 0 to 9 (first 10 authors)
python author_profile_summary.py --start 0 --end 10

# Process authors from index 100 to 199 (100 authors starting from index 100)
python author_profile_summary.py --start 100 --end 200

# Process authors from index 500 to the end
python author_profile_summary.py --start 500
```

### Command Line Arguments

- `--input`: Input JSON file with author profiles (default: `log/author_profile.json`)
- `--output`: Output JSON file for updated profiles (default: `log/author_profile_updated.json`)
- `--start`: Starting index for processing authors (default: 0)
- `--end`: Ending index for processing authors, exclusive (default: all authors)

## Input Format

The input JSON file should contain a list of authors, where each author has:
- `name`: Author's name
- `publication_urls`: List of publication URLs
- `list_of_pubs`: List of publications with `title` and `abstract`
- `summary`: Research summary (will be generated if empty)

## Output Format

The output JSON file will contain the same structure as the input, but with the `summary` field populated for processed authors.

## Rate Limiting

The program includes a 2-second delay between API calls to avoid rate limiting. You can adjust this in the `process_authors` function if needed.

## Error Handling

- API connection errors are automatically retried (up to 10 times)
- Authors with existing summaries are skipped
- Authors without publications are warned about
- All errors are logged and the program continues processing other authors

## Example

```bash
# Process first 50 authors
python author_profile_summary.py --start 0 --end 50 --output log/first_50_authors.json

# Process authors 100-149
python author_profile_summary.py --start 100 --end 150 --output log/authors_100_149.json
```
