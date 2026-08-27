import os
import time
import json
from typing import Any, Dict, Optional
from openai import OpenAI

# ============================================================
# CONFIG
# ============================================================

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError(
        "Please set OPENAI_API_KEY.\n"
        "PowerShell:\n"
        '$env:OPENAI_API_KEY="sk-..."'
    )

client = OpenAI(api_key=OPENAI_API_KEY)

# Replace these with models currently available to your account.
MODEL_FAST = "gpt-4.1-mini"
MODEL_SMART = "gpt-4.1"


# ============================================================
# HELPER
# ============================================================

def ask_llm(messages: list[dict], model: str = MODEL_FAST, temperature: float = 0) -> Optional[Dict[str, Any]]:
    start = time.perf_counter()
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature
        )
        latency = time.perf_counter() - start
        return {
            "content": response.choices[0].message.content,
            "usage": response.usage,
            "latency": latency,
            "response": response
        }
    except Exception as e:
        print(f"LLM request failed: {e}")
        return None

def get_weather(city: str) -> dict[str, str]:
    return {"city": city, "temperature": "26°C", "condition": "cloudy"}

def calculator(a: float, b: float, operation: str) -> float | str:
    if operation == "add": return a + b
    if operation == "subtract": return a - b
    if operation == "multiply": return a * b
    if operation == "divide":
        return "Cannot divide by zero." if b == 0 else a / b
    return "Unknown operation."

# ============================================================
# 1. SIMPLE CHAT + STREAMING
# ============================================================

def simple_chat():

    print("\n" + "=" * 60)
    print("1. SIMPLE CHAT + STREAMING")
    print("=" * 60)

    messages = [
        {
            "role": "system",
            "content": (
                "You are a helpful LLM tutor. "
                "Explain concepts clearly and concisely."
            )
        },
        {
            "role": "user",
            "content": "Explain tokens vs context window in 3 bullets."
        }
    ]

    start = time.perf_counter()

    try:

        stream = client.chat.completions.create(
            model=MODEL_FAST,
            messages=messages,
            temperature=0.2,
            max_tokens=300,
            stream=True
        )

        print("\nLLM: ", end="", flush=True)

        for chunk in stream:

            if not chunk.choices:
                continue

            content = chunk.choices[0].delta.content

            if content:
                print(content, end="", flush=True)

        latency = time.perf_counter() - start

        print(f"\n\nLatency: {latency:.2f}s")

    except Exception as e:
        print(f"\nError: {e}")


# ============================================================
# 2. MULTI-TURN CHAT / MEMORY
# ============================================================

def chat_with_memory():

    print("\n" + "=" * 60)
    print("2. MULTI-TURN CHAT + MEMORY")
    print("=" * 60)

    messages = [
        {
            "role": "system",
            "content": (
                "You are a helpful Python tutor. "
                "Remember the conversation and answer clearly."
            )
        }
    ]

    while True:

        user_input = input("\nYou: ")

        if user_input.lower() in ["exit", "quit"]:
            print("Exiting chat...")
            break

        messages.append({
            "role": "user",
            "content": user_input
        })

        result = ask_llm(
            messages,
            model=MODEL_FAST,
            temperature=0.3
        )

        if not result:
            continue

        answer = result["content"]

        print(f"AI: {answer}")

        messages.append({
            "role": "assistant",
            "content": answer
        })

        if result["usage"]:

            print(
                f"\nTokens: {result['usage'].total_tokens}"
                f" | Latency: {result['latency']:.2f}s"
            )


# ============================================================
# 3. STRUCTURED JSON OUTPUT
# ============================================================

