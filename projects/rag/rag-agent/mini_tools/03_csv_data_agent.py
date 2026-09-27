import os
import pandas as pd
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from langchain_openai import ChatOpenAI

# 1. Set your OpenAI API key
os.environ["OPENAI_API_KEY"] = "your-openai-api-key-here"

# 2. Create a dummy sales CSV for testing (Skip this step if you already have a CSV)
sample_data = {
    "Product": ["Laptop", "Phone", "Tablet", "Laptop", "Phone", "Headphones"],
    "Region": ["North", "South", "North", "West", "North", "South"],
    "Sales": [1200, 800, 450, 1400, 900, 150],
    "Units_Sold": [4, 10, 5, 5, 12, 15]
}
pd.DataFrame(sample_data).to_csv("sales.csv", index=False)

# 3. Load CSV into Pandas
df = pd.read_csv("sales.csv")

# 4. Initialize the LLM and Pandas Data Agent
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
agent = create_pandas_dataframe_agent(
    llm, 
    df, 
    verbose=False, 
    allow_dangerous_code=True  # Required to execute generated Pandas code
)

# 5. List of 5 data queries/questions
queries = [
    "How many total rows are in this dataset?",
    "What is the total sales amount across all regions?",
    "Which product generated the highest overall sales revenue?",
    "What is the average number of units sold per product type?",
    "Show me a breakdown of total sales by Region."
]

# 6. Execute queries
print("--- CSV Data Agent Results ---")
for i, q in enumerate(queries, 1):
    response = agent.invoke({"input": q})
    print(f"\nQ{i}: {q}")
    print(f"A: {response['output']}")
    