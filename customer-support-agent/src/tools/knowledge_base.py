import json
from pathlib import Path
from src.models import KnowledgeArticle


def load_knowledge_base() -> list[KnowledgeArticle]:
    kb_path = Path("data/knowledge_base.json")
    if not kb_path.exists():
        return []

    with open(kb_path, encoding="utf-8") as f:
        articles_data = json.load(f)

    return [KnowledgeArticle(**article) for article in articles_data]


def search_knowledge_base(query: str, category: str = "") -> list[KnowledgeArticle]:
    articles = load_knowledge_base()
    query_lower = query.lower()

    results = []
    for article in articles:
        if category and article.category != category:
            continue

        score = 0
        if query_lower in article.title.lower():
            score += 3
        if query_lower in article.content.lower():
            score += 2
        for tag in article.tags:
            if query_lower in tag.lower():
                score += 1

        if score > 0:
            results.append((score, article))

    results.sort(key=lambda x: x[0], reverse=True)
    return [article for _, article in results]


def get_article_by_id(article_id: str) -> KnowledgeArticle | None:
    articles = load_knowledge_base()
    for article in articles:
        if article.id == article_id:
            return article
    return None


def list_articles_by_category(category: str) -> list[KnowledgeArticle]:
    articles = load_knowledge_base()
    return [a for a in articles if a.category == category]
