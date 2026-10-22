
from pathlib import Path

import chromadb
import pymupdf
from sentence_transformers import SentenceTransformer


# ============================================================
# 1. PROJECT PATHS AND CONFIGURATION
# ============================================================

# Automatically find the main project folder.
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Folder containing TXT and PDF knowledge documents.
DOCUMENTS_DIR = PROJECT_ROOT / "data" / "documents"

# Folder used to store the persistent ChromaDB database.
DATABASE_DIR = PROJECT_ROOT / "artifacts" / "chroma_db"

# Create the database folder if it does not exist.
DATABASE_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# 2. LOAD THE EMBEDDING MODEL
# ============================================================

# This model converts text into numerical vectors.
# Similar questions and document passages should have
# similar vectors, allowing semantic search.
print("Loading the embedding model...")

embedding_model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)


# ============================================================
# 3. CONNECT TO CHROMADB
# ============================================================

# Create a persistent ChromaDB client.
chroma_client = chromadb.PersistentClient(
    path=str(DATABASE_DIR)
)

# Reuse the existing collection or create a new one.
collection = chroma_client.get_or_create_collection(
    name="it_knowledge",
    metadata={"hnsw:space": "cosine"},
)


# ============================================================
# 4. SPLIT TEXT INTO SMALLER CHUNKS
# ============================================================

def split_text(
    text: str,
    chunk_size: int = 700,
    overlap: int = 120,
) -> list[str]:
    """
    Split text into overlapping chunks.

    Chunking helps the retrieval system find relevant
    information without searching an entire document at once.
    """

    # Remove unnecessary spaces and line breaks.
    text = " ".join(text.split())

    if not text:
        return []

    if chunk_size <= 0 or overlap < 0 or overlap >= chunk_size:
        raise ValueError(
            "Use a positive chunk size and overlap smaller "
            "than the chunk size."
        )

    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size

        chunks.append(text[start:end])

        if end >= len(text):
            break

        # Move backwards slightly to preserve context.
        start = end - overlap

    return chunks


# ============================================================
# 5. LOAD TXT AND PDF DOCUMENTS
# ============================================================

def load_documents() -> list[dict]:
    """
    Read TXT and PDF documents.

    TXT files:
        Store Markdown section headings as source labels.

    PDF files:
        Store the actual PDF page numbers.
    """

    documents = []

    # Handle a missing documents directory gracefully.
    if not DOCUMENTS_DIR.exists():
        print(
            f"Documents folder not found: {DOCUMENTS_DIR}"
        )
        return documents

    # Process files in a consistent order.
    for file_path in sorted(DOCUMENTS_DIR.iterdir()):

        # Ignore folders and unsupported files.
        if not file_path.is_file():
            continue

        # ----------------------------------------------------
        # Process TXT documents
        # ----------------------------------------------------

        if file_path.suffix.lower() == ".txt":

            text = file_path.read_text(
                encoding="utf-8",
                errors="replace",
            )

            if not text.strip():
                continue

            sections = []

            current_heading = "Introduction"
            current_lines = []

            # Split the document whenever a Markdown heading
            # such as "# VPN Connection" is encountered.
            for line in text.splitlines():

                stripped_line = line.strip()

                if stripped_line.startswith("#"):

                    # Save the previous section.
                    if current_lines:
                        sections.append({
                            "heading": current_heading,
                            "text": "\n".join(
                                current_lines
                            ).strip(),
                        })

                    # Save the new section heading.
                    current_heading = (
                        stripped_line.lstrip("#").strip()
                    )

                    current_lines = []

                else:
                    current_lines.append(line)

            # Save the final section.
            if current_lines:
                sections.append({
                    "heading": current_heading,
                    "text": "\n".join(
                        current_lines
                    ).strip(),
                })

            # Store each section separately.
            for section in sections:

                if not section["text"].strip():
                    continue

                documents.append({
                    "text": (
                        f"Section: {section['heading']}\n"
                        f"{section['text']}"
                    ),
                    "source": file_path.name,
                    "page": section["heading"],
                })

        # ----------------------------------------------------
        # Process PDF documents
        # ----------------------------------------------------

        elif file_path.suffix.lower() == ".pdf":

            with pymupdf.open(file_path) as pdf:

                for page_number, page in enumerate(
                    pdf,
                    start=1,
                ):

                    text = page.get_text()

                    if not text.strip():
                        continue

                    documents.append({
                        "text": text,
                        "source": file_path.name,
                        "page": page_number,
                    })

    return documents


