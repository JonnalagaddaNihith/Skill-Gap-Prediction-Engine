import numpy as np
import pandas as pd
import torch

from .architecture import FEATURE_COLS, SKILL_NAMES


def _weak_profile(student_raw: pd.DataFrame, skill_id: str):
    g = student_raw[student_raw.skill_id == skill_id]
    if g.empty:
        return [], [], {}

    diff_acc = g.groupby("difficulty")["correct"].agg(["mean", "count"])
    diff_acc = diff_acc[diff_acc["count"] >= 2]
    weak_diffs = diff_acc.sort_values("mean").index.tolist() if not diff_acc.empty else []

    pt_acc = g.groupby("problem_type")["correct"].agg(["mean", "count"])
    pt_acc = pt_acc[pt_acc["count"] >= 2]
    weak_pts = pt_acc.sort_values("mean").index.tolist() if not pt_acc.empty else []

    profiles = {
        "diff_acc": diff_acc["mean"].to_dict() if not diff_acc.empty else {},
        "pt_acc": pt_acc["mean"].to_dict() if not pt_acc.empty else {},
    }
    return weak_diffs, weak_pts, profiles


def predict_mastery(student_id, feat_df, model, means, stds,
                    feature_cols=None, device="cpu"):
    cols = feature_cols or FEATURE_COLS
    rows = feat_df[feat_df.student_id == student_id].copy()
    if rows.empty:
        return rows

    means = np.asarray(means, dtype=np.float64)
    stds = np.asarray(stds, dtype=np.float64)
    X = (rows[cols].values - means) / stds
    X_t = torch.tensor(X, dtype=torch.float32).to(device)

    model.eval()
    with torch.no_grad():
        preds = model(X_t).cpu().numpy()

    rows = rows.reset_index(drop=True)
    rows["predicted_mastery"] = preds
    return rows


def identify_gaps(student_id, feat_df, model, means, stds, raw_df=None,
                threshold=0.55, feature_cols=None, skill_names=None,
                device="cpu"):
    """
    Return list of skill-gap dicts (mastery < threshold), sorted by severity.
    When raw_df is given, also attach weak difficulty / problem_type profiles.
    """
    skill_names = skill_names or SKILL_NAMES
    pred_df = predict_mastery(
        student_id, feat_df, model, means, stds,
        feature_cols=feature_cols, device=device,
    )
    if pred_df.empty:
        return []

    student_raw = raw_df[raw_df.student_id == student_id] if raw_df is not None else None

    gaps = []
    for _, r in pred_df.iterrows():
        if r.predicted_mastery >= threshold:
            continue

        weak_diffs, weak_pts, profiles = [], [], {}
        if student_raw is not None:
            weak_diffs, weak_pts, profiles = _weak_profile(student_raw, r.skill_id)

        gaps.append({
            "skill_id": r.skill_id,
            "skill_name": skill_names.get(r.skill_id, r.skill_id),
            "predicted_mastery": float(r.predicted_mastery),
            "gap_severity": float(threshold - r.predicted_mastery),
            "observed_accuracy": float(r.accuracy) if "accuracy" in r else None,
            "n_attempts": int(r.n_attempts) if "n_attempts" in r else None,
            "hint_rate": float(r.hint_rate) if "hint_rate" in r else None,
            "weak_difficulties": weak_diffs,
            "weak_problem_types": weak_pts,
            "diff_acc": profiles.get("diff_acc", {}),
            "pt_acc": profiles.get("pt_acc", {}),
        })

    gaps.sort(key=lambda x: -x["gap_severity"])
    return gaps