def structured_output():

    print("\n" + "=" * 60)
    print("3. STRUCTURED OUTPUT")
    print("=" * 60)

    messages = [
        {
            "role": "system",
            "content": (
                "Return only valid JSON. "
                "Do not include markdown."
            )
        },
        {
            "role": "user",
            "content": """
Give me 3 LLM concepts.

Return exactly this structure:

{
    "topics": [
        {
            "name": "",
            "difficulty": "",
            "description": ""
        }
    ]
}
"""
        }
    ]

    start = time.perf_counter()

    try:

        response = client.chat.completions.create(
            model=MODEL_FAST,
            messages=messages,
            temperature=0,
            response_format={
                "type": "json_object"
            }
        )

        latency = time.perf_counter() - start

        raw_json = response.choices[0].message.content

        # Actually parse the JSON.
        data = json.loads(raw_json)

        print("\nParsed JSON:")

        print(
            json.dumps(
                data,
                indent=4
            )
        )

        if response.usage:

            print(
                f"\nInput tokens: "
                f"{response.usage.prompt_tokens}"
            )

            print(
                f"Output tokens: "
                f"{response.usage.completion_tokens}"
            )

            print(
                f"Total tokens: "
                f"{response.usage.total_tokens}"
            )

        print(f"Latency: {latency:.2f}s")

    except json.JSONDecodeError:

        print("Model returned invalid JSON.")

    except Exception as e:

        print(f"Error: {e}")


# ============================================================
# 4. TOOLS
# ============================================================

def get_weather(city: str):

    """
    Fake weather function for learning.

    In a real application this would call a weather API.
    """

    return {
        "city": city,
        "temperature": "26°C",
        "condition": "cloudy"
    }


def calculator(a: float, b: float, operation: str):

    if operation == "add":
        return a + b

    if operation == "subtract":
        return a - b

    if operation == "multiply":
        return a * b

    if operation == "divide":

        if b == 0:
            return "Cannot divide by zero."

        return a / b

    return "Unknown operation."


# ============================================================
# TOOL DEFINITIONS
# ============================================================

TOOLS = [

    {
        "type": "function",

        "function": {

            "name": "get_weather",

            "description": (
                "Get the current weather for a city."
            ),

            "parameters": {

                "type": "object",

                "properties": {

                    "city": {
                        "type": "string",
                        "description": "City name"
                    }

                },

                "required": ["city"]
            }
        }
    },

    {
        "type": "function",

        "function": {

            "name": "calculator",

            "description": (
                "Perform basic mathematical calculations."
            ),

            "parameters": {

                "type": "object",

                "properties": {

                    "a": {
                        "type": "number"
                    },

                    "b": {
                        "type": "number"
                    },

                    "operation": {
                        "type": "string",
                        "enum": [
                            "add",
                            "subtract",
                            "multiply",
                            "divide"
                        ]
                    }
                },

                "required": [
                    "a",
                    "b",
                    "operation"
                ]
            }
        }
    }
]


# ============================================================
# 5. COMPLETE TOOL-CALLING LOOP
# ============================================================

