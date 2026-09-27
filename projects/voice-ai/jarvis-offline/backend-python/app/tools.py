import datetime, json, os, random, requests
NOTES_FILE=os.getenv('NOTES_FILE','./data/notes.json')
os.makedirs(os.path.dirname(NOTES_FILE) or '.',exist_ok=True)
def get_time(args): return datetime.datetime.now().astimezone().strftime('%I:%M %p, %A %B %d')
def get_weather(args):
    city=args.get('city','Bangalore')
    try:
        r=requests.get(f'https://wttr.in/{city}?format=%C+%t',timeout=3)
        if r.ok: return r.text.strip()
    except Exception: pass
    return f'Weather is unavailable offline for {city}.'
def tell_joke(args): return random.choice(['Why do programmers prefer dark mode? Because light attracts bugs.','I asked my AI for a joke. It said: 404 humor not found.','I have a joke about recursion, but first I have to tell you a joke about recursion.'])
def remember_note(args):
    note=(args.get('text') or args.get('note') or '').strip()
    if not note: return 'Tell me what you want me to remember.'
    try:
        data=json.load(open(NOTES_FILE)) if os.path.exists(NOTES_FILE) else []
    except Exception: data=[]
    data.append({'note':note,'time':datetime.datetime.now().astimezone().isoformat()})
    json.dump(data,open(NOTES_FILE,'w'),indent=2)
    return f'Noted: {note}'
def list_events_today(args):
    try:
        r=requests.get('http://localhost:5000/api/calendar/events/today',timeout=5)
        if r.status_code==401: return 'Google Calendar is not connected yet.'
        if not r.ok: return 'I could not read the calendar.'
        events=r.json()
        if not events: return 'Your calendar is clear today.'
        return 'Today: '+', '.join(f"{e['summary']} at {e['start']}" for e in events[:8])
    except Exception: return 'I could not reach the calendar gateway.'
def create_event(args):
    title=args.get('title') or args.get('summary')
    start=args.get('start'); end=args.get('end')
    if not title or not start or not end: return 'To create an event I need a title, start time, and end time.'
    try:
        r=requests.post('http://localhost:5000/api/calendar/events',json={'title':title,'start':start,'end':end,'description':args.get('description',''),'location':args.get('location','')},timeout=10)
        if r.status_code==401: return 'Google Calendar is not connected yet.'
        if not r.ok: return 'Calendar rejected the event.'
        return f"Created '{title}' on your calendar."
    except Exception: return 'I could not reach the calendar gateway.'
available_tools={'get_time':get_time,'get_weather':get_weather,'tell_joke':tell_joke,'remember_note':remember_note,'list_events_today':list_events_today,'create_event':create_event}
def execute_tool(name,args): return available_tools.get(name,lambda a:'Unknown tool')(args)
