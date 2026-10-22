import numpy as np
from scipy.optimize import minimize

EPS = 1e-8


def _clip(p):
    return float(np.clip(p, EPS, 1 - EPS))


def predict_correct_probability(mastery, guess, slip):
    """P(correct) before observing an answer."""
    return _clip(mastery * (1.0 - slip) + (1.0 - mastery) * guess)


def update_mastery(mastery, correct, guess, slip, learn):
    """Bayesian posterior update followed by the BKT learning transition."""
    p_correct = predict_correct_probability(mastery, guess, slip)
    if int(correct) == 1:
        posterior = mastery * (1.0 - slip) / p_correct
    else:
        posterior = mastery * slip / (1.0 - p_correct)
    return _clip(posterior + (1.0 - posterior) * learn)


def sequence_log_likelihood(params, sequences):
    p0, learn, guess, slip = params
    total = 0.0
    for seq in sequences:
        mastery = p0
        for answer in seq:
            p = predict_correct_probability(mastery, guess, slip)
            total += np.log(p if int(answer) == 1 else 1.0 - p)
            mastery = update_mastery(mastery, answer, guess, slip, learn)
    return -total


def fit_bkt(sequences, max_sequences=150):
    """Fit the four BKT parameters by maximum likelihood for one skill."""
    clean = [np.asarray(s, dtype=int).tolist() for s in sequences if len(s)]
    # Cap fitting cost while preserving many learner sequences per skill.
    if len(clean) > max_sequences:
        rng = np.random.default_rng(42)
        selected = rng.choice(len(clean), size=max_sequences, replace=False)
        clean = [clean[i] for i in sorted(selected)]
    if not clean:
        return {"p_initial": 0.25, "p_learn": 0.15, "p_guess": 0.20, "p_slip": 0.10}
    bounds = [(0.01, 0.99), (0.001, 0.80), (0.01, 0.45), (0.01, 0.45)]
    starts = [[0.25, 0.15, 0.20, 0.10]]
    best = None
    for start in starts:
        result = minimize(sequence_log_likelihood, start, args=(clean,), method="L-BFGS-B", bounds=bounds, options={"maxiter": 80})
        if result.success and (best is None or result.fun < best.fun):
            best = result
    values = best.x if best is not None else np.array(starts[0])
    return {"p_initial": float(values[0]), "p_learn": float(values[1]),
            "p_guess": float(values[2]), "p_slip": float(values[3])}


def run_sequence(answers, params):
    mastery = params["p_initial"]
    rows = []
    for answer in answers:
        p_correct = predict_correct_probability(mastery, params["p_guess"], params["p_slip"])
        rows.append({"predicted_correct_probability": p_correct, "mastery_before": mastery,
                    "correct": int(answer)})
        mastery = update_mastery(mastery, answer, params["p_guess"], params["p_slip"], params["p_learn"])
    return rows, mastery
