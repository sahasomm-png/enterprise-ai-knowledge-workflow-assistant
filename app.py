
import streamlit as st
import pandas as pd

from src.workflow import create_ticket_draft
from src.rag import retrieve
from src.generator import generate_answer
from src.database import (
    initialize_database,
    get_all_tickets,
    get_ticket_by_id,
    update_ticket_status,
)

# ==================================================
# PAGE CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="Enterprise AI Knowledge & Workflow Assistant",
    page_icon="🤖",
    layout="wide",
)

initialize_database()

st.title("🤖 Enterprise AI Knowledge & Workflow Assistant")
st.caption(
    "AI-powered company knowledge search, IT ticket classification, "
    "team assignment, and workflow management."
)

PENDING = "Pending human approval"

STATUS_OPTIONS = [
    PENDING,
    "Approved",
    "Rejected",
    "In Progress",
    "Resolved",
]


# ==================================================
# HELPER FUNCTIONS
# ==================================================

def safe_value(value, default="Not available"):
    """Return a fallback for missing or empty values."""
    if value is None or value == "":
        return default
    return value


def show_ticket_summary(ticket):
    """Display ticket category, priority, team, and status."""
    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Category",
        safe_value(ticket.get("category"), "Unknown"),
    )
    col2.metric(
        "Priority",
        safe_value(ticket.get("priority"), "Unknown"),
    )
    col3.metric(
        "Assigned Team",
        safe_value(ticket.get("assigned_team"), "Unassigned"),
    )
    col4.metric(
        "Status",
        safe_value(ticket.get("status"), PENDING),
    )


def show_sources(sources):
    """Display source documents when available."""
    if not sources:
        st.caption("No document sources available.")
        return

    st.markdown("**Knowledge-base sources**")

    for source in sources:
        source_name = source.get("source", "Unknown source")
        page = source.get("page")

        if page is not None:
            st.write(f"- {source_name} — page {page}")
        else:
            st.write(f"- {source_name}")


def get_ticket_label(ticket):
    """Build a readable ticket selection label."""
    ticket_id = ticket.get("id", "?")
    description = ticket.get("description", "")
    description = description[:65]

    return f"Ticket #{ticket_id} — {description}"


# ==================================================
# APPLICATION TABS
# ==================================================

knowledge_tab, create_tab, manage_tab = st.tabs(
    [
        "📚 Knowledge Assistant",
        "🎫 Create Support Ticket",
        "🗂️ Ticket Management",
    ]
)


# ==================================================
# TAB 1: KNOWLEDGE ASSISTANT
# ==================================================

with knowledge_tab:
    st.header("📚 Company Knowledge Assistant")

    st.write(
        "Ask questions about your company documents. "
        "The system retrieves relevant information and generates "
        "an answer using your local language model."
    )

    with st.form("knowledge_question_form"):
        question = st.text_area(
            "Enter your question",
            placeholder=(
                "Example: How do I reset my forgotten company password?"
            ),
            height=100,
        )

        ask_button = st.form_submit_button(
            "Ask Assistant",
            type="primary",
        )

    if ask_button:
        if not question.strip():
            st.warning("Please enter a question.")
        else:
            try:
                with st.spinner(
                    "Searching documents and generating an answer..."
                ):
                    results = retrieve(question.strip(), top_k=3)

                    # Keep results close to the best retrieval match.
                    if results:
                        best_distance = results[0]["distance"]

                        relevant_results = [
                            result
                            for result in results
                            if result["distance"]
                            <= best_distance + 0.20
                        ]
                    else:
                        relevant_results = []

                    answer = generate_answer(
                        question.strip(),
                        relevant_results,
                    )

                st.subheader("Answer")
                st.write(answer)

                st.divider()
                show_sources(relevant_results)

            except Exception as error:
                st.error(
                    "The assistant could not complete your question. "
                    "Check that the knowledge base is ready and Ollama "
                    "is running."
                )
                st.exception(error)


# ==================================================
# TAB 2: CREATE SUPPORT TICKET
# ==================================================

