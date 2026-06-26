from datetime import datetime
from typing import Optional
from src.models import Ticket

_tickets_db: dict[str, Ticket] = {}
_ticket_counter = 0


def create_ticket(customer_email: str, issue_type: str, description: str) -> Ticket:
    global _ticket_counter
    _ticket_counter += 1

    ticket = Ticket(
        ticket_id=f"TKT-{_ticket_counter:04d}",
        customer_email=customer_email,
        issue_type=issue_type,
        description=description,
        status="open",
        assigned_agent=None,
    )
    _tickets_db[ticket.ticket_id] = ticket
    return ticket


def get_ticket(ticket_id: str) -> Optional[Ticket]:
    return _tickets_db.get(ticket_id)


def update_ticket_status(ticket_id: str, status: str, agent: str = "") -> Optional[Ticket]:
    ticket = get_ticket(ticket_id)
    if not ticket:
        return None

    ticket.status = status
    if agent:
        ticket.assigned_agent = agent
    return ticket


def list_tickets_by_email(email: str) -> list[Ticket]:
    return [t for t in _tickets_db.values() if t.customer_email == email]


def list_open_tickets() -> list[Ticket]:
    return [t for t in _tickets_db.values() if t.status == "open"]
