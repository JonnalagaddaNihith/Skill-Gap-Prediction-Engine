from pathlib import Path
import pickle
from bkt_model import run_sequence

MODEL_PATH = Path(__file__).resolve().parent / "artifacts" / "bkt_model.pkl"
with MODEL_PATH.open("rb") as file:
    model = pickle.load(file)

# Example response sequence for SK001: correct, incorrect, correct, correct
skill_id = "SK001"
answers = [1, 0, 1, 1]
params = model["skill_parameters"][skill_id]
steps, final_mastery = run_sequence(answers, params)
print("Model:", model["model_type"])
print("Skill:", skill_id)
print("Final mastery:", round(final_mastery * 100, 2), "%")
print("Mastery threshold:", model["mastery_threshold"] * 100, "%")
print("Needs practice:", final_mastery < model["mastery_threshold"])
