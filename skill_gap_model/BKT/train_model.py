from pathlib import Path
import json
import pickle
import sys
import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, log_loss, brier_score_loss
from bkt_model import fit_bkt, run_sequence, predict_correct_probability, update_mastery
from recommend import recommend_activity

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA = "Generated_Learner_Assessment.csv"
ARTIFACTS = ROOT / "ml" / "artifacts"
REQUIRED = ["student_id", "question_id", "skill_id", "correct", "attempt_number",
            "response_time", "hint_used", "difficulty", "course_id", "problem_type"]


def load_data(path):
    df = pd.read_csv(path)
    df.columns = [str(c).strip().lower() for c in df.columns]
    missing = sorted(set(REQUIRED) - set(df.columns))
    if missing:
        raise ValueError(f"Dataset is missing required columns: {missing}")
    for col in ["correct", "attempt_number", "response_time", "hint_used"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.dropna(subset=["student_id", "skill_id", "correct"])
    df = df[df["correct"].isin([0, 1])].copy()
    df["student_id"] = df["student_id"].astype(str)
    df["skill_id"] = df["skill_id"].astype(str)
    df["correct"] = df["correct"].astype(int)
    df["attempt_number"] = df["attempt_number"].fillna(1)
    df["response_time"] = df["response_time"].clip(lower=0)
    df["hint_used"] = df["hint_used"].fillna(0).clip(0, 1)
    if df.empty:
        raise ValueError("No valid assessment rows remain after cleaning.")
    # The source has no timestamp, so use attempt_number then original file order as a proxy.
    df["_source_order"] = np.arange(len(df))
    return df.sort_values(["student_id", "skill_id", "attempt_number", "_source_order"])


def fit_and_score(df):
    params_by_skill = {}
    mastery_rows = []
    diagnostic_y, diagnostic_p = [], []
    grouped = df.groupby("skill_id", sort=True)
    for skill_id, skill_df in grouped:
        sequences = [g["correct"].tolist() for _, g in skill_df.groupby("student_id", sort=False)]
        params = fit_bkt(sequences)
        params_by_skill[str(skill_id)] = params
        for student_id, group in skill_df.groupby("student_id", sort=False):
            answers = group["correct"].tolist()
            _, final_mastery = run_sequence(answers, params)
            n = len(group)
            accuracy = float(group["correct"].mean())
            hint_rate = float(group["hint_used"].mean())
            avg_time = float(group["response_time"].mean()) if group["response_time"].notna().any() else 0.0
            common_type = group["problem_type"].mode(dropna=True)
            problem_type = str(common_type.iloc[0]) if len(common_type) else None
            rec = recommend_activity(final_mastery, accuracy, hint_rate, avg_time, problem_type)
            mastery_rows.append({
                "student_id": str(student_id), "skill_id": str(skill_id),
                "mastery_probability": round(float(final_mastery), 6),
                "mastery_percent": round(float(final_mastery) * 100, 2),
                "observed_accuracy": round(accuracy, 4), "responses": int(n),
                "hint_rate": round(hint_rate, 4), "avg_response_time": round(avg_time, 2),
                "priority": rec["priority"], "recommendation": rec["activity"], "reason": rec["reason"]
            })
            # One-step sequential diagnostic; parameter fit uses all sequences, so this is not a holdout score.
            m = params["p_initial"]
            for answer in answers:
                p = predict_correct_probability(m, params["p_guess"], params["p_slip"])
                diagnostic_y.append(answer)
                diagnostic_p.append(p)
                m = update_mastery(m, answer, params["p_guess"], params["p_slip"], params["p_learn"])
    predictions = pd.DataFrame(mastery_rows).sort_values(["student_id", "mastery_probability"])
    y = np.asarray(diagnostic_y, dtype=int)
    p = np.clip(np.asarray(diagnostic_p, dtype=float), 1e-7, 1 - 1e-7)
    metrics = {
        "rows_used": int(len(df)), "students": int(df["student_id"].nunique()),
        "skills": int(df["skill_id"].nunique()), "overall_observed_accuracy": round(float(y.mean()), 4),
        "sequential_diagnostic_accuracy": round(float(accuracy_score(y, p >= 0.5)), 4),
        "sequential_diagnostic_log_loss": round(float(log_loss(y, p, labels=[0, 1])), 4),
        "sequential_diagnostic_brier_score": round(float(brier_score_loss(y, p)), 4),
        "evaluation_note": "In-sample sequential diagnostic only: parameters were fitted on these same learner sequences. Use a student-held-out or time-ordered evaluation before claiming generalization."
    }
    return params_by_skill, predictions, metrics


def main():
    data_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_DATA
    df = load_data(data_path)
    params, predictions, metrics = fit_and_score(df)
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    (ARTIFACTS / "bkt_parameters.json").write_text(json.dumps(params, indent=2))
    model_bundle = {
        "model_type": "Bayesian Knowledge Tracing (BKT)",
        "model_version": "1.0",
        "skill_parameters": params,
        "mastery_threshold": 0.70,
        "parameter_order": ["p_initial", "p_learn", "p_guess", "p_slip"],
        "input_description": "Sequential binary correctness responses grouped by skill_id and ordered chronologically or by attempt_number.",
        "notes": "This pickle stores fitted BKT parameters, not a scikit-learn estimator. Use bkt_model.py functions for inference."
    }
    with (ARTIFACTS / "bkt_model.pkl").open("wb") as model_file:
        pickle.dump(model_bundle, model_file, protocol=pickle.HIGHEST_PROTOCOL)
    predictions.to_csv(ARTIFACTS / "student_skill_mastery.csv", index=False)
    (ARTIFACTS / "training_metrics.json").write_text(json.dumps(metrics, indent=2))
    print("DATASET SUMMARY")
    print(f"Rows used: {metrics['rows_used']} | Students: {metrics['students']} | Skills: {metrics['skills']}")
    print("\nBKT PARAMETERS BY SKILL")
    print(json.dumps(params, indent=2))
    print("\nEVALUATION DIAGNOSTICS")
    print(json.dumps(metrics, indent=2))
    print("\nSAMPLE MASTERY OUTPUT")
    print(predictions.head(12).to_string(index=False))
    print(f"\nArtifacts saved to: {ARTIFACTS}")

if __name__ == "__main__":
    main()
