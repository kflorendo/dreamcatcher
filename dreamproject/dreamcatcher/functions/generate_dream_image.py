import requests
from dotenv import load_dotenv
import os

# You can access the image with PIL.Image for example
import io
from PIL import Image

load_dotenv()
HF_KEY = os.getenv("HF_KEY")
API_URL = "https://api-inference.huggingface.co/models/SimianLuo/LCM_Dreamshaper_v7"
print(HF_KEY)
headers = {"Authorization": f"Bearer {HF_KEY}"}


def generate_dream_image(dream_prompt: str):
    def query(payload):
        response = requests.post(API_URL, headers=headers, json=payload)
        print(response)
        return response.content

    image_bytes = query(
        {
            "inputs": dream_prompt,
        }
    )

    image = Image.open(io.BytesIO(image_bytes))
    return image


# Test
# generate_dream_image(
#     "Last night, I had a dream about an elephant in a church. The elephant was singing a song, possibly an opera piece, and it caught my attention with its unusual gaze fixed upon me. Reflecting upon the dream, I believe the elephant symbolizes my mother. Much like the elephant, my mother is elderly and carries a larger physical presence."
# )
