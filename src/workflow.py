
from src.agent import classify_ticket
from src.rag import retrieve
from src.generator import generate_answer
from src.database import save_ticket


def create_ticket_draft(description: str) -> dict:
    """Classify, route, enrich, and save a ticket for human review."""

    description = description.strip()

    if not description:
        raise ValueError("Ticket description cannot be empty.")

    # Step 1: Classify the issue and assign its team.
    ticket = classify_ticket(description)

    # Ensure a team assignment is present.
    if not ticket.get("assigned_team"):
        ticket["assigned_team"] = "General IT Support"

    # Step 2: Retrieve relevant knowledge-base documents.
    results = retrieve(description, top_k=3)

    # Step 3: Keep results close to the best retrieval match.
    # Lower ChromaDB distances indicate better matches.
    if results:
        best_distance = results[0]["distance"]

        relevant_results = [
            result
            for result in results
            if result["distance"] <= best_distance + 0.20
        ]
    else:
        relevant_results = []

    # Step 4: Generate a suggested response.
    suggested_response = generate_answer(
        description,
        relevant_results,
    )

    # Step 5: Collect unique sources.
    unique_sources = []
    seen_sources = set()

    for result in relevant_results:
        source_key = (
            result["source"],
            result["page"],
        )

        if source_key not in seen_sources:
            seen_sources.add(source_key)

            unique_sources.append({
                "source": result["source"],
                "page": result["page"],
            })

    # Step 6: Complete the ticket draft.
    ticket["suggested_response"] = suggested_response
    ticket["status"] = "Pending human approval"
    ticket["sources"] = unique_sources

    # Step 7: Save all ticket fields, including assigned_team.
    ticket_id = save_ticket(ticket)

    # Step 8: Include the generated database ID.
    ticket["id"] = ticket_id

    return ticket
