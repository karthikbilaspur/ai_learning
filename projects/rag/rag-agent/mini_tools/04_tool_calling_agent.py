import os
import math
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate

# 1. Set OpenAI API key
os.environ["OPENAI_API_KEY"] = "your-openai-api-key-here"

# 2. Define Weather Tool
@tool
def get_weather(city: str) -> str:
    """Get current temperature and weather conditions for a given city."""
    # Mock data (Replace with OpenWeatherMap API call if needed)
    weather_db = {
        "london": "14°C, Light Rain",
        "tokyo": "21°C, Clear Skies",
        "mumbai": "31°C, High Humidity",
        "new york": "19°C, Partly Cloudy"
    }
    return weather_db.get(city.lower(), f"Weather data unavailable for {city}.")

# 3. Define Calculator Tool
@tool
def calculate(expression: str) -> str:
    """Evaluate a mathematical expression (e.g. '25 * 4', 'sqrt(144)', '1200 / 12')."""
    try:
        # Safe math scope with basic functions
        allowed_names = {"sqrt": math.sqrt, "pow": pow, "abs": abs}
        result = eval(expression, {"__builtins__": None}, allowed_names)
        return str(result)
    except Exception as e:
        return f"Error evaluating expression: {str(e)}"

tools = [get_weather, calculate]

# 4. Initialize LLM & Agent
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant. Use tools for weather lookups and math calculations."),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}"),
])

agent = create_tool_calling_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=False)

# 5. Queries (Weather, Math, and Both combined)
queries = [
    "What is the weather in Mumbai right now?",
    "Calculate sqrt(256) * 15.",
    "If the temperature in Tokyo is 21°C, what would it be in Fahrenheit? (Formula: C * 9/5 + 32)"
]

print("--- Calculator & Weather Agent Results ---")
for i, q in enumerate(queries, 1):
    response = agent_executor.invoke({"input": q})
    print(f"\nQ{i}: {q}")
    print(f"A: {response['output']}")