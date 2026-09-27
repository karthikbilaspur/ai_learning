import os
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate

# 1. Set API Keys
os.environ["OPENAI_API_KEY"] = "your-openai-api-key-here"
os.environ["TAVILY_API_KEY"] = "your-tavily-api-key-here"  # Get free key at https://tavily.com

# 2. Setup Tavily Search Tool (Searches & extracts page content)
search_tool = TavilySearchResults(
    max_results=3,
    include_answer=True,
    include_raw_content=False
)
tools = [search_tool]

# 3. Setup LLM and Prompt Instructions
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)

system_prompt = (
    "You are an expert Research Analyst. Your job is to:\n"
    "1. Use the web search tool to gather up-to-date factual information on the user's topic.\n"
    "2. Read and synthesize key information from multiple search results.\n"
    "3. Generate a structured executive summary report with clear headings, key insights, and key takeaways."
)

prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}"),
])

# 4. Construct the Research Agent
agent = create_tool_calling_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# 5. Run a Research Query
topic = "Latest breakthroughs in Quantum Computing in 2026"

print(f"--- Starting Research on: '{topic}' ---\n")
result = agent_executor.invoke({"input": f"Research and generate an executive report on: {topic}"})

print("\n" + "="*50)
print("--- FINAL RESEARCH REPORT ---")
print("="*50)
print(result["output"])