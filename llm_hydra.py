"""
LLM API Hydra - Single file, boom ready
Uses Groq (free) - get key from https://console.groq.com/keys

pip install openai
python llm_hydra.py
"""
import os
from openai import OpenAI

# --- CONFIG: Just put your key here ---
# Get free key: https://console.groq.com/keys
GROQ_API_KEY = os.getenv("GROQ_API_KEY") or "gsk_YOUR_KEY_HERE"

client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=GROQ_API_KEY
)

MODEL_FAST = "llama-3.1-8b-instant"  # fast, cheap
MODEL_SMART = "llama-3.3-70b-versatile"  # balanced

def simple_chat():
    print("\n=== 1. SIMPLE CHAT (System + User + Streaming) ===")
    messages = [
        {"role": "system", "content": "You are a helpful assistant. Be concise."},
        {"role": "user", "content": "Explain tokens vs context window in 3 bullets"}
    ]
    stream = client.chat.completions.create(
        model=MODEL_FAST,
        messages=messages,
        temperature=0.2,  # low = deterministic for learning
        max_tokens=300,
        stream=True
    )
    for chunk in stream:
        if chunk.choices[0].delta.content:
            print(chunk.choices[0].delta.content, end="", flush=True)
    print("\n")

def structured_output():
    print("\n=== 2. STRUCTURED OUTPUT (JSON mode) ===")
    res = client.chat.completions.create(
        model=MODEL_FAST,
        messages=[
            {"role": "system", "content": "You output only valid JSON."},
            {"role": "user", "content": "Give me 2 LLM models with cost and latency rating as JSON: {models: [{name, cost, latency}]}"}
        ],
        temperature=0,
        response_format={"type": "json_object"}
    )
    print(res.choices[0].message.content)
    print(f"Tokens used: {res.usage.total_tokens} | Cost: ~${res.usage.total_tokens * 0.0000002:.6f}")

def tool_calling_demo():
    print("\n=== 3. TOOL CALLING ===")
    tools = [{
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get weather for a city",
            "parameters": {
                "type": "object",
                "properties": {"city": {"type": "string"}},
                "required": ["city"]
            }
        }
    }]
    
    res = client.chat.completions.create(
        model=MODEL_SMART,
        messages=[{"role": "user", "content": "What's weather in Bangalore?"}],
        tools=tools,
        tool_choice="auto"
    )
    
    msg = res.choices[0].message
    if msg.tool_calls:
        print(f"Model wants to call: {msg.tool_calls[0].function.name}({msg.tool_calls[0].function.arguments})")
        # You execute the tool here
        tool_result = '{"temp": "26C", "condition": "cloudy"}'
        print(f"Tool result: {tool_result}")
        print("-> You would send this back as role: tool to get final answer")
    else:
        print(msg.content)

if __name__ == "__main__":
    if "YOUR_KEY" in GROQ_API_KEY:
        print("⚠️  Set your GROQ_API_KEY first!")
        print("1. Go to https://console.groq.com/keys")
        print("2. Create key, then: export GROQ_API_KEY=gsk_...")
        print("   or paste it into GROQ_API_KEY variable in this file")
    else:
        simple_chat()
        structured_output()
        tool_calling_demo()
        print("\n✅ Done. You covered: tokens, context, system/user, streaming, structured output, tool calling, model selection, latency & cost")
