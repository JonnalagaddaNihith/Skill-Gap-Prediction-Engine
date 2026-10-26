import sys
from pathlib import Path
import numpy as np
import pandas as pd
import json

_PKG_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = _PKG_DIR.parent.parent
if str(_PKG_DIR) not in sys.path:
    sys.path.insert(0, str(_PKG_DIR))

# Load catalog configuration
with (_PKG_DIR / "catalog.json").open(encoding="utf-8") as catalog_file:
    _catalog = json.load(catalog_file)

DIFFICULTY_LEVELS = _catalog["difficulty_levels"]
PROBLEM_TYPES = _catalog["problem_types"]


def load_and_prepare(path):
    df = pd.read_csv(path)
    diff_map = {level: idx for idx, level in enumerate(DIFFICULTY_LEVELS)}
    df["diff_num"] = df["difficulty"].map(diff_map)
    return df


def build_student_skill_features(df):
    """Aggregate interaction logs into per-(student, skill) feature vectors."""
    records = []
    for (stu, sk), g in df.groupby(["student_id", "skill_id"]):
        n = len(g)
        acc = g["correct"].mean()
        avg_time = g["response_time"].mean()
        median_time = g["response_time"].median()
        hint_rate = g["hint_used"].mean()
        avg_attempt = g["attempt_number"].mean()
        max_attempt = g["attempt_number"].max()
        weights = 1.0 + 0.5 * g["diff_num"]
        w_acc = (g["correct"] * weights).sum() / weights.sum()
        g_sorted = g.sort_values("attempt_number")
        recent = g_sorted.tail(max(1, int(0.3 * n)))
        recent_acc = recent["correct"].mean()
        consistency = 1.0 - g["correct"].std() if n > 1 else 0.5
        n_types = g["problem_type"].nunique()
        n_courses = g["course_id"].nunique()

        # Problem type distribution features
        pt_counts = g["problem_type"].value_counts()
        pt_dist = {pt: pt_counts.get(pt, 0) / n for pt in PROBLEM_TYPES}

        records.append({
            "student_id": stu,
            "skill_id": sk,
            "n_attempts": n,
            "accuracy": acc,
            "weighted_acc": w_acc,
            "recent_acc": recent_acc,
            "avg_time": avg_time,
            "median_time": median_time,
            "hint_rate": hint_rate,
            "avg_attempt_num": avg_attempt,
            "max_attempt": max_attempt,
            "consistency": consistency,
            "n_problem_types": n_types,
            "n_courses": n_courses,
            **{f"pt_{pt}": pt_dist[pt] for pt in PROBLEM_TYPES},
        })
    return pd.DataFrame(records)


def create_mastery_labels(feat_df, seed=42):
    """Synthesize continuous mastery target from observed signals."""
    rng = np.random.default_rng(seed)
    mastery = (
        0.40 * feat_df["accuracy"]
        + 0.20 * feat_df["weighted_acc"]
        + 0.15 * feat_df["recent_acc"]
        + 0.10 * (1 - feat_df["hint_rate"].clip(0, 1))
        + 0.08 * feat_df["consistency"]
        + 0.07 * np.minimum(feat_df["n_attempts"] / 25.0, 1.0)
    )
    mastery = mastery + rng.normal(0, 0.04, size=len(mastery))
    feat_df = feat_df.copy()
    feat_df["mastery"] = np.clip(mastery, 0.05, 0.98)
    return feat_df

def main():
    """Run feature engineering and save results."""
    data_path = PROJECT_ROOT / "DataSet_Output" / "Generated_Learner_Assessment.csv"
    out_dir = PROJECT_ROOT / "artifacts"
    out_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 65)
    print("FEATURE ENGINEERING")
    print("=" * 65)

    # 1. Load
    print("\n[1] Loading data …")
    raw = load_and_prepare(data_path)
    print(f"    Interactions: {len(raw):,}  |  Students: {raw.student_id.nunique()}  "
          f"|  Skills: {raw.skill_id.nunique()}")

    # 2. Features
    print("\n[2] Building student-skill features …")
    feat = build_student_skill_features(raw)
    feat = create_mastery_labels(feat)
    print(f"    Feature matrix: {feat.shape}")
    print(f"    Mastery mean={feat.mastery.mean():.3f}  std={feat.mastery.std():.3f}")

    # 3. Save results
    feat.to_csv(out_dir / "student_skill_features.csv", index=False)

    print(f"\n  Saved → {out_dir}/student_skill_features.csv")
    print("\n✅ Feature engineering complete.")

    return feat, raw


if __name__ == "__main__":
    main()
