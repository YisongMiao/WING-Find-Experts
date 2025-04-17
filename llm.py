import os
import openai

def qwen(llm: str, system_prompt: str, user_prompt: str):
    """
    This function wraps the QWen API.
    
    Args:
        llm (str): The name of LLM to use.
        system_prompt (str): The system prompt to the LLM.
        user_prompt (str): The user prompt to the LLM.
    
    Returns:
        output (str): The textual response from the LLM.
    """
    api_key = os.environ["QWEN_API_KEY"]
    engine = openai.OpenAI(
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        api_key=api_key
    )
    response = engine.chat.completions.create(
        model=llm,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.0,
    )
    return response.choices[0].message.content