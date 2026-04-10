from openai import OpenAI
import os


def get_client():
    return OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=os.getenv("OPENROUTER_API_KEY"),
    )


def chat(messages, model="google/gemma-4-31b-it:free"):
    client = get_client()

    response = client.chat.completions.create(
        model=model,
        messages=messages,
    )

    return response.choices[0].message.content
