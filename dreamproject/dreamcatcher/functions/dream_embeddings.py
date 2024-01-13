import pinecone
import openai
from dotenv import load_dotenv
import os

load_dotenv()
openai.api_key = str(os.getenv('OPENAI_KEY'))
# get API key from top-right dropdown on OpenAI website

MODEL = "text-embedding-ada-002"
PINECONE_INDEX = "dreams"

pinecone.init(
    api_key=str(os.getenv('PINECONE_KEY')), environment="gcp-starter"
)
index = pinecone.Index(PINECONE_INDEX)


def get_dream_embedding(dream_str):
    return openai.Embedding.create(
        input=[dream_str], engine=MODEL)['data'][0]['embedding']


def embed_and_store_dream(dream_id, dream_str):
    embedding = get_dream_embedding(dream_str)
    index.upsert(vectors=[{
        "id": dream_id, "values": embedding
    }])


def get_similar_dream_ids(dream_id, k):
    res = index.fetch(ids=[dream_id])
    embedding = res["vectors"][dream_id]["values"]

    res = index.query(
        top_k=k+1,  # we will remove one element (ourself)
        vector=embedding,
    )

    ids = [match["id"] for match in res["matches"] if match["id"] != dream_id]

    return ids
