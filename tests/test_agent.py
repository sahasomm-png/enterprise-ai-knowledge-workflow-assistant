
import pytest

from src.agent import classify_ticket


def test_vpn_issue():
    ticket = classify_ticket(
        "My VPN is not connecting and I cannot work"
    )

    assert ticket["category"] == "Network / VPN"
    assert ticket["priority"] == "High"
    assert ticket["assigned_team"] == "Network Support"


def test_password_issue():
    ticket = classify_ticket(
        "I forgot my company password"
    )

    assert ticket["category"] == "Account / Access"
    assert ticket["assigned_team"] == "IT Help Desk"


def test_hardware_issue():
    ticket = classify_ticket(
        "My laptop screen is broken"
    )

    assert ticket["category"] == "Hardware"
    assert ticket["assigned_team"] == "Hardware Support"


def test_software_issue():
    ticket = classify_ticket(
        "My application keeps crashing"
    )

    assert ticket["category"] == "Software"
    assert ticket["assigned_team"] == "Software Support"


def test_critical_production_issue():
    ticket = classify_ticket(
        "The production system is down for all employees"
    )

    assert ticket["category"] == "Production / Critical Incident"
    assert ticket["priority"] == "Critical"
    assert ticket["assigned_team"] == "Incident Response Team"


def test_empty_description():
    with pytest.raises(ValueError):
        classify_ticket("   ")
