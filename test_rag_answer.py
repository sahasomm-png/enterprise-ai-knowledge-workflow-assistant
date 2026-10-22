
from src.rag import retrieve
from src.generator import generate_answer


def main():
    question = "How do I reset my forgotten company password?"

    print("Question:", question)
    print("\nSearching the knowledge base...")

    results = retrieve(question, top_k=3)

    print("Retrieved chunks:", len(results))
    print("\nGenerating answer with Ollama...\n")

    answer = generate_answer(question, results)

    print("ANSWER:")
    print(answer)


if __name__ == "__main__":
    main()