with create_tab:
    st.header("🎫 Create an IT Support Ticket")

    st.write(
        "Describe an IT issue. The system will classify it, suggest "
        "a priority, assign a support team, retrieve relevant "
        "documentation, and draft a response for human review."
    )

    with st.form("create_ticket_form"):
        description = st.text_area(
            "Describe your issue",
            placeholder=(
                "Example: My VPN is not connecting and I cannot work."
            ),
            height=130,
        )

        create_button = st.form_submit_button(
            "Create Ticket",
            type="primary",
        )

    if create_button:
        if not description.strip():
            st.warning(
                "Please describe the issue before creating a ticket."
            )
        else:
            try:
                with st.spinner(
                    "Classifying the issue, preparing a response, "
                    "and saving the ticket..."
                ):
                    ticket = create_ticket_draft(description.strip())

                st.success(
                    f"Ticket #{ticket['id']} created successfully."
                )

                st.subheader("Ticket Summary")
                show_ticket_summary(ticket)

                st.markdown("### Issue Description")
                st.write(ticket.get("description", description))

                st.markdown("### AI-Suggested Response")
                st.write(
                    safe_value(
                        ticket.get("suggested_response"),
                        "No suggested response was generated.",
                    )
                )

                show_sources(ticket.get("sources", []))

                st.info(
                    "The suggested response is a draft. A human reviewer "
                    "should verify it before it is sent to an employee."
                )

            except Exception as error:
                st.error(
                    "Ticket creation failed. Check the terminal for "
                    "additional details."
                )
                st.exception(error)


# ==================================================
# TAB 3: TICKET MANAGEMENT
# ==================================================

