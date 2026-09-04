import os
import ast
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate

# 1. Set OpenAI API Key
os.environ["OPENAI_API_KEY"] = "your-openai-api-key-here"

# 2. Define Code Inspection Tools
@tool
def check_syntax(code_str: str) -> str:
    """Validates if the provided Python code has any syntax errors."""
    try:
        ast.parse(code_str)
        return "Syntax Check: PASSED (No syntax errors found)."
    except SyntaxError as e:
        return f"Syntax Check: FAILED on line {e.lineno}: {e.msg}"

tools = [check_syntax]

# 3. Sample Buggy Code snippet for analysis
buggy_code = """
def process_user_data(user_list):
    # Bug 1: Dangerous eval usage
    # Bug 2: Index error risk
    # Bug 3: Inefficient loop concatenation
    result = ""
    for i in range(len(user_list) + 1):
        data = eval(user_list[i])
        result = result + str(data) + ","
    return result
"""

# 4. Build Code Reviewer Agent
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

system_prompt = (
    "You are an expert Senior Python Code Reviewer.\n"
    "1. Always check syntax first using the `check_syntax` tool.\n"
    "2. Analyze the code for bugs, security vulnerabilities, performance bottlenecks, and style issues.\n"
    "3. Output a structured Code Review Report including:\n"
    "   - **Issues Identified** (Categorized by Severity: Critical, Warning, Info)\n"
    "   - **Refactored Code** (Fully functional, optimized, and secure Python code)\n"
    "   - **Key Improvements Made**"
)

prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    ("human", "Review the following Python code:\n```python\n{code}\n```"),
    ("placeholder", "{agent_scratchpad}"),
])

agent = create_tool_calling_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=False)

# 5. Run the Code Review
print("--- Running Code Reviewer Agent ---\n")
response = agent_executor.invoke({"code": buggy_code})

print("=" * 50)
print("--- CODE REVIEW REPORT ---")
print("=" * 50)
print(response["output"])