
import requests


# Ollama's local chat API.
OLLAMA_URL = "http://localhost:11434/api/chat"

# Model downloaded to your Mac.
MODEL_NAME = "llama3.2:3b"


def generate_answer(
    question: str,
    retrieved_chunks: list[dict],
) -> str:
    """
    Generate an answer using retrieved documentation.

    Citations must use the source labels supplied by
    retrieval, not page numbers invented by the model.
    """

    # Do not generate an answer without supporting evidence.
    if not retrieved_chunks:
        return (
            "I couldn't find supporting information in the "
            "available IT documentation. Please contact "
            "the IT support team."
        )

    # Prepare the context and an authoritative source list.
    context_parts = []
    source_labels = []

    for chunk in retrieved_chunks:
        source = chunk["source"]
        location = str(chunk["page"])

        source_label = f"{source} — {location}"

        context_parts.append(
            f"SOURCE: {source_label}\n"
            f"CONTENT:\n{chunk['text']}"
        )

        if source_label not in source_labels:
            source_labels.append(source_label)

    context = "\n\n".join(context_parts)

    allowed_sources = "\n".join(
        f"- {label}" for label in source_labels
    )

    # Tell the model to answer only from retrieved evidence.
    prompt = f"""
You are an enterprise IT knowledge assistant.

RULES:
1. Answer using only the supplied documentation.
2. Never invent policies, facts, or troubleshooting steps.
3. If the documentation does not answer the question,
   clearly say that you could not find the answer.
4. Give clear, numbered steps when appropriate.
5. Cite supporting sources using their exact labels from
   the ALLOWED SOURCES list below.
6. Do not invent physical page numbers.
7. Do not change a source's filename or section label.
8. Do not cite a source unless its content supports the answer.
9. Do not include contradictory or unsupported citations.

ALLOWED SOURCES:
{allowed_sources}

RETRIEVED DOCUMENTATION:
{context}

USER QUESTION:
{question}

Write a helpful, concise answer with accurate citations.
"""

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL_NAME,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a careful enterprise IT assistant. "
                        "Use only the supplied evidence and cite "
                        "only the exact source labels provided."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            "stream": False,
            "options": {
                "temperature": 0,
            },
        },
        timeout=180,
    )

    # Raise an error if Ollama returns an unsuccessful response.
    response.raise_for_status()

    return response.json()["message"]["content"].strip()
