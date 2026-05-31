"""Train the SpamShield AI baseline classifier.

- TF-IDF vectorizer
- Multinomial Naive Bayes (primary)
- Logistic Regression comparison
- Saves: model/model.pkl, model/vectorizer.pkl, model/metrics.json
"""
from __future__ import annotations

import json
import os
import pickle

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score, classification_report, confusion_matrix, f1_score,
)
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB

from utils.preprocessing import clean_text

DATA_PATH = os.path.join(os.path.dirname(__file__), "dataset", "spam.csv")
MODEL_DIR = os.path.join(os.path.dirname(__file__), "model")
os.makedirs(MODEL_DIR, exist_ok=True)


def load_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH, encoding="latin-1")
    df = df.rename(columns={c: c.strip() for c in df.columns})
    # Accept either ("label","text") or ("v1","v2") UCI format
    if "label" not in df.columns:
        df = df.rename(columns={"v1": "label", "v2": "text"})
    df = df[["label", "text"]].dropna()
    df["label"] = df["label"].map(lambda x: 1 if str(x).lower().strip() in ("spam", "1", "true") else 0)
    df["text"] = df["text"].astype(str)
    return df


def main() -> None:
    print("📦 Loading dataset...")
    df = load_data()
    print(f"   {len(df)} rows | spam ratio: {df['label'].mean():.2%}")

    print("🧹 Preprocessing...")
    df["clean"] = df["text"].map(clean_text)

    X_train, X_test, y_train, y_test = train_test_split(
        df["clean"], df["label"], test_size=0.2, random_state=42, stratify=df["label"],
    )

    print("🔠 Vectorizing (TF-IDF)...")
    vectorizer = TfidfVectorizer(max_features=5000, ngram_range=(1, 2), min_df=2)
    Xtr = vectorizer.fit_transform(X_train)
    Xte = vectorizer.transform(X_test)

    print("🧠 Training Multinomial Naive Bayes...")
    nb = MultinomialNB()
    nb.fit(Xtr, y_train)
    nb_pred = nb.predict(Xte)
    nb_acc = accuracy_score(y_test, nb_pred)
    nb_f1 = f1_score(y_test, nb_pred)

    print("🧠 Training Logistic Regression (comparison)...")
    lr = LogisticRegression(max_iter=1000, C=4.0)
    lr.fit(Xtr, y_train)
    lr_pred = lr.predict(Xte)
    lr_acc = accuracy_score(y_test, lr_pred)
    lr_f1 = f1_score(y_test, lr_pred)

    # Pick best by F1
    best_name, best_model, best_acc, best_f1, best_pred = max(
        [("naive_bayes", nb, nb_acc, nb_f1, nb_pred),
         ("logistic_regression", lr, lr_acc, lr_f1, lr_pred)],
        key=lambda t: t[3],
    )
    print(f"🏆 Best model: {best_name} | acc={best_acc:.4f} | f1={best_f1:.4f}")

    metrics = {
        "best_model": best_name,
        "best_accuracy": round(best_acc, 4),
        "best_f1": round(best_f1, 4),
        "naive_bayes": {"accuracy": round(nb_acc, 4), "f1": round(nb_f1, 4)},
        "logistic_regression": {"accuracy": round(lr_acc, 4), "f1": round(lr_f1, 4)},
        "confusion_matrix": confusion_matrix(y_test, best_pred).tolist(),
        "classification_report": classification_report(y_test, best_pred, output_dict=True),
        "n_train": int(len(X_train)),
        "n_test": int(len(X_test)),
    }

    with open(os.path.join(MODEL_DIR, "model.pkl"), "wb") as f:
        pickle.dump(best_model, f)
    with open(os.path.join(MODEL_DIR, "vectorizer.pkl"), "wb") as f:
        pickle.dump(vectorizer, f)
    with open(os.path.join(MODEL_DIR, "metrics.json"), "w") as f:
        json.dump(metrics, f, indent=2)

    print("💾 Saved model/model.pkl, model/vectorizer.pkl, model/metrics.json")


if __name__ == "__main__":
    main()
