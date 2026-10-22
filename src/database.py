
import sqlite3
from pathlib import Path


# Locate the project and SQLite database.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATABASE_PATH = PROJECT_ROOT / "artifacts" / "tickets.db"


# Valid ticket statuses.
ALLOWED_STATUSES = {
    "Pending human approval",
    "Approved",
    "Rejected",
    "In Progress",
    "Resolved",
}


# Default teams for tickets created before team assignment was added.
TEAM_MAPPING = {
    "Production / Critical Incident": "Incident Response Team",
    "Network / VPN": "Network Support",
    "Account / Access": "IT Help Desk",
    "Software": "Software Support",
    "Hardware": "Hardware Support",
    "Other": "General IT Support",
}


def get_connection():
    """Open a connection to the SQLite database."""

    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row

    return connection


def initialize_database():
    """Create the tickets table and safely add missing columns."""

    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS tickets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                description TEXT NOT NULL,
                category TEXT NOT NULL,
                priority TEXT NOT NULL,
                suggested_response TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'Pending human approval',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        # Read the current table structure.
        columns = {
            row["name"]
            for row in connection.execute(
                "PRAGMA table_info(tickets)"
            ).fetchall()
        }

        # Add assigned_team only if it doesn't exist yet.
        if "assigned_team" not in columns:
            connection.execute(
                """
                ALTER TABLE tickets
                ADD COLUMN assigned_team TEXT
                """
            )

        # Fill in team assignments for existing tickets.
        rows = connection.execute(
            """
            SELECT id, category
            FROM tickets
            WHERE assigned_team IS NULL OR assigned_team = ''
            """
        ).fetchall()

        for row in rows:
            team = TEAM_MAPPING.get(
                row["category"],
                "General IT Support",
            )

            connection.execute(
                """
                UPDATE tickets
                SET assigned_team = ?
                WHERE id = ?
                """,
                (team, row["id"]),
            )


def save_ticket(ticket: dict) -> int:
    """Save a ticket and return its database ID."""

    initialize_database()

    assigned_team = ticket.get("assigned_team")

    if not assigned_team:
        assigned_team = TEAM_MAPPING.get(
            ticket.get("category", "Other"),
            "General IT Support",
        )

    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO tickets (
                description,
                category,
                priority,
                suggested_response,
                status,
                assigned_team
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                ticket["description"],
                ticket["category"],
                ticket["priority"],
                ticket["suggested_response"],
                ticket.get("status", "Pending human approval"),
                assigned_team,
            ),
        )

        return cursor.lastrowid


def get_all_tickets() -> list[dict]:
    """Return all saved tickets, newest first."""

    initialize_database()

    with get_connection() as connection:
        rows = connection.execute(
            "SELECT * FROM tickets ORDER BY id DESC"
        ).fetchall()

        return [dict(row) for row in rows]


def get_ticket_by_id(ticket_id: int) -> dict | None:
    """Retrieve a ticket by its ID."""

    initialize_database()

    with get_connection() as connection:
        row = connection.execute(
            "SELECT * FROM tickets WHERE id = ?",
            (ticket_id,),
        ).fetchone()

        return dict(row) if row else None


def update_ticket_status(ticket_id: int, new_status: str) -> bool:
    """Update a ticket's status."""

    if new_status not in ALLOWED_STATUSES:
        raise ValueError(
            f"Invalid status: {new_status}. "
            f"Allowed statuses: {', '.join(sorted(ALLOWED_STATUSES))}"
        )

    with get_connection() as connection:
        cursor = connection.execute(
            """
            UPDATE tickets
            SET status = ?
            WHERE id = ?
            """,
            (new_status, ticket_id),
        )

        return cursor.rowcount > 0
