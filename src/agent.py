
def classify_ticket(description: str) -> dict:
    """Classify an IT ticket and suggest its priority and assigned team."""

    text = description.lower().strip()

    if not text:
        raise ValueError("Ticket description cannot be empty.")

    # Step 1: Classify the issue.
    if any(phrase in text for phrase in [
        "production system",
        "production outage",
        "production down",
        "entire company",
        "all employees",
    ]):
        category = "Production / Critical Incident"

    elif any(word in text for word in [
        "vpn", "network", "wifi", "wi-fi", "internet",
        "router", "connection",
    ]):
        category = "Network / VPN"

    elif any(word in text for word in [
        "password", "login", "account", "access", "sign in",
        "locked out", "forgot password",
    ]):
        category = "Account / Access"

    elif any(word in text for word in [
        "install", "software", "application", "app",
        "crash", "bug", "update",
    ]):
        category = "Software"

    elif any(word in text for word in [
        "laptop", "keyboard", "monitor", "hardware",
        "printer", "mouse", "screen", "battery",
    ]):
        category = "Hardware"

    else:
        category = "Other"

    # Step 2: Suggest priority.
    critical_phrases = [
        "entire company",
        "all employees",
        "production system down",
        "production system is down",
        "production system",
        "production outage",
        "production down",
    ]

    high_phrases = [
        "cannot work",
        "can't work",
        "business stopped",
        "urgent outage",
    ]

    if any(phrase in text for phrase in critical_phrases):
        priority = "Critical"
    elif any(phrase in text for phrase in high_phrases):
        priority = "High"
    else:
        priority = "Normal"

    # Step 3: Assign the responsible team.
    team_mapping = {
        "Production / Critical Incident": "Incident Response Team",
        "Network / VPN": "Network Support",
        "Account / Access": "IT Help Desk",
        "Software": "Software Support",
        "Hardware": "Hardware Support",
        "Other": "General IT Support",
    }

    assigned_team = team_mapping[category]

    # Step 4: Return the classified ticket.
    return {
        "category": category,
        "priority": priority,
        "assigned_team": assigned_team,
        "status": "Pending human approval",
        "description": description.strip(),
    }
