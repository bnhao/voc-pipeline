import json
import os
import pandas as pd
from sklearn.metrics import f1_score, precision_score, recall_score, accuracy_score, confusion_matrix, classification_report

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
SRC_DIR = os.path.join(BASE_DIR, "src")
PUBLIC_DATA_DIR = os.path.join(BASE_DIR, "public", "data")


def build_bundle():
    os.makedirs(PUBLIC_DATA_DIR, exist_ok=True)

    raw_path = os.path.join(DATA_DIR, "atb_large_dataset.csv")
    clean_path = os.path.join(DATA_DIR, "clean_feedback.csv")
    scored_path = os.path.join(DATA_DIR, "scored_feedback_final.csv")
    report_path = os.path.join(DATA_DIR, "CX_Executive_Report.md")

    raw_df = pd.read_csv(raw_path)
    clean_df = pd.read_csv(clean_path)
    scored_df = pd.read_csv(scored_path)

    with open(report_path, "r", encoding="utf-8") as f:
        executive_report_md = f.read()

    # Metrics calculation
    y_true = scored_df["ground_truth_simulated"]
    y_pred = scored_df["predicted_sentiment"]
    labels = ["Negative", "Neutral", "Positive"]

    f1_w = float(f1_score(y_true, y_pred, average="weighted", zero_division=0))
    precision_w = float(precision_score(y_true, y_pred, average="weighted", zero_division=0))
    recall_w = float(recall_score(y_true, y_pred, average="weighted", zero_division=0))
    acc = float(accuracy_score(y_true, y_pred))
    cm = confusion_matrix(y_true, y_pred, labels=labels).tolist()
    cls_report = classification_report(y_true, y_pred, labels=labels, output_dict=True, zero_division=0)

    sentiment_counts = scored_df["predicted_sentiment"].value_counts().to_dict()
    avg_confidence = float(scored_df["confidence_score"].mean())
    high_conf_count = int((scored_df["confidence_score"] >= 0.85).sum())

    # Group breakdowns
    def group_breakdown(col):
        rows = []
        for name, grp in scored_df.groupby(col):
            vc = grp["predicted_sentiment"].value_counts().to_dict()
            total = len(grp)
            neg = int(vc.get("Negative", 0))
            neu = int(vc.get("Neutral", 0))
            pos = int(vc.get("Positive", 0))
            rows.append({
                "name": str(name),
                "total": total,
                "Negative": neg,
                "Neutral": neu,
                "Positive": pos,
                "negative_pct": round((neg / total) * 100, 1) if total else 0,
                "positive_pct": round((pos / total) * 100, 1) if total else 0,
                "avg_confidence": round(float(grp["confidence_score"].mean()), 4),
            })
        rows.sort(key=lambda r: r["total"], reverse=True)
        return rows

    by_branch = group_breakdown("branch")
    by_product = group_breakdown("product")
    by_source = group_breakdown("source")

    # Monthly trend
    scored_df["month"] = pd.to_datetime(scored_df["date"], errors="coerce").dt.strftime("%Y-%m")
    by_month = []
    for month, grp in scored_df.groupby("month"):
        if pd.isna(month):
            continue
        vc = grp["predicted_sentiment"].value_counts().to_dict()
        by_month.append({
            "month": str(month),
            "total": len(grp),
            "Negative": int(vc.get("Negative", 0)),
            "Neutral": int(vc.get("Neutral", 0)),
            "Positive": int(vc.get("Positive", 0)),
        })
    by_month.sort(key=lambda r: r["month"])

    # Confidence histogram
    bins = [0.0, 0.6, 0.7, 0.8, 0.9, 1.01]
    bin_labels = ["< 60%", "60–70%", "70–80%", "80–90%", "90–100%"]
    scored_df["conf_bin"] = pd.cut(scored_df["confidence_score"], bins=bins, labels=bin_labels, right=False)
    conf_hist = []
    for b_label in bin_labels:
        sub = scored_df[scored_df["conf_bin"] == b_label]
        vc = sub["predicted_sentiment"].value_counts().to_dict()
        conf_hist.append({
            "bucket": b_label,
            "count": int(len(sub)),
            "Negative": int(vc.get("Negative", 0)),
            "Neutral": int(vc.get("Neutral", 0)),
            "Positive": int(vc.get("Positive", 0)),
        })

    # Real cleaning examples (including dropped/noisy rows from raw_df)
    cleaning_examples = []
    null_rows = raw_df[raw_df["client_comment"].isna()].head(2)
    for _, r in null_rows.iterrows():
        cleaning_examples.append({
            "feedback_id": str(r["feedback_id"])[:8],
            "branch": str(r["branch"]),
            "raw": "None / NaN (Missing Survey Comment)",
            "cleaned": "",
            "status": "Dropped (Empty/Null)",
        })
    special_rows = raw_df[raw_df["client_comment"].astype(str).str.contains(r"\?\?\?|@@", regex=True, na=False)].head(4)
    for _, r in special_rows.iterrows():
        raw_txt = str(r["client_comment"])
        matched = clean_df[clean_df["feedback_id"] == r["feedback_id"]]
        if len(matched) > 0:
            cleaned_txt = str(matched.iloc[0]["clean_comment"])
            status = "Normalized & Retained"
        else:
            cleaned_txt = ""
            status = "Dropped (Special Chars Only)"
        cleaning_examples.append({
            "feedback_id": str(r["feedback_id"])[:8],
            "branch": str(r["branch"]),
            "raw": raw_txt,
            "cleaned": cleaned_txt,
            "status": status,
        })
    normal_rows = clean_df.head(4)
    for _, r in normal_rows.iterrows():
        cleaning_examples.append({
            "feedback_id": str(r["feedback_id"])[:8],
            "branch": str(r["branch"]),
            "raw": str(r["client_comment"]),
            "cleaned": str(r["clean_comment"]),
            "status": "Normalized & Retained",
        })

    # Source files
    source_files = {}
    for fname in ["00_generate_data.py", "01_data_ingestion.py", "02_sentiment_analysis", "03_executive_reporting.py"]:
        fpath = os.path.join(SRC_DIR, fname)
        if os.path.exists(fpath):
            with open(fpath, "r", encoding="utf-8") as f:
                source_files[fname] = f.read()

    # All scored records for interactive exploration
    records = []
    for _, r in scored_df.iterrows():
        records.append({
            "id": str(r["feedback_id"]),
            "date": str(r["date"]),
            "branch": str(r["branch"]),
            "product": str(r["product"]),
            "comment": str(r["client_comment"]),
            "clean": str(r["clean_comment"]),
            "source": str(r["source"]),
            "sentiment": str(r["predicted_sentiment"]),
            "confidence": round(float(r["confidence_score"]), 4),
            "ground_truth": str(r["ground_truth_simulated"]),
        })

    bundle = {
        "generated_at": "2026-10-31",
        "summary": {
            "raw_records": int(len(raw_df)),
            "clean_records": int(len(clean_df)),
            "dropped_records": int(len(raw_df) - len(clean_df)),
            "scored_records": int(len(scored_df)),
            "sentiment_counts": {
                "Negative": int(sentiment_counts.get("Negative", 0)),
                "Neutral": int(sentiment_counts.get("Neutral", 0)),
                "Positive": int(sentiment_counts.get("Positive", 0)),
            },
            "avg_confidence": round(avg_confidence, 4),
            "high_confidence_count": high_conf_count,
            "metrics": {
                "f1_weighted": round(f1_w, 4),
                "precision_weighted": round(precision_w, 4),
                "recall_weighted": round(recall_w, 4),
                "accuracy": round(acc, 4),
                "confusion_matrix": cm,
                "labels": labels,
                "classification_report": cls_report,
            },
            "model_name": "cardiffnlp/twitter-roberta-base-sentiment",
            "llm_model": "gemini-2.5-flash",
        },
        "by_branch": by_branch,
        "by_product": by_product,
        "by_source": by_source,
        "by_month": by_month,
        "confidence_histogram": conf_hist,
        "cleaning_examples": cleaning_examples,
        "executive_report": executive_report_md,
        "source_files": source_files,
        "records": records,
    }

    out_file = os.path.join(PUBLIC_DATA_DIR, "pipeline_bundle.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(bundle, f, separators=(",", ":"))

    print(f"✅ Generated {out_file} ({os.path.getsize(out_file) / 1024:.1f} KB)")
    return bundle


if __name__ == "__main__":
    build_bundle()
