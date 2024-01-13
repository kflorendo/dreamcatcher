import openai
import json
from dotenv import load_dotenv
import os


def get_dream_analysis(dream_text: str):
    load_dotenv()
    OPENAI_KEY = os.getenv('OPENAI_KEY')
    openai.api_key = OPENAI_KEY

    prompt = f"Interpret this dream: {dream_text}"

    # Use GPT-3.5 to get the start time
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": prompt},
        ],
    )

    response_string = response.choices[0].message.content

    return response_string
