import os
import shutil
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate

# 1. Set OpenAI API Key
os.environ["OPENAI_API_KEY"] = "your-openai-api-key-here"

# 2. Define File Management Tools
TARGET_DIR = "./messy_folder"  # Directory to organize

@tool
def list_files() -> list:
    """Lists all files in the target directory (excluding folders)."""
    if not os.path.exists(TARGET_DIR):
        os.makedirs(TARGET_DIR)
    return [f for f in os.listdir(TARGET_DIR) if os.path.isfile(os.path.join(TARGET_DIR, f))]

@tool
def move_file(filename: str, category_folder: str) -> str:
    """Moves a file into a category subfolder inside target directory."""
    category_path = os.path.join(TARGET_DIR, category_folder)
    os.makedirs(category_path, exist_ok=True)
    
    src = os.path.join(TARGET_DIR, filename)
    dest = os.path.join(category_path, filename)
    shutil.move(src, dest)
    return f"Moved '{filename}' -> '{category_folder}/'"

tools = [list_files, move_file]

# 3. Create Sample Messy Files for Testing
os.makedirs(TARGET_DIR, exist_ok=True)
sample_files = ["report.pdf", "data.csv", "script.py", "photo.jpg", "notes.txt", "archive.zip"]
for f in sample_files:
    open(os.path.join(TARGET_DIR, f), 'a').close()

# 4. Build Agent
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
prompt = ChatPromptTemplate.from_messages([
    ("system", (
        "You are an autonomous File Organizer Agent.\n"
        "1. List all unorganized files in the folder.\n"
        "2. For each file, categorize it logically based on file extension "
        "(e.g., .pdf/.txt -> Documents, .jpg/.png -> Images, .py/.js -> Code, .csv -> Data, .zip -> Archives).\n"
        "3. Move every file to its proper subfolder.\n"
        "4. Output a summary report of organized files."
    )),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}"),
])

agent = create_tool_calling_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# 5. Execute Cleanup
print("--- Starting File Organizer Agent ---")
result = agent_executor.invoke({"input": f"Organize all files in {TARGET_DIR}"})

print("\n--- FINAL ORGANIZER REPORT ---")
print(result["output"])