with manage_tab:
    st.header("🗂️ Ticket Management")

    if st.button("🔄 Refresh Tickets"):
        st.rerun()

    tickets = get_all_tickets()

    if not tickets:
        st.info(
            "No tickets have been created yet. "
            "Create one using the Create Support Ticket tab."
        )

    else:
        # --------------------------------------------------
        # SUMMARY METRICS
        # --------------------------------------------------

        total_tickets = len(tickets)

        pending_count = sum(
            ticket.get("status") == PENDING
            for ticket in tickets
        )

        in_progress_count = sum(
            ticket.get("status") == "In Progress"
            for ticket in tickets
        )

        resolved_count = sum(
            ticket.get("status") == "Resolved"
            for ticket in tickets
        )

        metric1, metric2, metric3, metric4 = st.columns(4)

        metric1.metric("Total Tickets", total_tickets)
        metric2.metric("Awaiting Review", pending_count)
        metric3.metric("In Progress", in_progress_count)
        metric4.metric("Resolved", resolved_count)

        st.divider()

        # --------------------------------------------------
        # SEARCH AND FILTERS
        # --------------------------------------------------

        st.subheader("Search and Filter Tickets")

        filter1, filter2, filter3 = st.columns(3)

        with filter1:
            search_text = st.text_input(
                "Search tickets",
                placeholder="Search description, ID, or team",
            )

        with filter2:
            selected_status = st.selectbox(
                "Filter by status",
                ["All"] + STATUS_OPTIONS,
            )

        with filter3:
            available_priorities = sorted(
                {
                    str(ticket.get("priority", "Unknown"))
                    for ticket in tickets
                }
            )

            selected_priority = st.selectbox(
                "Filter by priority",
                ["All"] + available_priorities,
            )

        filtered_tickets = []

        for ticket in tickets:
            search_content = " ".join(
                [
                    str(ticket.get("id", "")),
                    str(ticket.get("description", "")),
                    str(ticket.get("category", "")),
                    str(ticket.get("assigned_team", "")),
                    str(ticket.get("priority", "")),
                    str(ticket.get("status", "")),
                ]
            ).lower()

            if (
                search_text.strip()
                and search_text.strip().lower() not in search_content
            ):
                continue

            if (
                selected_status != "All"
                and ticket.get("status") != selected_status
            ):
                continue

            if (
                selected_priority != "All"
                and ticket.get("priority") != selected_priority
            ):
                continue

            filtered_tickets.append(ticket)

        st.caption(
            f"Showing {len(filtered_tickets)} matching ticket(s)."
        )

        # --------------------------------------------------
        # TICKET TABLE
        # --------------------------------------------------

        st.subheader("All Tickets")

        if filtered_tickets:
            table_rows = [
                {
                    "Ticket ID": ticket.get("id"),
                    "Description": ticket.get("description", ""),
                    "Category": ticket.get("category", "Unknown"),
                    "Priority": ticket.get("priority", "Unknown"),
                    "Assigned Team": ticket.get(
                        "assigned_team",
                        "Unassigned",
                    ),
                    "Status": ticket.get("status", "Unknown"),
                    "Created At": ticket.get("created_at", ""),
                }
                for ticket in filtered_tickets
            ]

            st.dataframe(
                pd.DataFrame(table_rows),
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info(
                "No tickets match the selected search and filters."
            )

        # --------------------------------------------------
        # INDIVIDUAL TICKET REVIEW
        # --------------------------------------------------

        st.divider()
        st.subheader("Review an Individual Ticket")

        if not filtered_tickets:
            st.info(
                "Clear or change your filters to select a ticket."
            )

        else:
            ticket_by_id = {
                ticket["id"]: ticket
                for ticket in filtered_tickets
            }

            selected_ticket_id = st.selectbox(
                "Select a ticket",
                options=list(ticket_by_id.keys()),
                format_func=lambda ticket_id: get_ticket_label(
                    ticket_by_id[ticket_id]
                ),
            )

            selected_ticket = get_ticket_by_id(selected_ticket_id)

            if selected_ticket:
                st.markdown(
                    f"### Ticket #{selected_ticket['id']}"
                )

                show_ticket_summary(selected_ticket)

                st.markdown("**Description**")
                st.write(
                    selected_ticket.get("description", "")
                )

                st.markdown("**Assigned Team**")
                st.write(
                    safe_value(
                        selected_ticket.get("assigned_team"),
                        "Unassigned",
                    )
                )

                st.markdown("**AI-Suggested Response**")
                st.write(
                    safe_value(
                        selected_ticket.get("suggested_response"),
                        "No suggested response available.",
                    )
                )

                st.markdown("**Created At**")
                st.write(
                    safe_value(selected_ticket.get("created_at"))
                )

                st.divider()
                st.markdown("### Human Review")

                current_status = selected_ticket.get(
                    "status",
                    PENDING,
                )

                st.write(f"Current status: **{current_status}**")

                # --------------------------------------------------
                # APPROVE OR REJECT A PENDING RESPONSE
                # --------------------------------------------------

                if current_status == PENDING:
                    approve_col, reject_col = st.columns(2)

                    with approve_col:
                        if st.button(
                            "✅ Approve Response",
                            key=f"approve_{selected_ticket_id}",
                            type="primary",
                        ):
                            update_ticket_status(
                                selected_ticket_id,
                                "Approved",
                            )

                            st.success(
                                f"Ticket #{selected_ticket_id} approved."
                            )
                            st.rerun()

                    with reject_col:
                        if st.button(
                            "❌ Reject Response",
                            key=f"reject_{selected_ticket_id}",
                        ):
                            update_ticket_status(
                                selected_ticket_id,
                                "Rejected",
                            )

                            st.warning(
                                f"Ticket #{selected_ticket_id} rejected."
                            )
                            st.rerun()

                # --------------------------------------------------
                # UPDATE STATUS
                # --------------------------------------------------

                st.markdown("### Update Ticket Status")

                status_index = (
                    STATUS_OPTIONS.index(current_status)
                    if current_status in STATUS_OPTIONS
                    else 0
                )

                new_status = st.selectbox(
                    "Choose a status",
                    options=STATUS_OPTIONS,
                    index=status_index,
                    key=f"new_status_{selected_ticket_id}",
                )

                if st.button(
                    "Update Status",
                    key=f"update_status_{selected_ticket_id}",
                ):
                    if new_status == current_status:
                        st.info(
                            "The ticket already has that status."
                        )
                    else:
                        try:
                            updated = update_ticket_status(
                                selected_ticket_id,
                                new_status,
                            )

                            if updated:
                                st.success(
                                    f"Ticket #{selected_ticket_id} "
                                    f"updated to {new_status}."
                                )
                                st.rerun()
                            else:
                                st.error(
                                    "Ticket not found. Refresh and try again."
                                )

                        except Exception as error:
                            st.error(
                                "Could not update the ticket status."
                            )
                            st.exception(error)

                st.caption(
                    "Approval records the review decision in the database. "
                    "This demo does not automatically send emails or "
                    "notify the assigned team."
                )


# ==================================================
# FOOTER
# ==================================================

st.divider()

st.caption(
    "Enterprise AI Knowledge & Workflow Assistant | "
    "RAG + Ollama + ChromaDB + SQLite | Human review required"
)
