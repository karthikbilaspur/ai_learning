import json,pathlib,requests,streamlit as st
st.set_page_config(page_title="RAG Agent",layout="wide"); st.title("Production RAG Agent")
api=st.sidebar.text_input("API URL","http://localhost:8000")
try:
 h=requests.get(api+"/health",timeout=3).json(); r=requests.get(api+"/ready",timeout=3).json(); st.metric("Indexed documents",r.get("docs_indexed",0)); st.success(h.get("status","unknown"))
except Exception as e: st.warning(f"API unavailable: {e}")
p=pathlib.Path("evals/latest_metrics.json")
if p.exists():
 m=json.loads(p.read_text()); cols=st.columns(4); cols[0].metric("Recall@5",f"{m.get('Recall@5',0):.1%}"); cols[1].metric("MRR",f"{m.get('MRR',0):.1%}"); cols[2].metric("Faithfulness",f"{m.get('Faithfulness',0):.1%}"); cols[3].metric("p95 latency",f"{m.get('p95_latency',0)} ms")
st.divider(); q=st.text_input("Ask the knowledge base");
if st.button("Query") and q:
 try: st.json(requests.post(api+"/query",json={"question":q},timeout=60).json())
 except Exception as e: st.error(str(e))
