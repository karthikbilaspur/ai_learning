import os
from langchain_openai import ChatOpenAI
from tavily import TavilyClient
from agent.state import MarketResearchState, CompetitorProfile

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)
tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

def scout_node(state: MarketResearchState) -> dict:
    """Scout Agent: Performs targeted web searches to gather raw data."""
    company = state["company_name"]
    retry_count = state.get("search_retry_count", 0)
    
    # Adjust query if critic gave feedback
    query = f"{company} pricing plans target audience features"
    if state.get("critique_feedback"):
        query += f" {state['critique_feedback']}"

    search_response = tavily.search(query=query, max_results=3)
    results = [doc["content"] for doc in search_response.get("results", [])]
    
    return {
        "scraped_documents": results,
        "search_retry_count": retry_count + 1
    }

def analyst_node(state: MarketResearchState) -> dict:
    """Analyst Agent: Extracts structured pricing & feature JSON from raw text."""
    docs = "\n\n".join(state["scraped_documents"])
    
    structured_llm = llm.with_structured_output(CompetitorProfile)
    prompt = f"Extract a structured profile for {state['company_name']} from these web documents:\n\n{docs}"
    
    profile: CompetitorProfile = structured_llm.invoke(prompt)
    return {"structured_data": profile.model_dump()}

def critic_node(state: MarketResearchState) -> dict:
    """Critic Node: Evaluates if structured data is complete or needs another pass."""
    data = state.get("structured_data")
    retry_count = state.get("search_retry_count", 0)
    
    # If missing pricing tiers and under retry limit, trigger re-search
    if (not data or not data.get("pricing_tiers")) and retry_count < 2:
        return {"critique_feedback": "missing explicit pricing tiers and plan details"}
    
    # Otherwise synthesis report
    prompt = f"""Synthesize a high-level executive report for {state['company_name']}.
    Structured Data: {data}
    Raw Documents: {state['scraped_documents']}"""
    
    response = llm.invoke(prompt)
    return {"final_report": response.content, "critique_feedback": None}