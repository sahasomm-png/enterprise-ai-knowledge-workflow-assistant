
from src.workflow import create_ticket_draft
from src.database import get_ticket_by_id


def test_workflow_creates_ticket():
    description = "My VPN is not connecting and I cannot work"

    ticket = create_ticket_draft(description)

    assert ticket["description"] == description
    assert ticket["category"] == "Network / VPN"
    assert ticket["priority"] == "High"
    assert ticket["assigned_team"] == "Network Support"
    assert ticket["status"] == "Pending human approval"
    assert ticket["suggested_response"].strip()


def test_workflow_saves_ticket_to_database():
    description = "My VPN is not connecting and I cannot work"

    ticket = create_ticket_draft(description)

    saved_ticket = get_ticket_by_id(ticket["id"])

    assert saved_ticket is not None
    assert saved_ticket["description"] == description
    assert saved_ticket["category"] == "Network / VPN"
    assert saved_ticket["assigned_team"] == "Network Support"
    assert saved_ticket["status"] == "Pending human approval"


def test_workflow_rejects_empty_description():
    import pytest

    with pytest.raises(ValueError):
        create_ticket_draft("   ")



def test_unsupported_question_does_not_invent_an_answer():
    """An unsupported question should not receive an invented policy."""

    result = create_ticket_draft(
        "How many annual leave days do employees receive?"
    )

    response = result["suggested_response"].lower()

    assert (
        "couldn't find" in response
        or "not find" in response
        or "not available" in response
        or "not provided" in response
    ), f"Expected an uncertainty message, received: {response}"

    assert result["status"] == "Pending human approval"
