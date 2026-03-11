from datetime import datetime

import httpx

from app.schemas import ConceptCard, ResearchPaper

CROSSREF_ENDPOINT = "https://api.crossref.org/works"


def fetch_research_papers(topic: str, limit: int = 5) -> list[ResearchPaper]:
    params = {"query": topic, "rows": limit, "sort": "relevance"}
    with httpx.Client(timeout=15) as client:
        response = client.get(CROSSREF_ENDPOINT, params=params)
        response.raise_for_status()
        payload = response.json()

    papers: list[ResearchPaper] = []
    for item in payload.get("message", {}).get("items", [])[:limit]:
        title = (item.get("title") or ["Untitled"])[0]
        authors = ", ".join(
            f"{a.get('given', '').strip()} {a.get('family', '').strip()}".strip()
            for a in item.get("author", [])
        ) or "Unknown"
        doi = item.get("DOI")
        papers.append(
            ResearchPaper(
                title=title,
                authors=authors,
                abstract=item.get("abstract"),
                doi=doi,
                link=f"https://doi.org/{doi}" if doi else item.get("URL"),
            )
        )
    return papers


def daily_concept() -> ConceptCard:
    finance = ["Monte Carlo Simulation", "Duration Risk", "Sharpe Ratio", "Yield Curve"]
    sustainability = ["Systems Thinking", "Circular Economy", "Carbon Accounting", "TCFD Disclosure"]
    day = datetime.utcnow().day
    return ConceptCard(
        finance_concept=finance[day % len(finance)],
        sustainability_concept=sustainability[day % len(sustainability)],
        date=datetime.utcnow(),
    )
