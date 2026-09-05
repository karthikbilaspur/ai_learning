"""Deterministic citation validation for generated RAG answers."""
import re
from typing import Dict, List, Tuple

_CIT_RE = re.compile(r"\[([^\]:\s]+):([^\]\s]+)\]")
_WORD_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]{2,}")
_STOP = {"the","and","for","with","that","this","from","what","does","how","are","was","were","into","about","using","used","their","there","have","has","its","also","than","then","they","them","you","your","can","may","will","would","could","should"}

def extract_citations(text: str) -> List[Tuple[str, str]]:
    return _CIT_RE.findall(text or "")

def _tokens(text: str) -> set:
    return {w.lower() for w in _WORD_RE.findall(text or "") if w.lower() not in _STOP}

def _split_claims(answer: str) -> List[str]:
    clean = _CIT_RE.sub("", answer or "")
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+|\n+", clean) if len(_tokens(s)) >= 2]

def validate_answer(answer: str, citations: List[Dict], min_overlap: float = 0.22) -> Dict:
    """Check both citation validity and whether citations support each factual claim.

    A citation is correct only if its doc/chunk exists in retrieved context and its
    source has sufficient meaningful-token overlap with the associated claim.
    """
    by_id = {(str(c.get("doc_id")), str(c.get("chunk_id"))): c for c in citations}
    claims = _split_claims(answer)
    cited = extract_citations(answer)
    valid_citations = 0
    unsupported_citations = []
    for doc_id, chunk_id in cited:
        if (doc_id, chunk_id) in by_id:
            valid_citations += 1
        else:
            unsupported_citations.append(f"[{doc_id}:{chunk_id}]")

    claim_results = []
    for claim in claims:
        claim_tokens = _tokens(claim)
        refs = extract_citations(claim)
        # If citations occur after punctuation, associate the nearest citation in the answer.
        if not refs:
            before = answer[: max(0, answer.find(claim))]
            after = answer[answer.find(claim) + len(claim):]
            refs = extract_citations(after[:80]) or extract_citations(before[-80:])
        best = 0.0
        best_ref = None
        for ref in refs:
            source = by_id.get(ref)
            if not source:
                continue
            source_tokens = _tokens(source.get("text", ""))
            overlap = len(claim_tokens & source_tokens) / max(1, len(claim_tokens))
            if overlap > best:
                best, best_ref = overlap, ref
        supported = best >= min_overlap
        claim_results.append({"claim": claim, "supported": supported, "overlap": round(best, 3), "citation": best_ref})

    all_claims_supported = bool(claim_results) and all(x["supported"] for x in claim_results)
    return {
        "valid": all_claims_supported and bool(cited) and valid_citations == len(cited),
        "citation_count": len(cited),
        "valid_citation_count": valid_citations,
        "invalid_citations": unsupported_citations,
        "claims": claim_results,
        "score": round(sum(x["supported"] for x in claim_results) / max(1, len(claim_results)), 3),
    }
