# Quick Start Guide

## Immediate Usage

### 1. Set your OpenAI API key
```bash
export OPENAI_API_KEY="your-api-key-here"
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the program

**Process all authors:**
```bash
python author_profile_summary.py
```

**Process first 10 authors:**
```bash
python author_profile_summary.py --start 0 --end 10
```

**Process authors 100-199:**
```bash
python author_profile_summary.py --start 100 --end 200
```

**Custom input/output files:**
```bash
python author_profile_summary.py --input my_authors.json --output my_summaries.json
```

## What the Program Does

1. **Loads** author profiles from `log/author_profile.json`
2. **Generates** research summaries using GPT-4 for each author
3. **Saves** updated profiles with summaries to output file
4. **Skips** authors who already have summaries
5. **Handles** errors gracefully and continues processing

## Key Features

- ✅ **Programmable indices**: Start/stop at any point
- ✅ **Resume capability**: Skip already processed authors
- ✅ **Batch processing**: Process authors in chunks
- ✅ **Error handling**: Retry logic for API failures
- ✅ **Rate limiting**: Built-in delays to avoid API limits
- ✅ **Progress tracking**: Visual progress bars and status updates

## Output

The program creates a new JSON file with the same structure as input, but with the `summary` field populated for each processed author.

## Example Output Structure
```json
{
  "name": "Author Name",
  "publication_urls": [...],
  "list_of_pubs": [...],
  "summary": "This author specializes in machine learning and computer vision..."
}
```

## Troubleshooting

- **API Key Error**: Make sure `OPENAI_API_KEY` is set
- **File Not Found**: Check that `log/author_profile.json` exists
- **Rate Limiting**: The program includes 2-second delays between calls
- **Memory Issues**: Process authors in smaller batches using `--start` and `--end`

## Need Help?

- Run `python author_profile_summary.py --help` for command options
- Check `README.md` for detailed documentation
- Run `python test_author_summary.py` to test functionality
- Run `python example_usage.py` to see usage examples
