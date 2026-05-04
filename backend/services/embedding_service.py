from openai import OpenAI
from config import settings

_jina_client = OpenAI(api_key=settings.JINA_API_KEY, base_url="https://api.jina.ai/v1")
EMBED_MODEL = "jina-embeddings-v3"


def embed_texts(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []
    response = _jina_client.embeddings.create(model=EMBED_MODEL, input=texts)
    return [item.embedding for item in sorted(response.data, key=lambda x: x.index)]


def embed_single(text: str) -> list[float]:
    return embed_texts([text])[0]
