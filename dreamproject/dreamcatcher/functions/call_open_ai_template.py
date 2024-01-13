import openai
import json


def gpt_function_stub():
    # Initialize the OpenAI API client with your API key
    api_key = "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"
    openai.api_key = api_key

    prompt = f"prompt here"

    # Use GPT-3.5 to get the start time
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": prompt},
        ],
    )

    response_string = response.choices[0].message.content

    response_json = json.loads(response_string)

    return response_json
