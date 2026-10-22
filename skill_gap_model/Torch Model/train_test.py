import sys
from pathlib import Path
import json
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader

from architecture import (
    FEATURE_COLS,
    SKILL_NAMES,
    LEARNING_ACTIVITIES,
    ProficiencyDataset,
    SkillProficiencyNet,
)
from predict import identify_gaps
from recommend import recommend_activities

_PKG_DIR = Path(__file__).resolve().parent
if str(_PKG_DIR) not in sys.path:
    sys.path.insert(0, str(_PKG_DIR))


# Feature engineering

def load_and_prepare(path):
    df = pd.read_csv(path)
    diff_map = {"Easy": 0, "Medium": 1, "Hard": 2}
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

# Training loop

def train_model(model, train_loader, val_loader, epochs=100, lr=1e-3, device="cpu"):
    criterion = nn.MSELoss()
    optimizer = optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)
    scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs)

    best_val = float("inf")
    best_state = None
    history = {"train_loss": [], "val_loss": [], "val_mae": []}

    for epoch in range(1, epochs + 1):
        model.train()
        tr_loss = 0.0
        for X, y in train_loader:
            X, y = X.to(device), y.to(device)
            optimizer.zero_grad()
            pred = model(X)
            loss = criterion(pred, y)
            loss.backward()
            optimizer.step()
            tr_loss += loss.item() * len(y)
        tr_loss /= len(train_loader.dataset)

        model.eval()
        va_loss, va_mae = 0.0, 0.0
        with torch.no_grad():
            for X, y in val_loader:
                X, y = X.to(device), y.to(device)
                pred = model(X)
                va_loss += criterion(pred, y).item() * len(y)
                va_mae += torch.abs(pred - y).sum().item()
        va_loss /= len(val_loader.dataset)
        va_mae /= len(val_loader.dataset)
        scheduler.step()

        history["train_loss"].append(tr_loss)
        history["val_loss"].append(va_loss)
        history["val_mae"].append(va_mae)

        if va_loss < best_val:
            best_val = va_loss
            best_state = {k: v.cpu().clone() for k, v in model.state_dict().items()}

        if epoch % 10 == 0 or epoch == 1:
            print(f"  Epoch {epoch:3d} | train={tr_loss:.4f} | val={va_loss:.4f} | MAE={va_mae:.4f}")

    model.load_state_dict(best_state)
    return model, history


def evaluate(model, val_loader, device="cpu"):
    model.eval()
    preds, trues = [], []
    with torch.no_grad():
        for X, y in val_loader:
            p = model(X.to(device)).cpu()
            preds.append(p)
            trues.append(y)
    preds = torch.cat(preds).numpy()
    trues = torch.cat(trues).numpy()

    mae = float(np.mean(np.abs(preds - trues)))
    rmse = float(np.sqrt(np.mean((preds - trues) ** 2)))
    corr = float(np.corrcoef(preds, trues)[0, 1])

    pred_bin = (preds >= 0.55).astype(int)
    true_bin = (trues >= 0.55).astype(int)
    acc = float((pred_bin == true_bin).mean())
    tp = int(((pred_bin == 1) & (true_bin == 1)).sum())
    fp = int(((pred_bin == 1) & (true_bin == 0)).sum())
    fn = int(((pred_bin == 0) & (true_bin == 1)).sum())
    prec = tp / (tp + fp + 1e-9)
    rec = tp / (tp + fn + 1e-9)
    f1 = 2 * prec * rec / (prec + rec + 1e-9)

    return {
        "mae": mae,
        "rmse": rmse,
        "corr": corr,
        "accuracy": acc,
        "precision": float(prec),
        "recall": float(rec),
        "f1": float(f1),
    }


# Main

def resolve_data_path():
    """Find the assessment CSV relative to common locations."""
    candidates = [
        _PKG_DIR / "Generated_Learner_Assessment.csv",
        _PKG_DIR.parent / "Generated_Learner_Assessment.csv",
        Path("Generated_Learner_Assessment.csv"),
        Path("../Generated_Learner_Assessment.csv"),
    ]
    for p in candidates:
        if p.exists():
            return p
    raise FileNotFoundError(
        "Could not find Generated_Learner_Assessment.csv. "
        "Place it next to train_test.py or in /home/workdir/attachments/"
    )


