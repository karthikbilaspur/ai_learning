import asyncio
from src.agent import AgentOrchestrator
def test_agent():
 async def run(): return await AgentOrchestrator().run("What is RAG?","test")
 r=asyncio.run(run()); assert r["answer"] and r["citations"]

def test_no_fabricated_citation(monkeypatch):
    agent=AgentOrchestrator()
    async def run(): return await agent.run("What is RAG?","citation-test")
    r=asyncio.run(run())
    assert r["citation_validation"]["valid"]
    assert "[" in r["answer"]
