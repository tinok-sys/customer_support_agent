from pydantic import BaseModel, Field
from typing import Optional


class Ticket(BaseModel):
    ticket_id: str
    customer_email: str
    issue_type: str
    description: str
    status: str = "open"
    assigned_agent: Optional[str] = None


class Invoice(BaseModel):
    invoice_id: str
    customer_email: str
    amount: float
    currency: str = "EUR"
    paid: bool = False
    description: str = ""


class KnowledgeArticle(BaseModel):
    id: str
    title: str
    content: str
    category: str
    tags: list[str] = Field(default_factory=list)
