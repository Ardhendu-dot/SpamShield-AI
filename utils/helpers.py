"""Threat-level and category helpers."""
from __future__ import annotations

from datetime import datetime
from typing import Any


CATEGORY_EMOJI = {
    "Spam": "🚫",
    "Safe": "✅",
    "Promotional": "📣",
    "Scam": "⚠️",
    "Advertisement": "📢",
}

CATEGORY_COLOR = {
    "Spam":          "#F5B547",
    "Safe":          "#39E6A0",
    "Promotional":   "#5B8CFF",
    "Scam":          "#FF5A6E",
    "Advertisement": "#B66BFF",
}


def threat_level(category: str, confidence: float, phishing_prob: float) -> str:
    if category == "Scam" or phishing_prob >= 75:
        return "Critical"
    if category == "Spam" and confidence >= 70:
        return "High"
    if category in ("Spam", "Promotional", "Advertisement"):
        return "Medium"
    return "Low"


def now_iso() -> str:
    return datetime.utcnow().isoformat(timespec="seconds") + "Z"


def safer_alternative(category: str) -> str | None:
    if category == "Scam":
        return "Do NOT reply, click, or share information. Report and delete."
    if category == "Spam":
        return "Mark as spam and unsubscribe using a verified channel."
    if category == "Promotional":
        return "Verify the sender domain before clicking. Unsubscribe if unwanted."
    return None


def cyber_tip(category: str) -> str:
    tips = {
        "Scam": "Never share OTPs, passwords, or banking details over email/SMS.",
        "Spam": "Hover over links to inspect the real URL before clicking.",
        "Promotional": "Use a secondary email for newsletter subscriptions.",
        "Advertisement": "Use a tracker-blocker; check sender authenticity.",
        "Safe": "Always verify unexpected attachments — even from known senders.",
    }
    return tips.get(category, "Stay vigilant — when in doubt, do not click.")


def normalize_scores(scores: dict[str, float]) -> dict[str, float]:
    total = sum(scores.values()) or 1.0
    return {k: round(v / total * 100, 2) for k, v in scores.items()}
