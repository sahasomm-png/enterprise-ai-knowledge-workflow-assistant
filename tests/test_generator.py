
from unittest.mock import patch

from src.generator import generate_answer


def test_no_retrieved_chunks_returns_fallback():
    """Return a safe message when no evidence is available."""

    answer = generate_answer(
        question="How do I reset my password?",
        retrieved_chunks=[],
    )

    assert "couldn't find supporting information" in answer.lower()
    assert "IT support team" in answer


@patch("src.generator.requests.post")
def test_password_answer_uses_documentation(mock_post):
    """Check that the generated answer follows password guidance."""

    mock_post.return_value.json.return_value = {
        "message": {
            "content": (
                "1. Use the official password reset portal.\n"
                "2. Verify your identity before creating a new password.\n"
                "Source: IT_Support_Guide.txt — 1"
            )
        }
    }
    mock_post.return_value.raise_for_status.return_value = None

    chunks = [
        {
            "source": "IT_Support_Guide.txt",
            "page": 1,
            "text": (
                "Employees should use the official password reset "
                "portal. They must verify their identity before "
                "creating a new password."
            ),
        }
    ]

    answer = generate_answer(
        question="How do I reset my forgotten password?",
        retrieved_chunks=chunks,
    )

    assert "password reset portal" in answer.lower()
    assert "verify your identity" in answer.lower()
    mock_post.assert_called_once()


def test_empty_evidence_does_not_call_ollama():
    """Do not call the LLM when no evidence is retrieved."""

    with patch("src.generator.requests.post") as mock_post:
        generate_answer(
            question="What is my company's leave policy?",
            retrieved_chunks=[],
        )

    mock_post.assert_not_called()
