
from src.rag import retrieve


def test_password_question_retrieves_password_guidance():
    results = retrieve(
        "How do I reset my forgotten company password?",
        top_k=3,
    )

    assert results, "No results found for the password question"

    retrieved_text = " ".join(
        result["text"].lower() for result in results
    )

    assert any(
        phrase in retrieved_text
        for phrase in [
            "password reset portal",
            "verify their identity",
            "creating a new password",
        ]
    ), "Retrieved text does not contain password-reset guidance"


def test_vpn_question_retrieves_vpn_guidance():
    results = retrieve(
        "My company VPN is not connecting",
        top_k=3,
    )

    assert results, "No results found for the VPN question"

    retrieved_text = " ".join(
        result["text"].lower() for result in results
    )

    assert any(
        phrase in retrieved_text
        for phrase in [
            "internet connection",
            "vpn application",
            "vpn connection problems",
        ]
    ), "Retrieved text does not contain VPN troubleshooting guidance"


def test_retrieval_results_have_required_fields():
    results = retrieve(
        "How do I reset my forgotten company password?",
        top_k=3,
    )

    assert results, "Retrieval returned no results"

    for result in results:
        assert "text" in result
        assert "source" in result
        assert "distance" in result
        assert isinstance(result["text"], str)
        assert result["text"].strip()
