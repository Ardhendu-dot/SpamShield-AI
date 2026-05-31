"""SpamShield AI classifier wrapper.

Loads the trained TF-IDF + Multinomial Naive Bayes pipeline and exposes a
single `predict()` function returning a rich JSON-style report — confidence
scores per class, threat level, suspicious keywords, phishing probability,
and human-readable reasoning.
"""
from __future__ import annotations

import os
import pickle
from typing import Any

import numpy as np

from utils.preprocessing import clean_text, find_suspicious, has_suspicious_url
from utils.helpers import (
    CATEGORY_EMOJI, cyber_tip, normalize_scores, now_iso, safer_alternative,
    threat_level,
)

MODEL_DIR = os.path.join(os.path.dirname(__file__), "model")
MODEL_PATH = os.path.join(MODEL_DIR, "model.pkl")
VECTORIZER_PATH = os.path.join(MODEL_DIR, "vectorizer.pkl")

# Binary model classes (spam/ham). We re-distribute probability mass across
# 5 categories using lightweight content heuristics so the UI always shows
# a 5-way breakdown — the heart of "Spam vs Safe vs Promotional vs Scam vs Ad".
CATEGORIES = ["Spam", "Safe", "Promotional", "Scam", "Advertisement"]


class SpamShieldModel:
    def __init__(self) -> None:
        self._model = None
        self._vectorizer = None

    def _load(self) -> None:
        if self._model is not None:
            return
        if not (os.path.exists(MODEL_PATH) and os.path.exists(VECTORIZER_PATH)):
            raise FileNotFoundError(
                "Model files not found. Run `python train_model.py` first."
            )
        with open(MODEL_PATH, "rb") as f:
            self._model = pickle.load(f)
        with open(VECTORIZER_PATH, "rb") as f:
            self._vectorizer = pickle.load(f)

    # --------------------------------------------------------------- public
    def predict(self, text: str) -> dict[str, Any]:
        self._load()
        cleaned = clean_text(text)
        X = self._vectorizer.transform([cleaned])
        proba = self._model.predict_proba(X)[0]  # [ham, spam]
        classes = list(self._model.classes_)
        spam_idx = classes.index(1) if 1 in classes else classes.index("spam")
        ham_idx = 1 - spam_idx
        spam_p = float(proba[spam_idx]) * 100
        ham_p = float(proba[ham_idx]) * 100

        keywords = find_suspicious(text)
        url_flag = has_suspicious_url(text)
        low = text.lower()

        # Heuristic 5-way distribution
        scam_signal = sum(
            w in low for w in ("lottery", "winner", "prize", "wire", "verify", "bank", "password", "bitcoin")
        ) + (3 if url_flag else 0)
        promo_signal = sum(
            w in low for w in ("sale", "discount", "% off", "promo", "deal", "coupon")
        )
        ad_signal = sum(
            w in low for w in ("ad", "advertisement", "sponsored", "buy now", "shop now")
        )

        scores = {
            "Spam":          spam_p * 0.55,
            "Scam":          spam_p * (0.25 + 0.06 * scam_signal),
            "Promotional":   max(2.0, ham_p * 0.25 + 6 * promo_signal),
            "Advertisement": max(2.0, ham_p * 0.15 + 6 * ad_signal),
            "Safe":          ham_p * 0.60,
        }
        scores = normalize_scores(scores)
        category = max(scores, key=scores.get)
        confidence = scores[category]
        phishing = round(min(100.0, spam_p * 0.7 + 20 * scam_signal + (15 if url_flag else 0)), 2)

        reasoning = self._reason(text, scores, keywords, url_flag, category)

        return {
            "timestamp": now_iso(),
            "category": category,
            "category_icon": CATEGORY_EMOJI.get(category, "❔"),
            "confidence": confidence,
            "scores": scores,
            "threat_level": threat_level(category, confidence, phishing),
            "phishing_probability": phishing,
            "has_suspicious_url": url_flag,
            "suspicious_keywords": keywords,
            "safer_alternative": safer_alternative(category),
            "cybersecurity_tip": cyber_tip(category),
            "reasoning": reasoning,
            "raw_text": text,
        }

    @staticmethod
    def _reason(text: str, scores: dict[str, float], kws: list[str],
                url: bool, cat: str) -> str:
        bits = [f"Top class **{cat}** ({scores[cat]:.0f}%)."]
        if kws:
            bits.append(f"Flagged keywords: {', '.join(kws[:6])}.")
        if url:
            bits.append("Suspicious URL pattern detected.")
        if len(text) < 30:
            bits.append("Very short message — limited signal.")
        return " ".join(bits)


_MODEL = SpamShieldModel()


def predict(text: str) -> dict[str, Any]:
    """Convenience wrapper."""
    return _MODEL.predict(text)