def tool_calling_demo():

    print("\n" + "=" * 60)
    print("4. COMPLETE TOOL CALLING")
    print("=" * 60)

    messages = [

        {
            "role": "system",
            "content": (
                "You are a helpful assistant. "
                "Use tools when necessary."
            )
        },

        {
            "role": "user",
            "content": (
                "What's the weather in Bangalore? "
                "Also calculate 25 * 4."
            )
        }
    ]

    try:

        response = client.chat.completions.create(
            model=MODEL_SMART,
            messages=messages,
            tools=TOOLS,
            tool_choice="auto"
        )

        msg = response.choices[0].message

        # ----------------------------------------------------
        # No tool required
        # ----------------------------------------------------

        if not msg.tool_calls:

            print("\nAI:")
            print(msg.content)
            return

        # ----------------------------------------------------
        # Add assistant tool-call message to history
        # ----------------------------------------------------

        messages.append(msg)

        # ----------------------------------------------------
        # Execute every requested tool
        # ----------------------------------------------------

        for tool_call in msg.tool_calls:

            function_name = tool_call.function.name

            arguments = json.loads(
                tool_call.function.arguments
            )

            print(
                f"\nTool requested: "
                f"{function_name}"
            )

            print(
                f"Arguments: {arguments}"
            )

            # -----------------------------------------------
            # Execute weather
            # -----------------------------------------------

            if function_name == "get_weather":

                result = get_weather(
                    arguments["city"]
                )

            # -----------------------------------------------
            # Execute calculator
            # -----------------------------------------------

            elif function_name == "calculator":

                result = calculator(
                    arguments["a"],
                    arguments["b"],
                    arguments["operation"]
                )

            else:

                result = {
                    "error": "Unknown tool"
                }

            print(f"Tool result: {result}")

            # -----------------------------------------------
            # Send tool result back to model
            # -----------------------------------------------

            messages.append({

                "role": "tool",

                "tool_call_id": tool_call.id,

                "content": json.dumps(result)
            })

        # ----------------------------------------------------
        # Ask model for final response
        # ----------------------------------------------------

        final_response = client.chat.completions.create(

            model=MODEL_SMART,

            messages=messages,

            tools=TOOLS
        )

        final_answer = (
            final_response
            .choices[0]
            .message
            .content
        )

        print("\nFinal AI response:")
        print(final_answer)

    except Exception as e:

        print(f"\nTool calling error: {e}")


# ============================================================
# 6. MODEL COMPARISON
# ============================================================

def model_selection_demo():

    print("\n" + "=" * 60)
    print("5. MODEL SELECTION")
    print("=" * 60)

    models = [
        MODEL_FAST,
        MODEL_SMART
    ]

    question = (
        "Explain what an LLM is in one sentence."
    )

    for model in models:

        start = time.perf_counter()

        try:

            response = client.chat.completions.create(

                model=model,

                messages=[
                    {
                        "role": "user",
                        "content": question
                    }
                ],

                temperature=0
            )

            latency = (
                time.perf_counter()
                - start
            )

            print(f"\nModel: {model}")

            print(
                f"Response: "
                f"{response.choices[0].message.content}"
            )

            if response.usage:

                print(
                    f"Tokens: "
                    f"{response.usage.total_tokens}"
                )

            print(
                f"Latency: "
                f"{latency:.2f}s"
            )

        except Exception as e:

            print(
                f"\nModel {model} failed: {e}"
            )


# ============================================================
# 7. TOKEN / COST REPORT
# ============================================================

def token_demo():

    print("\n" + "=" * 60)
    print("6. TOKEN USAGE")
    print("=" * 60)

    response = client.chat.completions.create(

        model=MODEL_FAST,

        messages=[
            {
                "role": "user",
                "content": (
                    "Explain embeddings in simple terms."
                )
            }
        ],

        temperature=0
    )

    usage = response.usage

    print("\nAnswer:")
    print(response.choices[0].message.content)

    if usage:

        print("\nUsage:")

        print(
            f"Input tokens: "
            f"{usage.prompt_tokens}"
        )

        print(
            f"Output tokens: "
            f"{usage.completion_tokens}"
        )

        print(
            f"Total tokens: "
            f"{usage.total_tokens}"
        )

        print(
            "\nNote: calculate cost using the "
            "current pricing for the specific model "
            "you are using."
        )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    print("\n" + "=" * 60)
    print("OPENAI LLM API LEARNING DEMO")
    print("=" * 60)

    simple_chat()

    structured_output()

    tool_calling_demo()

    model_selection_demo()

    token_demo()

    # Uncomment this when you want interactive chat:
    #
    # chat_with_memory()

    print("\n" + "=" * 60)

    print(
        "✓ Covered:"
    )

    print(
        """
    - OpenAI API
    - Chat completions
    - System/user messages
    - Streaming
    - Conversation memory
    - Structured JSON
    - JSON parsing
    - Tool calling
    - Multiple tools
    - Complete tool loop
    - Model selection
    - Token tracking
    - Latency
    - Error handling
    - Provider abstraction
    """
    )

    print("=" * 60)