import json
from typing import TYPE_CHECKING, Any

try:
    from langchain_openai import ChatOpenAI
except ImportError:  # pragma: no cover
    ChatOpenAI = Any  # type: ignore[assignment]

try:
    from tavily import TavilyClient
except ImportError:  # pragma: no cover
    class TavilyClient:  # type: ignore[no-redef]
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            pass

        def search(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
            return {"results": []}

try:
    from firecrawl import FirecrawlApp
except ImportError:  # pragma: no cover
    class FirecrawlApp:  # type: ignore[no-redef]
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            pass

        def scrape_url(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
            return {}

if TYPE_CHECKING:
    from app.agent.state import CompetitorProfile, MarketResearchState
else:
    try:
        from app.agent.state import CompetitorProfile, MarketResearchState
    except ImportError:  # pragma: no cover
        MarketResearchState = dict[str, Any]

        class CompetitorProfile(dict[str, Any]):
            def model_dump(self) -> dict[str, Any]:
                return dict(self)

from app.core.config import settings

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)
tavily = TavilyClient(api_key=settings.TAVILY_API_KEY)
firecrawl = FirecrawlApp(api_key=settings.FIRECRAWL_API_KEY) if settings.FIRECRAWL_API_KEY else None

def scout_node(state: MarketResearchState) -> dict[str, Any]:
    """Scout Agent: Uses Tavily for initial discovery & Firecrawl for full Markdown web scraping."""
    company = state["company_name"]
    query = f"{company} pricing plans features"

    scraped_docs: list[str] = []

    # 1. Search Tavily for target URL discovery
    search_response = tavily.search(query=query, max_results=2)
    urls = [doc["url"] for doc in search_response.get("results", [])]

    # 2. Firecrawl integration: Scrape Javascript-heavy pages directly to clean Markdown
    if firecrawl and urls:
        for url in urls:
            try:
                scrape_result = firecrawl.scrape_url(url, params={"formats": ["markdown"]})
                if "markdown" in scrape_result:
                    scraped_docs.append(scrape_result["markdown"])
            except Exception:
                # Fallback to standard Tavily content snippet if Firecrawl fails
                pass

    # Fallback to Tavily snippets if Firecrawl is unconfigured or returned no data
    if not scraped_docs:
        scraped_docs = [doc["content"] for doc in search_response.get("results", [])]

    return {
        "scraped_documents": scraped_docs,
        "search_retry_count": state.get("search_retry_count", 0) + 1,
    }

def analyst_node(state: MarketResearchState) -> dict[str, Any]:
    docs = "\n\n".join(state["scraped_documents"])
    structured_llm = llm.with_structured_output(CompetitorProfile)
    prompt = f"Extract a structured profile for {state['company_name']} from these web documents:\n\n{docs}"
    profile = structured_llm.invoke(prompt)
    return {"structured_data": profile.model_dump()}

def critic_node(state: MarketResearchState) -> dict[str, Any]:
    data = state.get("structured_data")
    prompt = f"Synthesize an executive report for {state['company_name']} based on structured data: {json.dumps(data)}"
    response = llm.invoke(prompt)
    return {"final_report": response.content, "critique_feedback": None}