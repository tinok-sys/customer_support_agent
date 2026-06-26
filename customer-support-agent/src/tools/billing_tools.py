from typing import Optional
from datetime import datetime, timedelta
from src.models import Invoice

_invoices_db: dict[str, Invoice] = {
    "INV-001": Invoice(
        invoice_id="INV-001",
        customer_email="mario.rossi@example.com",
        amount=49.99,
        paid=True,
        description="Abbonamento Premium - Giugno 2026",
    ),
    "INV-002": Invoice(
        invoice_id="INV-002",
        customer_email="mario.rossi@example.com",
        amount=49.99,
        paid=False,
        description="Abbonamento Premium - Luglio 2026",
    ),
    "INV-003": Invoice(
        invoice_id="INV-003",
        customer_email="luca.bianchi@example.com",
        amount=99.99,
        paid=True,
        description="Abbonamento Enterprise - Giugno 2026",
    ),
}


def lookup_invoice(invoice_id: str) -> Optional[Invoice]:
    if invoice_id in _invoices_db:
        return _invoices_db[invoice_id]
    return None


def list_invoices_by_email(email: str) -> list[Invoice]:
    return [inv for inv in _invoices_db.values() if inv.customer_email == email]


def process_refund(invoice_id: str, reason: str) -> dict:
    invoice = lookup_invoice(invoice_id)
    if not invoice:
        return {"success": False, "message": f"Fattura {invoice_id} non trovata."}
    if not invoice.paid:
        return {"success": False, "message": "La fattura non è stata pagata. Nessun rimborso da elaborare."}

    return {
        "success": True,
        "message": f"Rimborso per {invoice_id} ({invoice.amount} {invoice.currency}) approvato. "
        f"Motivo: {reason}. Accreditato in 5-10 giorni lavorativi.",
        "refund_amount": invoice.amount,
        "estimated_days": "5-10",
    }


def get_subscription_status(email: str) -> dict:
    invoices = list_invoices_by_email(email)
    if not invoices:
        return {"active": False, "message": "Nessuna sottoscrizione trovata per questa email."}

    has_unpaid = any(not inv.paid for inv in invoices)
    total_paid = sum(inv.amount for inv in invoices if inv.paid)

    return {
        "active": not has_unpaid,
        "total_invoices": len(invoices),
        "unpaid_count": sum(1 for inv in invoices if not inv.paid),
        "total_paid": total_paid,
        "message": "Abbonamento attivo" if not has_unpaid else "Hai fatture in sospeso.",
    }
