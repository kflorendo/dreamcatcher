import openai
import json
from dotenv import load_dotenv
import os


def get_dream_question(dream_text: str):
    load_dotenv()
    OPENAI_KEY = os.getenv('OPENAI_KEY')
    openai.api_key = OPENAI_KEY

    prompt = f"Ask a question to learn more about this dream: {dream_text}"

    # flag to ensure question is clean and doesnt mention anything about the chatbot
    getNextQuestions = True

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
