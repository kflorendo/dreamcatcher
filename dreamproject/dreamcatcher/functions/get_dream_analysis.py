import openai
import json


def get_dream_analysis(dream_text: str):
    api_key = "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"
    openai.api_key = api_key

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
