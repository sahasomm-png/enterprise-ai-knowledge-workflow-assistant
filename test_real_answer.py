
from src.rag import retrieve
from src.generator import generate_answer


question = "How do I reset my forgotten company password?"

print("\nQUESTION:")
print(question)

print("\nRETRIEVING DOCUMENTATION...")
chunks = retrieve(question, top_k=3)

print(f"Retrieved chunks: {len(chunks)}")

if not chunks:
    print("No documentation retrieved. Check your knowledge base.")
else:
    print("\nGENERATING REAL AI ANSWER...")
    answer = generate_answer(question, chunks)

    print("\nAI ANSWER:")
    print(answer)

    answer_lower = answer.lower()

    print("\nBASIC QUALITY CHECKS:")
    print(
        "Mentions password reset portal:",
        "password reset portal" in answer_lower,
    )
    print(
        "Mentions identity verification:",
        "verify your identity" in answer_lower
        or "verify their identity" in answer_lower
        or "identity" in answer_lower,
    )
    print(
        "Includes a source reference:",
        "it_support_guide.txt" in answer_lower,
    )
