import os
import re
from typing import Dict


# Soft dependency: OpenAI. We fall back to heuristic if unavailable or no key.
USE_OPENAI = False
try:
    from openai import OpenAI
    USE_OPENAI = True
except Exception:
    USE_OPENAI = False


DEFAULT_MODEL = os.getenv("MODEL_NAME", "gpt-4o-mini")


PII_REGEXES = [
re.compile(r"\\b\\d{3}-\\d{2}-\\d{4}\\b"), # SSN-like
re.compile(r"\\b\\d{10,16}\\b"), # long digit sequences (phones/cards)
re.compile(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\\.[A-Z]{2,}", re.I), # emails
]


SENTIMENT_WORDS = {
"positive": ["great", "good", "excellent", "helpful", "kind", "caring", "amazing", "thank"],
"negative": ["bad", "rude", "slow", "terrible", "awful", "pain", "wait", "dirty", "unsafe"],
}


def _heuristic_analysis(text: str) -> Dict:
    low = text.lower()
    pos = sum(w in low for w in SENTIMENT_WORDS["positive"])
    neg = sum(w in low for w in SENTIMENT_WORDS["negative"])
    sentiment = "neutral"
    if pos > neg: sentiment = "positive"
    elif neg > pos: sentiment = "negative"


    topics = []
    for t in ["nursing", "billing", "food", "wait", "cleanliness", "safety", "doctor", "communication"]:
        if t in low: topics.append(t)


    pii = any(r.search(text) for r in PII_REGEXES)


    # naive summary: first sentence (truncate)
    first = re.split(r"[\.!?]", text.strip())[0][:240]
    return {
    "summary": first,
    "sentiment": sentiment,
    "topics": ",".join(topics) if topics else None,
    "pii_detected": bool(pii),
    }


def analyze_with_llm(text: str) -> Dict:
    api_key = os.getenv("OPENAI_API_KEY")
    if not (USE_OPENAI and api_key):
        return _heuristic_analysis(text)


    client = OpenAI(api_key=api_key)
    system = (
    "You are a clinical feedback analyst. Extract a concise summary (<=40 words), "
    "sentiment {positive|neutral|negative}, up to 3 topical tags, and whether PII is present. "
    "Return strict JSON with keys: summary, sentiment, topics (array), pii_detected (bool)."
    )
    user = f"Text:\n{text}"


    resp = client.chat.completions.create(
    model=os.getenv("MODEL_NAME", DEFAULT_MODEL),
    messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
    temperature=0.2,
    )
    content = resp.choices[0].message.content # expecting JSON


    # Defensive parse to plain dict
    import json
    try:
        data = json.loads(content)
        return {
        "summary": data.get("summary"),
        "sentiment": data.get("sentiment"),
        "topics": ",".join(data.get("topics", [])) if isinstance(data.get("topics"), list) else data.get("topics"),
        "pii_detected": bool(data.get("pii_detected")),
        }
    except Exception:
    # fallback if model returns non-JSON
        return _heuristic_analysis(text)
