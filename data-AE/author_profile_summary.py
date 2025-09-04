import os
import json
import time
import argparse
from typing import List, Dict, Any
import openai
from tqdm import tqdm


def call_gpt(system_prompt: str, user_prompt: str, max_retry: int = 10):
    """
    Local function to call GPT API for generating author summaries.
    
    Args:
        system_prompt (str): The system prompt to the LLM.
        user_prompt (str): The user prompt to the LLM.
        max_retry (int): Maximum number of retries for API calls.
    
    Returns:
        output (str): The textual response from the LLM.
    """
    api_key = os.environ["OPENAI_API_KEY"]
    client = openai.OpenAI(api_key=api_key)
    
    error_cnt = 0
    while error_cnt < max_retry:
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini-2024-07-18",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.0,
            )
            return response.choices[0].message.content
        except openai.BadRequestError as e:
            raise e
        except openai.APIConnectionError as e:
            error_cnt += 1
            if error_cnt >= max_retry:
                raise e
            time.sleep(1)
        except Exception as e:
            error_cnt += 1
            if error_cnt >= max_retry:
                raise e
            time.sleep(1)
    raise Exception("Max retries exceeded")


def estimate_tokens(text: str) -> int:
    """
    Rough estimation of token count for text.
    GPT models typically use ~4 characters per token for English text.
    
    Args:
        text (str): Text to estimate tokens for.
    
    Returns:
        int: Estimated token count.
    """
    return len(text) // 4


def truncate_publications_for_context(publications: List[Dict[str, str]], max_tokens: int = 6000) -> List[Dict[str, str]]:
    """
    Truncate publications to fit within GPT context limits.
    Prioritizes keeping more recent publications and truncates abstracts if necessary.
    
    Args:
        publications (List[Dict[str, str]]): List of publications with title and abstract.
        max_tokens (int): Maximum tokens allowed for publications (leaving room for prompts).
    
    Returns:
        List[Dict[str, str]]: Truncated list of publications.
    """
    if not publications:
        return publications
    
    # Start with all publications
    selected_pubs = publications.copy()
    current_tokens = sum(estimate_tokens(pub['title'] + pub['abstract']) for pub in selected_pubs)
    
    # If we're under the limit, return all
    if current_tokens <= max_tokens:
        return selected_pubs
    
    # If we're over the limit, start removing publications from the end (older ones)
    while current_tokens > max_tokens and len(selected_pubs) > 1:
        removed_pub = selected_pubs.pop()
        current_tokens -= estimate_tokens(removed_pub['title'] + removed_pub['abstract'])
    
    # If still over limit, truncate abstracts
    if current_tokens > max_tokens:
        for pub in selected_pubs:
            if current_tokens <= max_tokens:
                break
            
            # Truncate abstract if it's too long
            abstract = pub['abstract']
            while current_tokens > max_tokens and len(abstract) > 100:
                # Remove last sentence
                sentences = abstract.split('. ')
                if len(sentences) > 1:
                    abstract = '. '.join(sentences[:-1]) + '.'
                else:
                    # If only one sentence, truncate by words
                    words = abstract.split()
                    if len(words) > 20:
                        abstract = ' '.join(words[:20]) + '...'
                    else:
                        break
                
                pub['abstract'] = abstract
                current_tokens = estimate_tokens(pub['title'] + pub['abstract'])
    
    print(f"Selected {len(selected_pubs)} publications (estimated {current_tokens} tokens)")
    return selected_pubs


def create_author_summary_prompt(author_name: str, publications: List[Dict[str, str]]) -> str:
    """
    Create a prompt for summarizing an author's research contributions.
    
    Args:
        author_name (str): Name of the author.
        publications (List[Dict[str, str]]): List of publications with title and abstract.
    
    Returns:
        str: Formatted prompt for the LLM.
    """
    user_prompt = f"Author: {author_name}\n\n"
    user_prompt += "Publications:\n\n"
    
    for i, pub in enumerate(publications, 1):
        user_prompt += f"{i}. Title: {pub['title']}\n"
        user_prompt += f"   Abstract: {pub['abstract']}\n\n"
    
    user_prompt += "Please provide a comprehensive summary of this author's research contributions, expertise areas, and main research directions based on their publications. Focus on identifying patterns, methodologies, and key research themes. Make it maximum 250 words."
    
    return user_prompt


