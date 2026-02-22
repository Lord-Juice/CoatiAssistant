from __future__ import annotations

import re
from typing import Dict, Iterable

# Minimal synonym/alias map (extend as you like)
SYNONYMS: Dict[str, str] = {
    "portemonnaie": "wallet",
    "geldbeutel": "wallet",
    "börse": "wallet",
    "schlüssel": "keys",
    "handy": "phone",
    "telefon": "phone",
}

STOPWORDS = {
    "mein", "meine", "meinen", "meinem", "meiner",
    "your", "my", "the", "a", "an",
    "bitte", "pls", "please",
}


def normalize_text(s: str) -> str:
    s = s.strip().lower()
    s = re.sub(r"[^\w\s-]", " ", s, flags=re.UNICODE)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def canonical_entity(raw: str) -> str:
    """
    Convert a user phrase like "mein Portemonnaie" -> "wallet"
    Deterministic, no LLM required.
    """
    s = normalize_text(raw)

    # quick synonym replace per token
    tokens = [t for t in s.split() if t not in STOPWORDS]
    if not tokens:
        return s or "unknown"

    # If the phrase contains a known synonym anywhere, return that canonical
    for t in tokens:
        if t in SYNONYMS:
            return SYNONYMS[t]

    # Otherwise: use last token as a pragmatic default ("wallet", "keys", ...)
    # You can replace this with a more advanced noun-chunk extractor later.
    return tokens[-1]


def key_for_entity(canonical: str) -> str:
    return f"entity:{canonical}"


def extract_aliases(raw: str) -> list[str]:
    s = normalize_text(raw)
    tokens = [t for t in s.split() if t and t not in STOPWORDS]
    # keep short alias list, unique
    seen = set()
    out: list[str] = []
    for t in tokens:
        if t not in seen:
            seen.add(t)
            out.append(t)
    # add synonym canonical if present
    for t in list(out):
        if t in SYNONYMS and SYNONYMS[t] not in out:
            out.append(SYNONYMS[t])
    return out[:10]