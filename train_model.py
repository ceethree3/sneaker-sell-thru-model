"""
Binary sell-through classifier: healthy vs. at-risk.

  healthy  = sell_through_rate >= 0.45  (hot + moderate)
  at-risk  = sell_through_rate <  0.45  (slow + dead)

Prediction fires at receipt — only signals available before any sales are used.

Usage:
    python train_model.py
    python train_model.py --db path/to/file.db
    python train_model.py --save        # persists model to models/model.pkl
"""

import argparse
import pickle
import sqlite3
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score
from sklearn.model_selection import LeaveOneOut, cross_val_predict
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

warnings.filterwarnings("ignore")

# ── Constants (must match EDA notebook) ──────────────────────────────────────
HEALTHY_THRESHOLD = 0.45

CAT_FEATURES = ["vendor", "department", "price_tier"]
NUM_FEATURES  = ["avg_retail_price", "receive_month", "units_received"]
FEATURES      = CAT_FEATURES + NUM_FEATURES


# ── Data ─────────────────────────────────────────────────────────────────────

def load_features(db_path: Path) -> pd.DataFrame:
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query("SELECT * FROM sku_sell_through", conn)
    conn.close()

    df["receive_month"] = pd.to_datetime(df["receive_date"]).dt.month
    df["label"] = (df["sell_through_rate"] >= HEALTHY_THRESHOLD).astype(int)
    return df


# ── Pipeline ─────────────────────────────────────────────────────────────────

def build_pipeline(clf) -> Pipeline:
    pre = ColumnTransformer([
        ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), CAT_FEATURES),
        ("num", StandardScaler(), NUM_FEATURES),
    ])
    return Pipeline([("pre", pre), ("clf", clf)])


# ── Evaluation ───────────────────────────────────────────────────────────────

def evaluate(name: str, pipe: Pipeline, X: pd.DataFrame, y: pd.Series) -> None:
    loo = LeaveOneOut()

    y_pred = cross_val_predict(pipe, X, y, cv=loo)
    y_prob = cross_val_predict(pipe, X, y, cv=loo, method="predict_proba")[:, 1]

    SEP = "-" * 54
    print(f"\n{SEP}")
    print(f"  {name}")
    print(SEP)
    print(classification_report(
        y, y_pred,
        target_names=["at-risk (0)", "healthy (1)"],
        zero_division=0,
    ))

    cm = confusion_matrix(y, y_pred)
    tn, fp, fn, tp = cm.ravel()
    print(f"  Confusion matrix:")
    print(f"                Predicted at-risk  Predicted healthy")
    print(f"  Actual at-risk       {tn:>4}               {fp:>4}")
    print(f"  Actual healthy       {fn:>4}               {tp:>4}")

    try:
        auc = roc_auc_score(y, y_prob)
        print(f"\n  ROC-AUC : {auc:.3f}")
    except ValueError:
        print("\n  ROC-AUC : n/a")

    # Probability scores for all SKUs — useful for ranking risk even when
    # the hard label is always at-risk due to imbalance.
    return y_prob


def print_risk_scores(df: pd.DataFrame, y_prob: np.ndarray) -> None:
    scores = df[["sku", "brand_desc", "sku_desc", "sell_through_rate"]].copy()
    scores["healthy_prob"] = y_prob.round(3)
    scores = scores.sort_values("healthy_prob", ascending=False)

    SEP = "-" * 54
    print(f"\n{SEP}")
    print("  Risk scores (all SKUs, ranked by healthy probability)")
    print(SEP)
    print(f"  {'Brand / Style':<40} {'ST%':>5}  {'P(healthy)':>10}")
    print(f"  {'-'*40} {'-'*5}  {'-'*10}")
    for _, row in scores.iterrows():
        label = f"{row['brand_desc'][:25]} / {row['sku_desc'][:12]}"
        print(f"  {label:<40} {row['sell_through_rate']:>5.1%}  {row['healthy_prob']:>10.3f}")


# ── Feature importance ────────────────────────────────────────────────────────

def print_feature_importance(pipe: Pipeline) -> None:
    clf = pipe.named_steps["clf"]
    if not hasattr(clf, "feature_importances_"):
        return

    cat_names = (
        pipe.named_steps["pre"]
            .named_transformers_["cat"]
            .get_feature_names_out(CAT_FEATURES)
    )
    names = list(cat_names) + NUM_FEATURES
    imp = (
        pd.DataFrame({"feature": names, "importance": clf.feature_importances_})
        .sort_values("importance", ascending=False)
        .reset_index(drop=True)
    )

    SEP = "-" * 54
    print(f"\n{SEP}")
    print("  Feature Importance (Random Forest, full-data fit)")
    print(SEP)
    print(imp.to_string(index=False))


# ── Main ─────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db",   default="sellthrough.db")
    parser.add_argument("--save", action="store_true",
                        help="Save trained model to models/model.pkl")
    args = parser.parse_args()

    df = load_features(Path(args.db))
    X, y = df[FEATURES], df["label"]

    n_healthy = int(y.sum())
    n_atrisk  = int((y == 0).sum())

    print(f"Dataset        : {len(df)} SKUs")
    print(f"healthy        : {n_healthy}  ({n_healthy/len(df):.1%})")
    print(f"at-risk        : {n_atrisk}  ({n_atrisk/len(df):.1%})")
    print(f"Imbalance      : 1 : {n_atrisk // max(n_healthy, 1)}")
    print(f"Baseline acc.  : {n_atrisk/len(df):.1%}  (all-at-risk dummy)")
    print(f"\nEvaluating with Leave-One-Out CV ...")

    models = {
        "Logistic Regression  (class_weight=balanced)": LogisticRegression(
            class_weight="balanced", max_iter=1000, random_state=42
        ),
        "Random Forest        (class_weight=balanced)": RandomForestClassifier(
            n_estimators=200, max_depth=3, class_weight="balanced", random_state=42
        ),
    }

    best_prob = None
    for name, clf in models.items():
        pipe  = build_pipeline(clf)
        y_prob = evaluate(name, pipe, X, y)
        if "Random Forest" in name:
            best_prob = y_prob

    # Risk score table uses RF probabilities
    if best_prob is not None:
        print_risk_scores(df, best_prob)

    # Fit RF on full data for feature importance + optional save
    rf_pipe = build_pipeline(models["Random Forest        (class_weight=balanced)"])
    rf_pipe.fit(X, y)
    print_feature_importance(rf_pipe)

    if args.save:
        out = Path("models")
        out.mkdir(exist_ok=True)
        with open(out / "model.pkl", "wb") as f:
            pickle.dump(rf_pipe, f)
        print(f"\nModel saved → models/model.pkl")


if __name__ == "__main__":
    main()
