from langchain_core.messages import SystemMessage, HumanMessage
from src.tools.billing_tools import lookup_invoice, list_invoices_by_email, process_refund, get_subscription_status
from src.tools.knowledge_base import search_knowledge_base
from src.tools.ticketing import create_ticket


BILLING_PROMPT = """Sei un agente specializzato in fatturazione e pagamenti. Rispondi in modo professionale e in italiano.

Hai a disposizione questi strumenti:
1. lookup_invoice(invoice_id) - cerca una fattura
2. list_invoices_by_email(email) - elenca le fatture di un cliente
3. process_refund(invoice_id, reason) - elabora un rimborso
4. get_subscription_status(email) - stato dell'abbonamento
5. search_knowledge_base(query, category) - cerca nella knowledge base (usa categoria "billing")
6. create_ticket(email, issue_type, description) - crea un ticket di supporto

Se non puoi risolvere il problema, proponi la creazione di un ticket."""


def create_billing_agent(llm):
    def handle_request(user_input: str, email: str = "") -> dict:
        kb_results = search_knowledge_base(user_input, category="billing")

        messages = [
            SystemMessage(content=BILLING_PROMPT),
            HumanMessage(content=f"Richiesta: {user_input}\nEmail cliente: {email or 'non fornita'}"),
        ]

        response = llm.invoke(messages)

        result = {
            "response": response.content,
            "ticket_created": False,
            "articles_found": len(kb_results),
            "agent_type": "billing",
        }

        if "ticket" in response.content.lower():
            ticket = create_ticket(
                customer_email=email or "unknown@example.com",
                issue_type="billing",
                description=user_input,
            )
            result["ticket_created"] = True
            result["ticket_id"] = ticket.ticket_id

        if kb_results:
            result["suggested_article"] = kb_results[0].title

        return result

    return handle_request
