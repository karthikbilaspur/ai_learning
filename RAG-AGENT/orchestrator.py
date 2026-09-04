import os
import sys
import importlib.util
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool

# 1. Set OpenAI API Key
os.environ["OPENAI_API_KEY"] = "your-openai-api-key-here"

# Helper function to dynamically import scripts with dashes/numbers in filename
def load_tool_module(filename):
    module_path = os.path.join("mini-tools", filename)
    module_name = filename.replace("-", "_").replace(".py", "")
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module

# Add mini-tools to system path
sys.path.append(os.path.abspath("mini-tools"))

# 2. Define Wrapper Tools targeting scripts in 'mini-tools/' folder
@tool
def pdf_rag_tool(query: str) -> str:
    """[01] Queries unstructured PDF documents for information."""
    # mod = load_tool_module("01-pdf_rag.py")
    return f"[mini-tools/01-pdf_rag.py] Processed PDF query: '{query}'"

@tool
def web_qa_tool(query: str) -> str:
    """[02] Scrapes web pages and extracts targeted information."""
    return f"[mini-tools/02-website-qa.py] Extracted web answer for: '{query}'"

@tool
def csv_data_tool(query: str) -> str:
    """[03] Executes Pandas operations for structured CSV data analysis."""
    return f"[mini-tools/03-csv-data-agent.py] Executed CSV analysis for: '{query}'"

@tool
def tool_calling_tool(query: str) -> str:
    """[04] Performs exact math calculations or live weather lookups."""
    return f"[mini-tools/04-Tool-Calling-Agent.py] Processed math/weather query: '{query}'"

@tool
def memory_chatbot_tool(query: str) -> str:
    """[05] Manages multi-turn conversation maintaining recent history."""
    return f"[mini-tools/05-Memory-Chatbot.py] Responded with chat context to: '{query}'"

@tool
def research_tool(query: str) -> str:
    """[06] Conducts deep web search and synthesizes executive reports."""
    return f"[mini-tools/06-research-agent.py] Compiled web research report on: '{query}'"

@tool
def file_organizer_tool(query: str) -> str:
    """[07] Inspects local folders and autonomously organizes messy files."""
    return f"[mini-tools/07-file-organizer-agent.py] Organized local files for: '{query}'"

@tool
def code_reviewer_tool(code_snippet: str) -> str:
    """[08] Audits Python code for syntax errors, bugs, and optimizations."""
    return f"[mini-tools/08-code-reviewer-agent.py] Executed code security audit."

@tool
def voice_action_tool(query: str) -> str:
    """[09] Processes audio inputs (STT) and outputs spoken responses (TTS)."""
    return f"[mini-tools/09-voice-action-agent.py] Executed voice audio command."

orchestrator_tools = [
    pdf_rag_tool, web_qa_tool, csv_data_tool, tool_calling_tool,
    memory_chatbot_tool, research_tool, file_organizer_tool,
    code_reviewer_tool, voice_action_tool
]

# 3. Initialize Master Orchestrator Router
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
llm_with_tools = llm.bind_tools(orchestrator_tools)

system_prompt = (
    "You are the Master Orchestrator. Evaluate the user request and invoke "
    "the single most appropriate script inside the 'mini-tools' folder to handle it."
)

prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    ("human", "{input}")
])

orchestrator = prompt | llm_with_tools

# 4. Run Routing Test
queries = [
    "Organize all files in my downloads folder into neat categories.",
    "Perform a deep research report on battery tech in 2026.",
    "Review my code snippet for security holes.",
    "Calculate 50 * 12 and check London weather."
]

print("--- Orchestrator Routing to mini-tools/ Folder ---\n")
for i, q in enumerate(queries, 1):
    response = orchestrator.invoke({"input": q})
    tool_call = response.tool_calls[0] if response.tool_calls else None
    print(f"[Query {i}]: {q}")
    if tool_call:
        print(f"  ➜ Target Tool: {tool_call['name']}")
        print(f"  ➜ Input Args : {tool_call['args']}\n")