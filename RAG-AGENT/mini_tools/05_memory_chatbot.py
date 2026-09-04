import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

# 1. Set OpenAI API key
os.environ["OPENAI_API_KEY"] = "your-openai-api-key-here"

# 2. Store chat session histories in memory
store = {}

def get_session_history(session_id: str):
    if session_id not in store:
        store[session_id] = InMemoryChatMessageHistory()
    
    # Strictly trim to keep only the last 3 user-assistant pairs (6 messages total)
    messages = store[session_id].messages
    if len(messages) > 6:
        store[session_id].messages = messages[-6:]
        
    return store[session_id]

# 3. Create Prompt & Chain
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant. Remember context provided in recent messages."),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{input}")
])

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
chain = prompt | llm

# 4. Wrap chain with memory history
chatbot = RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key="input",
    history_messages_key="history",
)

# 5. Simulate a multi-turn conversation
session_config = {"configurable": {"session_id": "user_123"}}

turns = [
    "Hi, my name is Alex and my favorite color is Blue.",
    "I live in Bengaluru and I love playing Chess.",
    "My favorite food is Biryani.",
    "I have two pets: a dog named Max and a cat named Luna.",
    "Can you recall my name, favorite color, and my pets?" # 4th response - Alex/Blue from turn 1 will be trimmed!
]

print("--- Memory Chatbot (Last 3 Turns Only) ---")
for i, user_msg in enumerate(turns, 1):
    print(f"\n[Turn {i}] User: {user_msg}")
    res = chatbot.invoke({"input": user_msg}, config=session_config)
    print(f"Assistant: {res.content}")