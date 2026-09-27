import os
from openai import OpenAI
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate

# 1. Set OpenAI API Key
os.environ["OPENAI_API_KEY"] = "your-openai-api-key-here"
client = OpenAI()

# 2. Define Executable Action Tools
@tool
def send_email(recipient: str, message: str) -> str:
    """Simulates sending an email to a recipient."""
    return f"Email successfully sent to '{recipient}' with body: '{message}'."

@tool
def set_reminder(task: str, time: str) -> str:
    """Sets a reminder for a specific task and time."""
    return f"Reminder set: '{task}' at {time}."

tools = [send_email, set_reminder]

# 3. Audio Pipeline Functions (STT & TTS)
def transcribe_audio(audio_path: str) -> str:
    """Converts Speech to Text using OpenAI Whisper."""
    with open(audio_path, "rb") as f:
        transcript = client.audio.transcriptions.create(model="whisper-1", file=f)
    return transcript.text

def speak_text(text: str, output_path: str = "response.mp3"):
    """Converts Text to Speech using OpenAI TTS."""
    response = client.audio.speech.create(model="tts-1", voice="alloy", input=text)
    response.stream_to_file(output_path)
    print(f"🔊 Audio response saved to: {output_path}")

# 4. Build Voice Action Agent
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a Voice Action Assistant. Listen to transcribed commands and trigger the correct tool."),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}"),
])

agent = create_tool_calling_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# 5. Execution Pipeline (Simulated with text input if audio file isn't present)
AUDIO_FILE = "input_command.mp3"

if os.path.exists(AUDIO_FILE):
    print("🎙️ Transcribing voice command...")
    user_command = transcribe_audio(AUDIO_FILE)
else:
    # Simulated voice transcript
    user_command = "Please set a reminder to call John tomorrow at 5 PM."

print(f"\n🗣️ Voice Input: '{user_command}'")

# Process command and generate spoken answer
result = agent_executor.invoke({"input": user_command})
response_text = result["output"]

print(f"\n🤖 Agent Output: {response_text}")
speak_text(response_text)