
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

def test_normal_priority_for_routine_request():
    ticket = classify_ticket(
        "I need to install a new application"
    )

    assert ticket["category"] == "Software"
    assert ticket["priority"] == "Normal"
    assert ticket["assigned_team"] == "Software Support"


def test_high_priority_for_unusable_laptop():
    ticket = classify_ticket(
        "My laptop is completely unusable and I cannot work"
    )

    assert ticket["category"] == "Hardware"
    assert ticket["priority"] == "High"
    assert ticket["assigned_team"] == "Hardware Support"


def test_critical_priority_for_company_wide_outage():
    ticket = classify_ticket(
        "The network is down for the entire company"
    )

    assert ticket["category"] == "Production / Critical Incident"
    assert ticket["priority"] == "Critical"
    assert ticket["assigned_team"] == "Incident Response Team"


def test_company_wide_network_outage():
    ticket = classify_ticket(
        "The internet is unavailable for all employees"
    )

    assert ticket["category"] == "Production / Critical Incident"
    assert ticket["priority"] == "Critical"
    assert ticket["assigned_team"] == "Incident Response Team"   

def test_routine_vpn_issue_has_normal_priority():
    ticket = classify_ticket(
        "I have a question about configuring my VPN"
    )

    assert ticket["category"] == "Network / VPN"
    assert ticket["priority"] == "Normal"
    assert ticket["assigned_team"] == "Network Support"


def test_vpn_issue_preventing_work_has_high_priority():
    ticket = classify_ticket(
        "My VPN is disconnected and I cannot work"
    )

    assert ticket["category"] == "Network / VPN"
    assert ticket["priority"] == "High"
    assert ticket["assigned_team"] == "Network Support" 

def test_laptop_cannot_connect_to_company_network():
    ticket = classify_ticket(
        "My laptop cannot connect to the company network, and I cannot work"
    )

    assert ticket["category"] == "Network / VPN"
    assert ticket["priority"] == "High"
    assert ticket["assigned_team"] == "Network Support"       