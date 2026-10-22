
import src.rag as rag


def main():
    print("\n=== Enterprise AI Assistant: Document Ingestion ===")

    number_of_chunks = rag.ingest_documents()

    # Read the collection from the module after ingestion.
    # Ingestion may have recreated the collection.
    current_collection = rag.collection

    print(f"\nChunks processed: {number_of_chunks}")
    print(
        f"Total chunks in ChromaDB: "
        f"{current_collection.count()}"
    )

    if current_collection.count() > 0:
        print("SUCCESS: Your knowledge base is ready!")
    else:
        print("No chunks were stored. Check your documents folder.")


if __name__ == "__main__":
    main()
