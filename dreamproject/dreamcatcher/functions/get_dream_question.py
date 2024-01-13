import openai
import json


def get_dream_question(dream_text: str):
    api_key = "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"
    openai.api_key = api_key

    prompt = f"Ask a question to learn more about this dream: {dream_text}"

    getNextQuestions = True  # flag to ensure question is clean and doesnt mention anything about the chatbot

    # Use GPT-3.5 to get the start time
    while getNextQuestions:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": prompt},
            ],
        )

        response_string = response.choices[0].message.content
        getNextQuestions = False

        banned_words = ["I", "I'm"]
        for word in banned_words:
            if word in response_string:
                getNextQuestions = True

    return response_string
