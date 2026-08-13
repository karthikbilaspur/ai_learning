import json
import os
import time
from typing import Any, Optional

from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam, ChatCompletionToolParam


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

# These can be changed to models available to your account.
MODEL_FAST = "gpt-4.1-mini"
MODEL_SMART = "gpt-4.1"


# ============================================================
# HELPER
# ============================================================

def ask_llm(
    messages: list[ChatCompletionMessageParam],
    model: str = MODEL_FAST,
    temperature: float = 0,
) -> Optional[dict[str, Any]]:
    """Call the Chat Completions API and return useful response data."""
    start = time.perf_counter()

    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
        )

        latency = time.perf_counter() - start

        return {
            "content": response.choices[0].message.content,
            "usage": response.usage,
            "latency": latency,
            "response": response,
        }

    except Exception as e:
        print(f"LLM request failed: {e}")
        return None


# ============================================================
# LOCAL DEMO TOOLS
# ============================================================

def get_weather(city: str) -> dict[str, str]:
    """Fake weather function for learning."""
    return {
        "city": city,
        "temperature": "26°C",
        "condition": "cloudy",
    }


def calculator(
    a: float,
    b: float,
    operation: str,
) -> float | str:
    """Perform a basic calculation."""
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
# 1. SIMPLE CHAT + STREAMING
# ============================================================

def simple_chat() -> None:
    print("\n" + "=" * 60)
    print("1. SIMPLE CHAT + STREAMING")
    print("=" * 60)

    messages: list[ChatCompletionMessageParam] = [
        {
            "role": "system",
            "content": (
                "You are a helpful LLM tutor. "
                "Explain concepts clearly and concisely."
            ),
        },
        {
            "role": "user",
            "content": "Explain tokens vs context window in 3 bullets.",
        },
    ]

    start = time.perf_counter()

    try:
        stream = client.chat.completions.create(
            model=MODEL_FAST,
            messages=messages,
            temperature=0.2,
            max_completion_tokens=300,
            stream=True,
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

def chat_with_memory() -> None:
    print("\n" + "=" * 60)
    print("2. MULTI-TURN CHAT + MEMORY")
    print("=" * 60)

    messages: list[ChatCompletionMessageParam] = [
        {
            "role": "system",
            "content": (
                "You are a helpful Python tutor. "
                "Remember the conversation and answer clearly."
            ),
        }
    ]

    while True:
        user_input = input("\nYou: ").strip()

        if user_input.lower() in {"exit", "quit"}:
            print("Exiting chat...")
            break

        if not user_input:
            continue

        messages.append(
            {
                "role": "user",
                "content": user_input,
            }
        )

        result = ask_llm(
            messages,
            model=MODEL_FAST,
            temperature=0.3,
        )

        if not result:
            continue

        answer = result["content"]
        print(f"AI: {answer}")

        messages.append(
            {
                "role": "assistant",
                "content": answer,
            }
        )

        if result["usage"]:
            print(
                f"\nTokens: {result['usage'].total_tokens}"
                f" | Latency: {result['latency']:.2f}s"
            )


# ============================================================
# 3. STRUCTURED JSON OUTPUT
# ============================================================

def structured_output() -> None:
    print("\n" + "=" * 60)
    print("3. STRUCTURED OUTPUT")
    print("=" * 60)

    messages: list[ChatCompletionMessageParam] = [
        {
            "role": "system",
            "content": (
                "Return exactly 3 LLM concepts. "
                "Each concept must have name, difficulty, and description."
            ),
        },
        {
            "role": "user",
            "content": "Give me 3 LLM concepts.",
        },
    ]

    start = time.perf_counter()

    try:
        response = client.chat.completions.create(
            model=MODEL_FAST,
            messages=messages,
            temperature=0,
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "llm_concepts",
                    "strict": True,
                    "schema": {
                        "type": "object",
                        "properties": {
                            "topics": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "name": {"type": "string"},
                                        "difficulty": {"type": "string"},
                                        "description": {"type": "string"},
                                    },
                                    "required": [
                                        "name",
                                        "difficulty",
                                        "description",
                                    ],
                                    "additionalProperties": False,
                                },
                            }
                        },
                        "required": ["topics"],
                        "additionalProperties": False,
                    },
                },
            },
        )

        latency = time.perf_counter() - start
        raw_json = response.choices[0].message.content

        if raw_json is None:
            raise ValueError("The model returned no content.")

        data = json.loads(raw_json)

        print("\nParsed JSON:")
        print(json.dumps(data, indent=4))

        if response.usage:
            print(f"\nInput tokens: {response.usage.prompt_tokens}")
            print(f"Output tokens: {response.usage.completion_tokens}")
            print(f"Total tokens: {response.usage.total_tokens}")

        print(f"Latency: {latency:.2f}s")

    except json.JSONDecodeError:
        print("Model returned invalid JSON.")

    except Exception as e:
        print(f"Error: {e}")


# ============================================================
# 4. TOOLS
# ============================================================

