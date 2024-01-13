import openai
import json


# dream_chat should be an array sequnce alteranting beween
# user and chatbot conversations
# list[0] is user, list[1] is chatbot, list[2] is user...
def get_dream_question(dream_chat: list[str]):
    # parse only the user text
    dream_content = dream_chat[::2]
    dream_string = "\n".join(dream_content)

    api_key = "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"
    openai.api_key = api_key

    prompt = (
        f"Reformat this dream so its in paragraph format and more clean: {dream_string}"
    )

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

    return response_string


test_chat = [
    "I had a dream last night about an elephant in a church.",
    "What was the elephant doing inside the church in your dream? Can you describe its behavior or any specific details about the church or the elephant that stood out to you?",
    "The elephant was singing a song, maybe an opera song. It was also staring at me really funny.",
    "What do you think the elephant singing an opera song and staring at you in the church might symbolize or represent to you personally? Did you have any specific emotions or thoughts during the dream that stood out to you",
    "I think the elephant symbolizes my mother.",
    "In what ways do you see your mother's characteristics or traits reflected in the elephant's behavior or presence in the church in your dream?",
    "My mother is also really old and a little big.",
]

print(get_dream_question(test_chat))
