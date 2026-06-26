import json
from pathlib import Path
import pytest
from src.models import KnowledgeArticle, Invoice, Ticket
from src.tools.knowledge_base import load_knowledge_base, search_knowledge_base, get_article_by_id
from src.tools.billing_tools import lookup_invoice, list_invoices_by_email, process_refund


class TestKnowledgeBase:
    def test_load_knowledge_base(self):
        articles = load_knowledge_base()
        assert len(articles) > 0
        assert all(isinstance(a, KnowledgeArticle) for a in articles)

    def test_search_found(self):
        results = search_knowledge_base("password")
        assert len(results) > 0
        assert any("password" in r.title.lower() for r in results)

    def test_search_empty(self):
        results = search_knowledge_base("zzzznotexists")
        assert len(results) == 0

    def test_search_by_category(self):
        results = search_knowledge_base("payment", category="billing")
        assert len(results) > 0
        assert all(r.category == "billing" for r in results)

    def test_get_article_by_id(self):
        article = get_article_by_id("KB001")
        assert article is not None
        assert article.title == "How to reset your password"

    def test_get_article_missing(self):
        article = get_article_by_id("NOTEXIST")
        assert article is None

    def test_load_knowledge_file_content(self):
        kb_path = Path("data/knowledge_base.json")
        assert kb_path.exists()
        with open(kb_path, encoding="utf-8") as f:
            data = json.load(f)
        assert len(data) >= 6


class TestBillingTools:
    def test_lookup_invoice_found(self):
        invoice = lookup_invoice("INV-001")
        assert invoice is not None
        assert invoice.amount == 49.99

    def test_lookup_invoice_not_found(self):
        invoice = lookup_invoice("INV-XXX")
        assert invoice is None

    def test_list_invoices_by_email(self):
        invoices = list_invoices_by_email("mario.rossi@example.com")
        assert len(invoices) == 2

    def test_list_invoices_by_email_empty(self):
        invoices = list_invoices_by_email("nobody@example.com")
        assert len(invoices) == 0

    def test_process_refund_not_found(self):
        result = process_refund("INV-XXX", "test")
        assert result["success"] is False

    def test_process_refund_success(self):
        result = process_refund("INV-001", "Cliente insoddisfatto")
        assert result["success"] is True
        assert "Rimborso" in result["message"]

    def test_process_refund_unpaid(self):
        result = process_refund("INV-002", "Richiesto")
        assert result["success"] is False
        assert "non è stata pagata" in result["message"]