TOOLS: list[ChatCompletionToolParam] = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get the current weather for a city.",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "City name",
                    }
                },
                "required": ["city"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": "Perform basic mathematical calculations.",
            "parameters": {
                "type": "object",
                "properties": {
                    "a": {"type": "number"},
                    "b": {"type": "number"},
                    "operation": {
                        "type": "string",
                        "enum": [
                            "add",
                            "subtract",
                            "multiply",
                            "divide",
                        ],
                    },
                },
                "required": ["a", "b", "operation"],
                "additionalProperties": False,
            },
        },
    },
]


def execute_tool(tool_name: str, arguments: dict[str, Any]) -> Any:
    """Dispatch a model-requested tool call to the local Python function."""
    if tool_name == "get_weather":
        return get_weather(arguments["city"])

    if tool_name == "calculator":
        return calculator(
            arguments["a"],
            arguments["b"],
            arguments["operation"],
        )

    return {"error": f"Unknown tool: {tool_name}"}


# ============================================================
# 5. COMPLETE TOOL-CALLING LOOP
# ============================================================

def tool_calling_demo() -> None:
    print("\n" + "=" * 60)
    print("4. COMPLETE TOOL CALLING")
    print("=" * 60)

    messages: list[ChatCompletionMessageParam] = [
        {
            "role": "system",
            "content": "You are a helpful assistant. Use tools when necessary.",
        },
        {
            "role": "user",
            "content": "What's the weather in Bangalore? Also calculate 25 * 4.",
        },
    ]

    try:
        while True:
            response = client.chat.completions.create(
                model=MODEL_SMART,
                messages=messages,
                tools=TOOLS,
                tool_choice="auto",
            )

            msg = response.choices[0].message

            # No tools needed -> final answer
            if not msg.tool_calls:
                print("\nAI:")
                print(msg.content)
                return

            # Convert tool_calls objects -> dicts (Pylance fix)
            messages.append({
                "role": "assistant",
                "content": msg.content or "",
                "tool_calls": [
                    {
                        "id": getattr(tc, "id", ""),
                        "type": "function",
                        "function": {
                            "name": getattr(getattr(tc, "function", None), "name", ""),
                            "arguments": getattr(getattr(tc, "function", None), "arguments", "{}"),
                        },
                    }
                    for tc in msg.tool_calls
                ],
            })

            # Execute each tool
            for tool_call in msg.tool_calls:
                tool_call_any: Any = tool_call
                function = getattr(tool_call_any, "function", None)
                if function is None:
                    result: Any = {"error": "Tool call missing function metadata."}
                    tool_call_id = getattr(tool_call_any, "id", "")
                else:
                    function_name = getattr(function, "name", "")
                    raw_arguments = getattr(function, "arguments", "{}")

                    try:
                        arguments = json.loads(raw_arguments)
                    except json.JSONDecodeError as e:
                        result = {"error": f"Invalid tool arguments: {e}"}
                    else:
                        print(f"\nTool requested: {function_name}")
                        print(f"Arguments: {arguments}")
                        result = execute_tool(function_name, arguments)

                    tool_call_id = getattr(tool_call_any, "id", "")

                print(f"Tool result: {result}")

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call_id,
                    "content": json.dumps(result),
                })

    except Exception as e:
        print(f"\nTool calling error: {e}")

# ============================================================
# 6. MODEL COMPARISON
# ============================================================

def model_selection_demo() -> None:
    print("\n" + "=" * 60)
    print("5. MODEL SELECTION")
    print("=" * 60)

    models = [
        MODEL_FAST,
        MODEL_SMART,
    ]

    question = "Explain what an LLM is in one sentence."

    for model in models:
        start = time.perf_counter()

        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "user",
                        "content": question,
                    }
                ],
                temperature=0,
            )

            latency = time.perf_counter() - start

            print(f"\nModel: {model}")
            print(
                "Response: "
                f"{response.choices[0].message.content}"
            )

            if response.usage:
                print(
                    f"Tokens: {response.usage.total_tokens}"
                )

            print(f"Latency: {latency:.2f}s")

        except Exception as e:
            print(f"\nModel {model} failed: {e}")


# ============================================================
# 7. TOKEN / COST REPORT
# ============================================================

def token_demo() -> None:
    print("\n" + "=" * 60)
    print("6. TOKEN USAGE")
    print("=" * 60)

    try:
        response = client.chat.completions.create(
            model=MODEL_FAST,
            messages=[
                {
                    "role": "user",
                    "content": "Explain embeddings in simple terms.",
                }
            ],
            temperature=0,
        )

        usage = response.usage

        print("\nAnswer:")
        print(response.choices[0].message.content)

        if usage:
            print("\nUsage:")
            print(f"Input tokens: {usage.prompt_tokens}")
            print(f"Output tokens: {usage.completion_tokens}")
            print(f"Total tokens: {usage.total_tokens}")

            print(
                "\nNote: calculate cost using the current pricing "
                "for the specific model you are using."
            )

    except Exception as e:
        print(f"\nToken demo error: {e}")


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
    # chat_with_memory()

    print("\n" + "=" * 60)
    print("✓ Covered:")
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
"""
    )
    print("=" * 60)