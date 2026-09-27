import datetime,json,os,re,requests
SYSTEM="""You are JARVIS, a concise local voice assistant. Return either normal text or exactly one JSON object with this shape: {"tool":"tool_name","arguments":{...}}. Available tools: get_time, get_weather(city), tell_joke, remember_note(text), list_events_today, create_event(title,start,end,description?,location?). Use create_event only when all required fields are known. Never invent calendar details. Current local time: {time}."""
def call_ollama(prompt):
    try:
        r=requests.post(os.getenv('OLLAMA_URL','http://localhost:11434/api/generate'),json={'model':os.getenv('OLLAMA_MODEL','llama3.1:8b'),'prompt':prompt,'stream':False},timeout=45)
        if r.ok: return r.json().get('response','').strip()
    except Exception as e: print('Ollama unavailable:',e)
    return None
def parse_tool(text):
    if not text: return None
    candidates=re.findall(r'\{.*\}',text,re.S)
    for c in candidates:
        try:
            obj=json.loads(c)
            if obj.get('tool'): return obj
        except Exception: pass
    return None
def get_ai_response(transcript,history):
    lower=transcript.lower().strip()
    if any(w in lower for w in ['what time','current time','time is it','clock']): return f"It is {datetime.datetime.now().astimezone().strftime('%I:%M %p')}.",'get_time'
    if lower in ['tell me a joke','tell a joke','joke']: return execute('tell_joke',{}),'tell_joke'
    prompt=SYSTEM.format(time=datetime.datetime.now().astimezone().strftime('%Y-%m-%d %H:%M %Z'))+f'\nRecent history: {json.dumps(history[-5:])}\nUser: {transcript}\nJARVIS:'
    raw=call_ollama(prompt)
    obj=parse_tool(raw)
    if obj and obj.get('tool') in AVAILABLE: return execute(obj['tool'],obj.get('arguments',{})),obj['tool']
    if raw: return raw,None
    return 'My local language model is unavailable. Start Ollama and try again.',None
from .tools import execute_tool
AVAILABLE={'get_time','get_weather','tell_joke','remember_note','list_events_today','create_event'}
def execute(name,args): return execute_tool(name,args)
