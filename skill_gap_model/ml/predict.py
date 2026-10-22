from pathlib import Path
import json
from bkt_model import run_sequence
from recommend import recommend_activity

ARTIFACTS = Path(__file__).resolve().parent / "artifacts"


def load_parameters():
    with (ARTIFACTS / "bkt_parameters.json").open(encoding="utf-8") as f:
        return json.load(f)


def predict_skill(answers, skill_id, response_times=None, hints=None, problem_type=None):
    """Predict one learner's mastery for one skill from chronological 0/1 answers."""
    all_params = load_parameters()
    key = str(skill_id)
    if key not in all_params:
        raise ValueError(f"No trained BKT parameters found for skill_id={key}")
    answers = [int(a) for a in answers]
    if not answers or any(a not in (0, 1) for a in answers):
        raise ValueError("answers must be a non-empty list containing only 0 and 1")
    params = all_params[key]
    _, mastery = run_sequence(answers, params)
    response_times = response_times or []
    hints = hints or []
    avg_time = sum(response_times) / len(response_times) if response_times else 0
    hint_rate = sum(hints) / len(hints) if hints else 0
    rec = recommend_activity(mastery, sum(answers) / len(answers), hint_rate, avg_time, problem_type)
    return {"skill_id": key, "mastery_probability": round(mastery, 4),
            "mastery_percent": round(mastery * 100, 2), "observed_accuracy": round(sum(answers) / len(answers), 4),
            "recommendation": rec}

if __name__ == "__main__":
    print(predict_skill([0, 1, 1, 0, 1], "SK001", response_times=[40, 30, 60, 50, 35], hints=[1, 0, 0, 1, 0], problem_type="Coding"))