def generate_author_summary(author_name: str, publications: List[Dict[str, str]]) -> str:
    """
    Generate a summary for an author based on their publications.
    
    Args:
        author_name (str): Name of the author.
        publications (List[Dict[str, str]]): List of publications with title and abstract.
    
    Returns:
        str: Generated summary of the author's research.
    """
    system_prompt = """You are an academic expert specializing in research analysis. Your task is to analyze an author's publications and provide a comprehensive summary of their research contributions, expertise areas, and main research directions.

Please focus on:
1. Identifying the main research themes and areas of expertise
2. Highlighting key methodologies and approaches used
3. Summarizing significant contributions and findings
4. Describing the evolution of their research interests
5. Identifying potential applications and impact of their work

Provide a clear, concise summary that would be useful for understanding this researcher's expertise and contributions to their field. Make it maximum 250 words."""

    # Truncate publications to fit within context limits
    # Reserve ~2000 tokens for system prompt, user prompt, and response
    max_pub_tokens = 100000  # GPT-4o-mini context limit is 128K, reserve 28K for prompts
    truncated_pubs = truncate_publications_for_context(publications, max_pub_tokens)
    
    user_prompt = create_author_summary_prompt(author_name, truncated_pubs)
    
    try:
        summary = call_gpt(system_prompt, user_prompt)
        return summary
    except Exception as e:
        print(f"Error generating summary for {author_name}: {e}")
        return f"Error generating summary: {str(e)}"


def save_author_profiles_incremental(authors_data: List[Dict[str, Any]], output_file: str, current_index: int = None):
    """
    Save the updated author profiles to a JSON file incrementally.
    
    Args:
        authors_data (List[Dict[str, Any]]): List of author data with summaries.
        output_file (str): Path to the output JSON file.
        current_index (int): Current author index being processed (for logging).
    """
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(authors_data, f, indent=2, ensure_ascii=False)
        
        if current_index is not None:
            print(f"✓ Saved progress after processing author {current_index}")
        else:
            print(f"✓ Author profiles saved to {output_file}")
    except Exception as e:
        print(f"Error saving to {output_file}: {e}")


def process_authors(authors_data: List[Dict[str, Any]], start_idx: int, end_idx: int, output_file: str) -> List[Dict[str, Any]]:
    """
    Process authors within the specified index range to generate summaries.
    Saves progress incrementally after each summary.
    
    Args:
        authors_data (List[Dict[str, Any]]): List of author data.
        start_idx (int): Starting index for processing.
        end_idx (int): Ending index for processing.
        output_file (str): Output file to save progress incrementally.
    
    Returns:
        List[Dict[str, Any]]: Updated author data with summaries.
    """
    # Ensure indices are within bounds
    start_idx = max(0, start_idx)
    end_idx = min(len(authors_data), end_idx)
    
    print(f"Processing authors from index {start_idx} to {end_idx-1} (total: {end_idx - start_idx} authors)")
    print(f"Progress will be saved incrementally to: {output_file}")
    
    for i in tqdm(range(start_idx, end_idx), desc="Generating author summaries"):
        author = authors_data[i]
        
        # Skip if already has a summary
        if author.get("summary") and author["summary"].strip():
            print(f"Skipping {author['name']} - already has summary")
            continue
        
        # Check if publications exist
        if not author.get("list_of_pubs") or not author["list_of_pubs"]:
            print(f"Warning: {author['name']} has no publications to summarize")
            continue
        
        print(f"Generating summary for {author['name']} ({i+1}/{end_idx-start_idx})")
        
        # Generate summary
        summary = generate_author_summary(author['name'], author['list_of_pubs'])
        author['summary'] = summary
        
        # Save progress immediately after each summary
        save_author_profiles_incremental(authors_data, output_file, i)
        
        # Add delay to avoid rate limiting
        time.sleep(2)
    
    return authors_data


def save_author_profiles(authors_data: List[Dict[str, Any]], output_file: str):
    """
    Save the updated author profiles to a JSON file.
    
    Args:
        authors_data (List[Dict[str, Any]]): List of author data with summaries.
        output_file (str): Path to the output JSON file.
    """
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(authors_data, f, indent=2, ensure_ascii=False)
    print(f"Author profiles saved to {output_file}")


def main():
    parser = argparse.ArgumentParser(description="Generate summaries for author profiles")
    parser.add_argument("--input", default="log/author_profile.json", 
                       help="Input JSON file with author profiles")
    parser.add_argument("--output", default="log/author_profile_updated.json",
                       help="Output JSON file for updated author profiles")
    parser.add_argument("--start", type=int, default=0,
                       help="Starting index for processing authors")
    parser.add_argument("--end", type=int, default=None,
                       help="Ending index for processing authors (exclusive)")
    
    args = parser.parse_args()
    
    # Check if OpenAI API key is set
    if "OPENAI_API_KEY" not in os.environ:
        print("Error: OPENAI_API_KEY environment variable not set")
        return
    
    # Load author profiles
    print(f"Loading author profiles from {args.input}")
    try:
        with open(args.input, 'r', encoding='utf-8') as f:
            authors_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: Input file {args.input} not found")
        return
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in {args.input}")
        return
    
    print(f"Loaded {len(authors_data)} authors")
    
    # Set end index if not specified
    if args.end is None:
        args.end = len(authors_data)
    
    # Process authors with incremental saving
    updated_authors = process_authors(authors_data, args.start, args.end, args.output)
    
    print("Author profile summary generation completed!")
    print(f"Final results saved to: {args.output}")


if __name__ == "__main__":
    main()
