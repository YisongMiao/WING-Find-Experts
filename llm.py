import os
import openai

def qwen(llm, system_prompt, user_prompt):
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