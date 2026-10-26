from pathlib import Path
import json
import torch
import pandas as pd

from .architecture import SkillProficiencyNet, FEATURE_COLS, SKILL_NAMES, LEARNING_ACTIVITIES


def get_default_artifact_dir():
    return Path(__file__).resolve().parent.parent.parent / "artifacts"


def load_checkpoint(artifact_dir=None, device=None):
    """
    Load model weights + scaling stats + metrics from disk.

    Returns
    -------
    model : SkillProficiencyNet (eval mode)
    meta  : dict with keys feature_cols, means, stds, skill_names, metrics, ...
    """
    artifact_dir = Path(artifact_dir) if artifact_dir else get_default_artifact_dir()
    device = device or ("cuda" if torch.cuda.is_available() else "cpu")

    ckpt_path = artifact_dir / "skill_proficiency_model.pt"
    if not ckpt_path.exists():
        # fallback to older naming
        for name in ("Synthetic_proficiency_model.pt", "real_proficiency_model.pt"):
            alt = artifact_dir / name
            if alt.exists():
                ckpt_path = alt
                break
        else:
            raise FileNotFoundError(f"No model checkpoint found in {artifact_dir}")

    ckpt = torch.load(ckpt_path, map_location=device, weights_only=False)

    feature_cols = ckpt.get("feature_cols", FEATURE_COLS)
    model = SkillProficiencyNet(input_dim=len(feature_cols)).to(device)
    model.load_state_dict(ckpt["model_state"])
    model.eval()

    meta = {
        "feature_cols": feature_cols,
        "means": ckpt["means"],
        "stds": ckpt["stds"],
        "skill_names": ckpt.get("skill_names", SKILL_NAMES),
        "metrics": ckpt.get("metrics", {}),
        "history": ckpt.get("history", {}),
        "artifact_dir": str(artifact_dir),
        "device": device,
    }
    return model, meta


def load_features(artifact_dir=None):
    """Load the student-skill feature CSV saved during training."""
    artifact_dir = Path(artifact_dir) if artifact_dir else get_default_artifact_dir()
    for name in ("student_skill_features.csv", "Synthetic_student_skill_features.csv",
                "real_student_skill_features.csv"):
        path = artifact_dir / name
        if path.exists():
            return pd.read_csv(path)
    raise FileNotFoundError(f"No feature CSV found in {artifact_dir}")


def load_activities(artifact_dir=None):
    """Load activity catalog (JSON) or fall back to built-in list."""
    artifact_dir = Path(artifact_dir) if artifact_dir else get_default_artifact_dir()
    for name in ("activities.json", "Synthetic_activities.json", "real_activities.json"):
        path = artifact_dir / name
        if path.exists():
            with open(path) as f:
                return json.load(f)
    return LEARNING_ACTIVITIES
