import re
from src.citation_validator import validate_answer

def keyword_recall(answer,expected_keywords):
    a=answer.lower(); return sum(k.lower() in a for k in expected_keywords)/max(1,len(expected_keywords))

def faithfulness_heuristic(answer,citations):
    if not citations:return 0.0
    words={w.lower() for w in re.findall(r"\b\w{4,}\b",answer) if not w.startswith("doc_")}
    ctx={w.lower() for c in citations for w in re.findall(r"\b\w{4,}\b",c.get("text", ""))}
    return round(len(words&ctx)/max(1,len(words)),3)

def answer_relevancy_heuristic(answer,question):
    q={w.lower() for w in re.findall(r"\b\w{3,}\b",question)}; a={w.lower() for w in re.findall(r"\b\w{3,}\b",answer)}; return len(q&a)/max(1,len(q))

def citation_correctness(answer,citations):
    return validate_answer(answer,citations).get("score",0.0)

faithfulness=faithfulness_heuristic; answer_relevancy=answer_relevancy_heuristic