def main():
    data_path = resolve_data_path()
    out_dir = _PKG_DIR / "artifacts"
    out_dir.mkdir(parents=True, exist_ok=True)
    device = "cuda" if torch.cuda.is_available() else "cpu"

    print(f"Device: {device}")
    print("=" * 65)
    print("LEARNER PROFICIENCY – TRAIN / TEST")
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

    # 3. Normalize & split by student (no leakage)
    means = feat[FEATURE_COLS].mean().values
    stds = feat[FEATURE_COLS].std().replace(0, 1).values
    feat_norm = feat.copy()
    feat_norm[FEATURE_COLS] = (feat[FEATURE_COLS] - means) / stds

    rng = np.random.default_rng(42)
    students = np.array(feat.student_id.unique())
    rng.shuffle(students)
    split = int(0.8 * len(students))
    train_stu = set(students[:split])
    val_stu = set(students[split:])

    train_df = feat_norm[feat_norm.student_id.isin(train_stu)]
    val_df = feat_norm[feat_norm.student_id.isin(val_stu)]
    print(f"    Train students: {len(train_stu)} ({len(train_df)} rows)  |  "
        f"Val: {len(val_stu)} ({len(val_df)} rows)")

    train_loader = DataLoader(ProficiencyDataset(train_df), batch_size=128, shuffle=True)
    val_loader = DataLoader(ProficiencyDataset(val_df), batch_size=256, shuffle=False)

    # 4. Train
    print("\n[3] Training SkillProficiencyNet …")
    model = SkillProficiencyNet(input_dim=len(FEATURE_COLS)).to(device)
    model, history = train_model(model, train_loader, val_loader, epochs=50, lr=1e-3, device=device)

    metrics = evaluate(model, val_loader, device=device)

    print("\n" + "=" * 65)
    print("VALIDATION METRICS")
    print("=" * 65)
    print(f"  MAE             : {metrics['mae']:.4f}")
    print(f"  RMSE            : {metrics['rmse']:.4f}")
    print(f"  Correlation     : {metrics['corr']:.4f}")
    print(f"  Accuracy        : {metrics['accuracy']:.4f}")
    print(f"  Precision       : {metrics['precision']:.4f}")
    print(f"  Recall          : {metrics['recall']:.4f}")
    print(f"  F1              : {metrics['f1']:.4f}")

    # 5. Persist
    torch.save({
        "model_state": model.state_dict(),
        "feature_cols": FEATURE_COLS,
        "means": means.tolist(),
        "stds": stds.tolist(),
        "skill_names": SKILL_NAMES,
        "metrics": metrics,
        "history": history,
    }, out_dir / "proficiency_model.pt")

    feat.to_csv(out_dir / "student_skill_features.csv", index=False)
    with open(out_dir / "activities.json", "w") as f:
        json.dump(LEARNING_ACTIVITIES, f, indent=2)

    print(f"\n  Saved → {out_dir}/proficiency_model.pt")
    print(f"  Saved → {out_dir}/student_skill_features.csv")
    print(f"  Saved → {out_dir}/activities.json")

    # 6. Demo
    print("\n" + "=" * 65)
    print("DEMO – Skill Gaps & Recommendations")
    print("      (skill gap + difficulty match + problem_type match)")
    print("=" * 65)

    for sid in list(val_stu)[:4]:
        gaps = identify_gaps(
            sid, feat, model, means, stds,
            raw_df=raw, threshold=0.55, device=device,
        )
        print(f"\nStudent: {sid}")
        if not gaps:
            print("  ✓ No significant skill gaps")
            continue
        print("  Gaps (mastery < 0.55):")
        for g in gaps:
            weak_d = ", ".join(g["weak_difficulties"][:2]) or "n/a"
            weak_p = ", ".join(g["weak_problem_types"][:2]) or "n/a"
            print(f"    • {g['skill_name']:<38} mastery={g['predicted_mastery']:.2f}  "
                f"(acc={g['observed_accuracy']:.2f}, n={g['n_attempts']})")
            print(f"      weak difficulty: [{weak_d}]   weak problem_type: [{weak_p}]")
        recs = recommend_activities(gaps, top_k=4)
        print("  Recommended activities:")
        for r in recs:
            print(f"    → [{r['activity_id']}] {r['title']}")
            print(f"       {r['type']}, {r['duration_min']} min, {r['difficulty']}  |  "
                f"covers: {', '.join(r['matched_skills'])}")
            print(f"       score={r['relevance_score']:.3f}  "
                f"(skill={r['base_skill_score']:.2f} + "
                f"diff={r['difficulty_bonus']:.2f} + "
                f"ptype={r['problem_type_bonus']:.2f})")

    print("\n✅ Done.")
    return model, feat, metrics


if __name__ == "__main__":
    main()
