"""SpamShield AI — Streamlit dashboard."""
from __future__ import annotations

import json
import os
from datetime import datetime

import pandas as pd
import streamlit as st

from spam_classifier import predict
from utils.helpers import CATEGORY_COLOR, CATEGORY_EMOJI
from utils.visualizations import (
    category_pie, confidence_bar, keyword_bar, timeline,
)

st.set_page_config(
    page_title="SpamShield AI — Cyber Threat Intelligence",
    page_icon="🛡️", layout="wide", initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------- styling
st.markdown("""
<style>
  .stApp { background:
    radial-gradient(ellipse at top left, rgba(91,140,255,.18), transparent 50%),
    radial-gradient(ellipse at bottom right, rgba(182,107,255,.15), transparent 50%),
    #0B0E1A; }
  section[data-testid="stSidebar"] { background: #0A0D18; border-right: 1px solid rgba(255,255,255,.08); }
  .glass {
    background: linear-gradient(135deg, rgba(255,255,255,.06), rgba(255,255,255,.02));
    border: 1px solid rgba(255,255,255,.08);
    border-radius: 14px; padding: 18px; backdrop-filter: blur(14px);
  }
  .cyber-title {
    background: linear-gradient(135deg,#5B8CFF,#B66BFF);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    font-weight: 800;
  }
  .verdict {
    border-radius: 16px; padding: 20px;
    color: white; font-weight: 700; font-size: 22px;
    box-shadow: 0 0 40px -10px rgba(91,140,255,.6);
  }
  .badge {
    display:inline-block; padding:4px 10px; border-radius:999px;
    font-size:11px; font-weight:600; letter-spacing:.08em; text-transform:uppercase;
  }
  .kw {
    display:inline-block; background:rgba(255,90,110,.18); color:#FF8A99;
    border:1px solid rgba(255,90,110,.35); padding:2px 8px; border-radius:8px;
    font-family:monospace; font-size:12px; margin:2px 4px 2px 0;
  }
  .stButton>button {
    background: linear-gradient(135deg,#5B8CFF,#B66BFF);
    color:#0B0E1A; border:0; font-weight:700; border-radius:10px;
    box-shadow: 0 0 30px -10px rgba(91,140,255,.7);
  }
  mark { background: rgba(255,90,110,.25); color:#FF8A99; padding:0 3px; border-radius:4px; }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------- session
if "history" not in st.session_state:
    st.session_state.history = []

# ---------------------------------------------------------------- sidebar
with st.sidebar:
    st.markdown("## 🛡️ **SpamShield AI**")
    st.caption("Cyber Threat Intelligence")
    page = st.radio(
        "Navigation",
        ["🚀 Command Center", "🔍 Threat Scanner", "📊 Analytics",
         "🗂️ Detection History", "ℹ️ About"],
        label_visibility="collapsed",
    )
    st.markdown("---")
    st.markdown("🟢 **AI Engine Online**")
    st.caption("scikit-learn · NLP · Real-time")

# ---------------------------------------------------------------- pages
def page_home() -> None:
    st.markdown("## <span class='cyber-title'>Neural spam & scam detection at the edge.</span>",
                unsafe_allow_html=True)
    st.write(
        "SpamShield AI classifies any message as **Spam · Safe · Promotional · Scam · "
        "Advertisement** with confidence scoring, phishing probability and "
        "cyber recommendations."
    )
    h = st.session_state.history
    total = len(h)
    threats = sum(1 for x in h if x["category"] in ("Spam", "Scam"))
    safe = sum(1 for x in h if x["category"] == "Safe")
    avg_conf = round(sum(x["confidence"] for x in h) / total, 1) if total else 99.0
    c1, c2, c3, c4 = st.columns(4)
    for col, (label, val) in zip(
        (c1, c2, c3, c4),
        [("Total Scans", total), ("Threats Blocked", threats),
         ("Safe Messages", safe), ("Avg. Confidence", f"{avg_conf}%")],
    ):
        with col:
            st.markdown(f"<div class='glass'><div style='opacity:.7;font-size:11px;"
                        f"letter-spacing:.15em;text-transform:uppercase'>{label}</div>"
                        f"<div style='font-size:28px;font-weight:800;margin-top:6px;'>{val}</div>"
                        "</div>", unsafe_allow_html=True)

def render_verdict(r: dict) -> None:
    color = CATEGORY_COLOR.get(r["category"], "#5B8CFF")
    st.markdown(
        f"<div class='verdict' style='background:linear-gradient(135deg,{color},#5B8CFF);'>"
        f"{r['category_icon']} &nbsp; {r['category']} "
        f"<span style='float:right'>{r['confidence']:.0f}% confidence</span></div>",
        unsafe_allow_html=True,
    )
    threat_colors = {"Low":"#39E6A0","Medium":"#F5B547","High":"#FF8A55","Critical":"#FF5A6E"}
    tc = threat_colors[r["threat_level"]]
    st.markdown(
        f"<p style='margin-top:10px'>Threat level: "
        f"<span class='badge' style='background:{tc}22;color:{tc};border:1px solid {tc}66'>"
        f"{r['threat_level']}</span></p>", unsafe_allow_html=True,
    )

    st.plotly_chart(confidence_bar(r["scores"]), use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"<div class='glass'><b>Phishing probability</b><br>"
                    f"<span style='font-size:24px;color:#FF5A6E'>{r['phishing_probability']:.0f}%</span></div>",
                    unsafe_allow_html=True)
    with c2:
        flag = "Detected" if r["has_suspicious_url"] else "None"
        color = "#FF5A6E" if r["has_suspicious_url"] else "#39E6A0"
        st.markdown(f"<div class='glass'><b>Suspicious URL</b><br>"
                    f"<span style='font-size:24px;color:{color}'>{flag}</span></div>",
                    unsafe_allow_html=True)

    if r["suspicious_keywords"]:
        st.markdown("**Flagged keywords**")
        st.markdown(" ".join(f"<span class='kw'>{k}</span>" for k in r["suspicious_keywords"]),
                    unsafe_allow_html=True)

    st.info(f"🧠 **AI Reasoning** — {r['reasoning']}")
    st.success(f"🛡️ **Cyber tip** — {r['cybersecurity_tip']}")
    if r.get("safer_alternative"):
        st.warning(f"✅ **Safer alternative** — {r['safer_alternative']}")

    rcol1, rcol2 = st.columns(2)
    rcol1.download_button("⬇️ Export JSON report",
        data=json.dumps(r, indent=2), file_name=f"spamshield-{int(datetime.now().timestamp())}.json",
        mime="application/json", use_container_width=True)
    rcol2.download_button("⬇️ Export CSV row",
        data=pd.DataFrame([r]).to_csv(index=False),
        file_name=f"spamshield-{int(datetime.now().timestamp())}.csv",
        mime="text/csv", use_container_width=True)

def page_scanner() -> None:
    st.markdown("## <span class='cyber-title'>Threat Scanner</span>", unsafe_allow_html=True)
    st.caption("Paste any email, SMS or message — AI classifies it in real time.")
    samples = {
        "Phishing email": "URGENT: Your account has been suspended! Click http://paypa1-secure.com/verify to verify your password now.",
        "Lottery scam":   "CONGRATULATIONS! You are the lucky winner of $5,000,000 USD. Send your bank details to claim.",
        "Safe message":   "Hey, just confirming our meeting tomorrow at 3pm at the coffee shop near campus.",
        "Promotional":    "Spring Sale is here! Get 20% off all running shoes this weekend at Nike.com.",
    }
    s = st.selectbox("Try a sample", ["—"] + list(samples.keys()))
    default = samples[s] if s != "—" else ""
    text = st.text_area("Message", value=default, height=200,
                        placeholder="Paste the suspicious email or message here...")
    if st.button("🔍 Scan Message", use_container_width=True):
        if not text.strip():
            st.error("Paste a message to scan.")
        else:
            with st.spinner("Neural network analyzing tokens..."):
                try:
                    r = predict(text)
                    st.session_state.history.insert(0, r)
                    render_verdict(r)
                except FileNotFoundError as e:
                    st.error(str(e))

def page_analytics() -> None:
    st.markdown("## <span class='cyber-title'>Analytics</span>", unsafe_allow_html=True)
    h = st.session_state.history
    if not h:
        st.info("Run a few scans to populate analytics.")
        return
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Category distribution")
        st.plotly_chart(category_pie(h), use_container_width=True)
    with c2:
        st.subheader("Top suspicious keywords")
        st.plotly_chart(keyword_bar(h), use_container_width=True)
    st.subheader("Detection timeline")
    st.plotly_chart(timeline(h), use_container_width=True)

    metrics_path = os.path.join("model", "metrics.json")
    if os.path.exists(metrics_path):
        with open(metrics_path) as f:
            m = json.load(f)
        st.subheader("Model performance")
        st.json(m)

def page_history() -> None:
    st.markdown("## <span class='cyber-title'>Detection History</span>", unsafe_allow_html=True)
    h = st.session_state.history
    if not h:
        st.info("No scans yet.")
        return
    df = pd.DataFrame([{
        "time": x["timestamp"], "category": x["category"],
        "confidence": x["confidence"], "threat": x["threat_level"],
        "phishing%": x["phishing_probability"], "message": x["raw_text"][:140],
    } for x in h])
    st.dataframe(df, use_container_width=True, height=480)
    st.download_button("⬇️ Export all as CSV", data=df.to_csv(index=False),
                       file_name="spamshield-history.csv", mime="text/csv")
    if st.button("🗑️ Clear history"):
        st.session_state.history = []
        st.rerun()

def page_about() -> None:
    st.markdown("## About <span class='cyber-title'>SpamShield AI</span>", unsafe_allow_html=True)
    st.write(
        "SpamShield AI is a premium cybersecurity SaaS demo combining classical NLP/ML "
        "techniques with modern threat-intelligence heuristics. Every prediction comes "
        "with confidence scores, threat level, phishing probability, and recommendations."
    )
    st.markdown("### AI workflow")
    st.markdown("1. **Preprocessing** — lowercase, punctuation strip, stopword removal, stemming\n"
                "2. **Vectorization** — TF-IDF features\n"
                "3. **Classification** — Naive Bayes (vs. Logistic Regression)\n"
                "4. **Threat scoring** — phishing probability, URL heuristics, keyword highlighting")
    st.markdown("### Tech stack")
    st.write("Python · Streamlit · scikit-learn · NLTK · pandas · NumPy · Plotly · pickle")

# ----------------------------------------------------------------- router
if page == "🚀 Command Center":
    page_home()

elif page == "🔍 Threat Scanner":
    page_scanner()

elif page == "📊 Analytics":
    page_analytics()

elif page == "🗂️ Detection History":
    page_history()

elif page == "ℹ️ About":
    page_about()
