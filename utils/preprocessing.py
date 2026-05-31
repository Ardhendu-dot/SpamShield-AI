"""Text preprocessing utilities for SpamShield AI.

Lowercase -> strip punctuation -> tokenize -> remove stopwords -> stem.
"""
from __future__ import annotations

import re
import string
from functools import lru_cache

import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize


def _ensure_nltk() -> None:
    for pkg in ("punkt", "punkt_tab", "stopwords"):
        try:
            nltk.data.find(f"tokenizers/{pkg}" if "punkt" in pkg else f"corpora/{pkg}")
        except LookupError:
            try:
                nltk.download(pkg, quiet=True)
            except Exception:
                pass


_ensure_nltk()
_STEMMER = PorterStemmer()


@lru_cache(maxsize=1)
def _stopwords() -> set[str]:
    try:
        return set(stopwords.words("english"))
    except Exception:
        return set()


_URL_RE = re.compile(r"https?://\S+|www\.\S+")
_NUM_RE = re.compile(r"\b\d+\b")


def clean_text(text: str) -> str:
    """Full preprocessing pipeline returning a normalized token string."""
    if not text:
        return ""
    t = text.lower()
    t = _URL_RE.sub(" urltoken ", t)
    t = _NUM_RE.sub(" numtoken ", t)
    t = t.translate(str.maketrans("", "", string.punctuation))
    try:
        tokens = word_tokenize(t)
    except Exception:
        tokens = t.split()
    sw = _stopwords()
    tokens = [_STEMMER.stem(tok) for tok in tokens if tok and tok not in sw and len(tok) > 1]
    return " ".join(tokens)


DANGEROUS_KEYWORDS = [
    "lottery", "winner", "free", "urgent", "click", "claim", "prize",
    "verify", "bank", "wire", "bitcoin", "crypto", "gift", "card",
    "congratulations", "selected", "password", "ssn", "irs", "refund",
    "suspended", "act now", "limited time",
]


def find_suspicious(text: str) -> list[str]:
    low = text.lower()
    return sorted({k for k in DANGEROUS_KEYWORDS if k in low})


def has_suspicious_url(text: str) -> bool:
    for url in _URL_RE.findall(text):
        # shortened, IP-address, or look-alike domains
        if any(s in url for s in ("bit.ly", "tinyurl", "goo.gl", "t.co", "ow.ly")):
            return True
        if re.search(r"https?://\d+\.\d+\.\d+\.\d+", url):
            return True
        if re.search(r"paypa1|g00gle|micr0soft|amaz0n|app1e", url, re.I):
            return True
    return False