# ============================================================
# 6. INGEST DOCUMENTS INTO CHROMADB
# ============================================================

def ingest_documents() -> int:
    """
    Rebuild the knowledge base using the current documents.

    Old records are removed before the new records are stored.
    This prevents stale chunks from remaining in the database.
    """

    global collection

    print("\nReading knowledge documents...")

    documents = load_documents()

    if not documents:
        print(
            f"No readable TXT or PDF documents found in "
            f"{DOCUMENTS_DIR}"
        )
        return 0

    all_chunks = []
    all_ids = []
    all_metadata = []

    # Create chunks and metadata for each document section
    # or PDF page.
    for document in documents:

        chunks = split_text(document["text"])

        for chunk_number, chunk in enumerate(
            chunks,
            start=1,
        ):

            # Include the section/page label in the ID.
            chunk_id = (
                f"{document['source']}_"
                f"{document['page']}_"
                f"{chunk_number}"
            )

            all_chunks.append(chunk)
            all_ids.append(chunk_id)

            # ChromaDB metadata values must be supported
            # scalar types. Store the label as a string.
            all_metadata.append({
                "source": document["source"],
                "page": str(document["page"]),
            })

    if not all_chunks:
        print("No text chunks were generated.")
        return 0

    print(f"Documents/sections loaded: {len(documents)}")
    print(f"Text chunks generated: {len(all_chunks)}")

    # Generate embeddings before replacing the old database.
    # If embedding generation fails, the existing collection
    # remains available.
    print("\nGenerating embeddings...")

    embeddings = embedding_model.encode(
        all_chunks,
        normalize_embeddings=True,
        show_progress_bar=True,
    ).tolist()

    # Remove the old collection so stale IDs cannot survive.
    try:
        chroma_client.delete_collection(
            name="it_knowledge"
        )
    except Exception:
        # The collection might not exist on the first run.
        pass

    # Create a fresh collection.
    collection = chroma_client.create_collection(
        name="it_knowledge",
        metadata={"hnsw:space": "cosine"},
    )

    # Store the new chunks in batches.
    batch_size = 500

    for start in range(0, len(all_chunks), batch_size):

        end = start + batch_size

        collection.upsert(
            ids=all_ids[start:end],
            documents=all_chunks[start:end],
            embeddings=embeddings[start:end],
            metadatas=all_metadata[start:end],
        )

    print("\nKnowledge base rebuilt successfully.")

    return len(all_chunks)


# ============================================================
# 7. RETRIEVE RELEVANT DOCUMENT CHUNKS
# ============================================================

def retrieve(
    question: str,
    top_k: int = 4,
) -> list[dict]:
    """
    Search the knowledge base for passages relevant to
    a user's question.

    Returns the text, source, section/page label, and
    cosine distance for each retrieved passage.
    """

    # Handle empty questions.
    if not question.strip():
        return []

    if top_k < 1:
        raise ValueError(
            "top_k must be at least 1"
        )

    # Return no results when the knowledge base is empty.
    if collection.count() == 0:
        return []

    # Convert the question into an embedding.
    query_embedding = embedding_model.encode(
        question,
        normalize_embeddings=True,
    ).tolist()

    # Search for the nearest document chunks.
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=min(
            top_k,
            collection.count(),
        ),
        include=[
            "documents",
            "metadatas",
            "distances",
        ],
    )

    matches = []

    for text, metadata, distance in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):

        matches.append({
            "text": text,
            "source": metadata["source"],
            "page": metadata["page"],
            "distance": distance,
        })

    return matches
