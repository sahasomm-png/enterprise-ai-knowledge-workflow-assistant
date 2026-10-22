
from src.database import (
    initialize_database,
    save_ticket,
    get_all_tickets,
    get_ticket_by_id,
    update_ticket_status,
)


def test_database_initializes():
    initialize_database()


def test_save_and_retrieve_ticket():
    ticket = {
        "description": "Automated database test: VPN issue",
        "category": "Network / VPN",
        "priority": "High",
        "suggested_response": "Contact Network Support.",
        "status": "Pending human approval",
        "assigned_team": "Network Support",
    }

    ticket_id = save_ticket(ticket)

    saved_ticket = get_ticket_by_id(ticket_id)

    assert saved_ticket is not None
    assert saved_ticket["description"] == ticket["description"]
    assert saved_ticket["category"] == "Network / VPN"
    assert saved_ticket["priority"] == "High"
    assert saved_ticket["assigned_team"] == "Network Support"


def test_ticket_appears_in_all_tickets():
    tickets = get_all_tickets()

    assert isinstance(tickets, list)


def test_update_ticket_status():
    ticket = {
        "description": "Automated status update test",
        "category": "Software",
        "priority": "Normal",
        "suggested_response": "Contact Software Support.",
        "status": "Pending human approval",
        "assigned_team": "Software Support",
    }

    ticket_id = save_ticket(ticket)

    updated = update_ticket_status(ticket_id, "In Progress")

    assert updated is True

    saved_ticket = get_ticket_by_id(ticket_id)
    assert saved_ticket["status"] == "In Progress"
