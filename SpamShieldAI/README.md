# 🛡️ SpamShield AI

> **Neural spam, scam & phishing detection — a premium cybersecurity SaaS demo built with Python, Streamlit, scikit-learn and NLP.**

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.36+-FF4B4B?logo=streamlit&logoColor=white)
![scikit-learn](https://img.shields.io/badge/scikit--learn-1.4-F7931E?logo=scikitlearn&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-5B8CFF)

SpamShield AI classifies any message as **Spam · Safe · Promotional · Scam · Advertisement**, with confidence scoring, threat level, phishing probability, suspicious-keyword highlighting and cybersecurity recommendations — wrapped in a futuristic dark dashboard.

---

## ✨ Features

- 🧠 **Real-time AI classification** (TF-IDF + Multinomial Naive Bayes, with Logistic Regression comparison)
- 🔬 **Full NLP pipeline** — lowercase, punctuation strip, stopword removal, stemming, TF-IDF vectorization
- 📊 **Analytics dashboard** — category distribution, top suspicious keywords, detection timeline, model metrics
- 🚨 **Threat-level system** — Low · Medium · High · Critical
- 🔗 **Phishing & URL heuristics** — IP-address URLs, look-alike domains, shortened links
- 🔥 **Dangerous keyword highlighter**
- 🗂️ **Detection history** in session, with **CSV / JSON export**
- 🛡️ **Cyber recommendations** for every verdict
- 🎨 **Premium dark UI** — glassmorphism, neon gradients, animated metrics

---

## 🧱 Architecture

```
SpamShieldAI/
├── app.py                  # Streamlit dashboard
├── train_model.py          # TF-IDF + NB/LR training script
├── spam_classifier.py      # Prediction API (returns rich JSON report)
├── requirements.txt
├── README.md
├── .streamlit/config.toml  # Dark theme
├── model/
│   ├── model.pkl
│   ├── vectorizer.pkl
│   └── metrics.json
├── dataset/spam.csv        # Seed dataset (550 rows)
├── utils/
│   ├── preprocessing.py    # Clean / tokenize / stem / keyword & URL heuristics
│   ├── helpers.py          # Threat-level, tips, safer alternatives
│   └── visualizations.py   # Plotly charts
└── exported_reports/
```

### AI Workflow

```
   raw message
      ▼
  [Preprocessing]  ── lowercase · strip punct · stopwords · stem · token-normalize
      ▼
  [TF-IDF (1-2 grams, 5k features)]
      ▼
  [Naive Bayes  /  Logistic Regression] ── best by F1
      ▼
  [Threat scoring] ── phishing prob · URL heuristics · keyword flags
      ▼
   JSON report ─→ Streamlit UI
```

---

## 🚀 Quick start

```bash
git clone https://github.com/your-username/SpamShieldAI.git
cd SpamShieldAI
pip install -r requirements.txt
python train_model.py        # builds model/model.pkl + vectorizer.pkl
streamlit run app.py
```

The app opens at `http://localhost:8501`.

---

## ☁️ Deployment

### Streamlit Community Cloud
1. Push this repo to GitHub.
2. Go to [share.streamlit.io](https://share.streamlit.io) → **New app**.
3. Pick the repo, set `app.py` as the entrypoint.

### Hugging Face Spaces
1. Create a new Space → SDK: **Streamlit**.
2. Push this repo to the Space.

### Render
1. New → **Web Service**, connect repo.
2. Build: `pip install -r requirements.txt && python train_model.py`
3. Start: `streamlit run app.py --server.port=$PORT --server.address=0.0.0.0`

### Replit
1. Import repo.
2. `.replit` run command: `bash -c "pip install -r requirements.txt && python train_model.py && streamlit run app.py --server.port=8080 --server.address=0.0.0.0"`

---

## 🛠️ Tech stack

Python · Streamlit · scikit-learn · NLTK · pandas · NumPy · Plotly · pickle · fpdf2

---

## 🧭 Future improvements

- Transformer-based classifier (DistilBERT) alongside the NB baseline
- Multilingual detection (XLM-R)
- Voice input via `streamlit-mic-recorder`
- AI chatbot assistant for explaining verdicts
- Persistent storage (SQLite / Supabase)
- Browser extension / Gmail plug-in

---

## 🤝 Contributing

PRs are welcome. Please open an issue first to discuss substantial changes.

---

## 📜 License

MIT
