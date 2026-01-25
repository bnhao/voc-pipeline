import pandas as pd
from transformers import pipeline
from sklearn.metrics import classification_report

# 1. Data Cleaning (Pandas/SQL focus)
def clean_feedback(text):
    return text.strip().lower()

# 2. NLP Pipeline (BERT focus)
# We use a pre-trained BERT-based model for sentiment analysis
classifier = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")

def analyze_sentiment(data):
    results = classifier(data['text'].tolist())
    data['sentiment'] = [r['label'] for r in results]
    data['confidence'] = [r['score'] for r in results]
    return data

# 3. Model Evaluation (Benchmarking focus)
def benchmark_model(y_true, y_pred):
    print("Model Performance Metrics:")
    print(classification_report(y_true, y_pred))