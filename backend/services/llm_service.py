from langsmith import traceable
from openai import OpenAI
from config import settings

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=settings.OPENROUTER_API_KEY,
)

SYSTEM_PROMPT = "You are a helpful AI assistant. Answer questions clearly and concisely."
MODEL = "nvidia/nemotron-3-super-120b-a12b:free"


@traceable(name="openrouter_chat", run_type="llm")
def stream_chat(history: list[dict], metadata: dict | None = None) -> list[str]:
    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + history
    deltas = []
    with client.chat.completions.create(
        model=MODEL,
        messages=messages,
        stream=True,
    ) as stream:
        for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                deltas.append(delta)
    return deltas
