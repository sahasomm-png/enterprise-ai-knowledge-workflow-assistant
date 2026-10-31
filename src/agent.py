def classify_ticket(description: str) -> dict:
    """
    Classify an IT support ticket, recommend its priority,
    assign a responsible team, and explain each decision.
    """

    text = description.lower().strip()

    if not text:
        raise ValueError("Ticket description cannot be empty.")

    # --------------------------------------------------
    # STEP 1: DEFINE CATEGORY KEYWORDS
    # --------------------------------------------------

    production_phrases = [
        "production server down",
        "production server is down",
        "production system down",
        "production system is down",
        "production outage",
        "production down",
        "production system",
        "entire company",
        "all employees",
        "company-wide outage",
        "company wide outage",
    ]

    network_keywords = [
        "vpn",
        "network",
        "wifi",
        "wi-fi",
        "internet",
        "router",
        "connection",
        "connectivity",
        "dns",
    ]

    account_keywords = [
        "password",
        "login",
        "account",
        "access",
        "sign in",
        "sign-in",
        "locked out",
        "forgot password",
        "authentication",
    ]

    software_keywords = [
        "install",
        "software",
        "application",
        "app",
        "crash",
        "bug",
        "update",
        "error message",
        "not responding",
    ]

    hardware_keywords = [
        "laptop",
        "keyboard",
        "monitor",
        "hardware",
        "printer",
        "mouse",
        "screen",
        "battery",
        "overheating",
        "hard drive",
    ]

    # --------------------------------------------------
    # STEP 2: CLASSIFY THE CATEGORY
    # --------------------------------------------------

    if any(phrase in text for phrase in production_phrases):
        category = "Production / Critical Incident"
        category_reason = (
            "The description mentions a production outage, "
            "production system problem, or company-wide incident."
        )

    elif any(keyword in text for keyword in network_keywords):
        category = "Network / VPN"
        category_reason = (
            "The description contains network, connectivity, "
            "internet, or VPN-related terms."
        )

    elif any(keyword in text for keyword in account_keywords):
        category = "Account / Access"
        category_reason = (
            "The description contains account, authentication, "
            "login, access, or password-related terms."
        )

    elif any(keyword in text for keyword in software_keywords):
        category = "Software"
        category_reason = (
            "The description contains software, application, "
            "installation, crash, or bug-related terms."
        )

    elif any(keyword in text for keyword in hardware_keywords):
        category = "Hardware"
        category_reason = (
            "The description contains hardware or physical-device "
            "related terms."
        )

    else:
        category = "Other"
        category_reason = (
            "No matching category rule was found, so the issue "
            "was assigned to the Other category."
        )

    # --------------------------------------------------
    # STEP 3: DETERMINE PRIORITY
    # --------------------------------------------------

    critical_phrases = [
        "production server down",
        "production server is down",
        "production system down",
        "production system is down",
        "production outage",
        "production down",
        "entire company",
        "all employees",
        "company-wide outage",
        "company wide outage",
        "critical outage",
    ]

    high_phrases = [
        "cannot work",
        "can't work",
        "unable to work",
        "work is blocked",
        "business stopped",
        "urgent outage",
        "multiple employees",
        "major outage",
        "completely unavailable",
    ]

    if any(phrase in text for phrase in critical_phrases):
        priority = "Critical"
        priority_reason = (
            "The description matches a production outage, "
            "company-wide incident, or another critical-incident rule."
        )

    elif any(phrase in text for phrase in high_phrases):
        priority = "High"
        priority_reason = (
            "The description indicates blocked work, a major outage, "
            "or an urgent operational problem."
        )

    else:
        priority = "Normal"
        priority_reason = (
            "No critical or high-priority phrase was detected. "
            "A human reviewer should confirm the final priority."
        )

    # --------------------------------------------------
    # STEP 4: ASSIGN THE RESPONSIBLE TEAM
    # --------------------------------------------------

    team_mapping = {
        "Production / Critical Incident": "Incident Response Team",
        "Network / VPN": "Network Support",
        "Account / Access": "IT Help Desk",
        "Software": "Software Support",
        "Hardware": "Hardware Support",
        "Other": "General IT Support",
    }

    assigned_team = team_mapping[category]

    # --------------------------------------------------
    # STEP 5: EXPLAIN THE ROUTING DECISION
    # --------------------------------------------------

    routing_explanations = {
        "Production / Critical Incident": (
            "A production or company-wide incident was detected. "
            "The Incident Response Team is assigned to investigate "
            "and coordinate incident handling."
        ),
        "Network / VPN": (
            "The issue appears related to network connectivity or VPN "
            "access, so Network Support is assigned."
        ),
        "Account / Access": (
            "The issue appears related to login, authentication, "
            "password, or account access, so IT Help Desk is assigned."
        ),
        "Software": (
            "The issue appears related to an application, software "
            "installation, crash, or bug, so Software Support is assigned."
        ),
        "Hardware": (
            "The issue appears related to a physical device or hardware "
            "component, so Hardware Support is assigned."
        ),
        "Other": (
            "The issue did not match a specific routing category, "
            "so General IT Support is assigned for initial review."
        ),
    }

    routing_reason = routing_explanations[category]

    # --------------------------------------------------
    # STEP 6: RETURN THE TICKET
    # --------------------------------------------------

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