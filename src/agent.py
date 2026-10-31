
def classify_ticket(description: str) -> dict:
    """Classify an IT ticket and explain its priority and routing decisions."""

    text = description.lower().strip()

    if not text:
        raise ValueError("Ticket description cannot be empty.")

    # Step 1: Classify the issue and explain the category.
    if any(phrase in text for phrase in [
        "production system",
        "production outage",
        "production down",
        "entire company",
        "all employees",
    ]):
        category = "Production / Critical Incident"
        category_reason = (
            "The description mentions a production incident "
            "or a company-wide problem."
        )

    elif any(word in text for word in [
        "vpn", "network", "wifi", "wi-fi", "internet",
        "router", "connection",
    ]):
        category = "Network / VPN"
        category_reason = (
            "The description contains a network or VPN-related keyword."
        )

    elif any(word in text for word in [
        "password", "login", "account", "access", "sign in",
        "locked out", "forgot password",
    ]):
        category = "Account / Access"
        category_reason = (
            "The description contains an account, login, or password-related keyword."
        )

    elif any(word in text for word in [
        "install", "software", "application", "app",
        "crash", "bug", "update",
    ]):
        category = "Software"
        category_reason = (
            "The description contains a software-related keyword."
        )

    elif any(word in text for word in [
        "laptop", "keyboard", "monitor", "hardware",
        "printer", "mouse", "screen", "battery",
    ]):
        category = "Hardware"
        category_reason = (
            "The description contains a hardware-related keyword."
        )

    else:
        category = "Other"
        category_reason = (
            "No matching keyword rule was found, so the issue was categorized as Other."
        )

    # Step 2: Suggest priority and explain the decision.
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
        priority_reason = (
            "The description matches a critical-incident rule."
        )

    elif any(phrase in text for phrase in high_phrases):
        priority = "High"
        priority_reason = (
            "The description indicates that work is blocked or there is an urgent outage."
        )

    else:
        priority = "Normal"
        priority_reason = (
            "No critical or high-priority phrase was detected by the current rules."
        )

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

    # Step 4: Explain the team assignment.
    routing_reason = (
        f"The '{category}' category is mapped to the "
        f"'{assigned_team}' team."
    )

    # Step 5: Return the classified ticket and explanations.
    return {
        "category": category,
        "category_reason": category_reason,
        "priority": priority,
        "priority_reason": priority_reason,
        "assigned_team": assigned_team,
        "routing_reason": routing_reason,
        "status": "Pending human approval",
        "description": description.strip(),
    }
