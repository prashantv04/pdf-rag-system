import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI


PROJECT_ROOT = Path(__file__).resolve().parent.parent

load_dotenv(PROJECT_ROOT / ".env")

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

print("API key loaded:", bool(OPENROUTER_API_KEY))

if not OPENROUTER_API_KEY:
    raise RuntimeError(
        "OPENROUTER_API_KEY is not set. "
        "Please add it to your .env file."
    )


client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
    timeout=90.0,
)


# MODEL_NAME = "openrouter/free"
MODEL_NAME = "google/gemma-4-26b-a4b-it:free"


def generate_answer(
    question: str,
    context: str,
) -> str:
    prompt = f"""
    You are a question-answering assistant for a PDF document.

    You MUST answer the question using ONLY the provided context.

    IMPORTANT RULES:

    - Answer ONLY from the provided DOCUMENT CONTEXT.

    - Check the Opinion type (Majority, Dissenting, or Concurring) for each source in the DOCUMENT CONTEXT.

    - The 'Majority' opinion represents the binding legal ruling.

    - If any fact, viewpoint, or rationale comes from a 'Dissenting' or 'Concurring' opinion, you MUST explicitly identify it as such (e.g., "According to a dissenting opinion..." or "In a concurring judgment...").

    - Never present a dissenting argument as the prevailing court holding or final rule of law.

    - Every factual statement in your answer must be supported by the DOCUMENT CONTEXT.

    - Do not use outside knowledge, even if you know the answer.

    - Do not infer or assume facts that are not explicitly supported by the context.

    - Do not combine unrelated statements into a new conclusion.

    - If the context does not provide enough information to answer a part of the question, do not answer that part.

    - If the context does not support the answer at all, respond exactly:

      The information is not available in the supplied documents.

    - Do not fabricate facts, dates, legal conclusions, case holdings, or procedural details.

    - Do not mention information that appears only in your general knowledge.

    - Keep the answer concise.

    - Use short paragraphs or bullet points when appropriate.

    - Do not include citations or source information in the answer.

    - The application handles sources separately.

    - Return only the final answer.


    Before answering, check each factual statement against the supplied context.
    Remove any statement that is not supported by the context.

    DOCUMENT CONTEXT:
    {context}

    USER QUESTION:
    {question}
    """
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": (
                    "Answer strictly from the supplied document context. "
                    "Preserve the exact meaning and direction of every "
                    "statement. Never reverse subject and object."
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        temperature=0,
    )

    answer = response.choices[0].message.content

    if not answer:
        return (
            "The information is not available in the supplied documents."
        )

    return answer.strip()