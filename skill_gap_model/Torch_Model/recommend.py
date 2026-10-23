from architecture import (
    LEARNING_ACTIVITIES,
    SKILL_NAMES,
    DIFFICULTY_LEVELS,
    PROBLEM_TYPES,
    PROBLEM_WEIGHTS,
)

# Map activity difficulty → assessment difficulty labels
ACT_DIFF_TO_ASSESS = {
    "beginner": DIFFICULTY_LEVELS[0] if len(DIFFICULTY_LEVELS) > 0 else "Easy",
    "intermediate": DIFFICULTY_LEVELS[1] if len(DIFFICULTY_LEVELS) > 1 else "Medium",
    "advanced": DIFFICULTY_LEVELS[2] if len(DIFFICULTY_LEVELS) > 2 else "Hard",
}

# Create problem type to weight mapping
PROBLEM_TYPE_WEIGHT = {pt: weight for pt, weight in zip(PROBLEM_TYPES, PROBLEM_WEIGHTS)}

# Affinity between activity type and assessment problem_type
# Initialize with default values for all problem types in catalog
TYPE_AFFINITY = {
    "coding": {},
    "interactive": {},
    "video": {},
    "reading": {},
    "project": {},
}

# Set affinity values based on problem type
for pt in PROBLEM_TYPES:
    if pt == "Coding":
        TYPE_AFFINITY["coding"][pt] = 1.0
        TYPE_AFFINITY["interactive"][pt] = 0.5
        TYPE_AFFINITY["video"][pt] = 0.2
        TYPE_AFFINITY["reading"][pt] = 0.2
        TYPE_AFFINITY["project"][pt] = 1.0
    elif pt == "Debugging":
        TYPE_AFFINITY["coding"][pt] = 0.6
        TYPE_AFFINITY["interactive"][pt] = 0.5
        TYPE_AFFINITY["video"][pt] = 0.3
        TYPE_AFFINITY["reading"][pt] = 0.3
        TYPE_AFFINITY["project"][pt] = 0.7
    elif pt == "Conceptual":
        TYPE_AFFINITY["coding"][pt] = 0.2
        TYPE_AFFINITY["interactive"][pt] = 0.6
        TYPE_AFFINITY["video"][pt] = 1.0
        TYPE_AFFINITY["reading"][pt] = 0.9
        TYPE_AFFINITY["project"][pt] = 0.4
    else:  # Multiple Choice or other
        TYPE_AFFINITY["coding"][pt] = 0.3
        TYPE_AFFINITY["interactive"][pt] = 0.7
        TYPE_AFFINITY["video"][pt] = 0.5
        TYPE_AFFINITY["reading"][pt] = 0.6
        TYPE_AFFINITY["project"][pt] = 0.3

# Affinity between activity type and assessment problem_type
TYPE_AFFINITY = {
    "coding":      {"Coding": 1.0, "Debugging": 0.6, "Conceptual": 0.2, "Multiple Choice": 0.3},
    "interactive": {"Coding": 0.5, "Debugging": 0.5, "Conceptual": 0.6, "Multiple Choice": 0.7},
    "video":       {"Coding": 0.2, "Debugging": 0.3, "Conceptual": 1.0, "Multiple Choice": 0.5},
    "reading":     {"Coding": 0.2, "Debugging": 0.3, "Conceptual": 0.9, "Multiple Choice": 0.6},
    "project":     {"Coding": 1.0, "Debugging": 0.7, "Conceptual": 0.4, "Multiple Choice": 0.3},
}


def recommend_activities(gaps, activities=None, skill_names=None, top_k=5):
    """
    Rank activities by:
    base              = sum of gap severities for matched skills
    difficulty_bonus  = activity level aligns with student's weak difficulty
    problem_type_bonus = activity type aligns with student's weak problem_types
    """
    if not gaps:
        return []

    activities = activities or LEARNING_ACTIVITIES
    skill_names = skill_names or SKILL_NAMES
    gap_map = {g["skill_id"]: g for g in gaps}
    scored = []

    for act in activities:
        matched_skills = [sk for sk in act["skills"] if sk in gap_map]
        if not matched_skills:
            continue

        base = sum(gap_map[sk]["gap_severity"] for sk in matched_skills)

        # Difficulty match
        act_diff_label = ACT_DIFF_TO_ASSESS.get(act["difficulty"], "Medium")
        diff_bonus = 0.0
        for sk in matched_skills:
            weak = gap_map[sk].get("weak_difficulties") or []
            if not weak:
                continue
            if act_diff_label == weak[0]:
                diff_bonus += 0.35 * gap_map[sk]["gap_severity"]
            elif act_diff_label in weak[:2]:
                diff_bonus += 0.15 * gap_map[sk]["gap_severity"]

        # Problem-type match
        affinity = TYPE_AFFINITY.get(act["type"], {})
        type_bonus = 0.0
        for sk in matched_skills:
            weak_pts = gap_map[sk].get("weak_problem_types") or []
            if not weak_pts:
                continue
            for i, pt in enumerate(weak_pts[:3]):
                weight = 1.0 / (i + 1)
                pt_weight = PROBLEM_TYPE_WEIGHT.get(pt, 1.0)
                type_bonus += 0.25 * weight * affinity.get(pt, 0.0) * pt_weight * gap_map[sk]["gap_severity"]

        total = base + diff_bonus + type_bonus
        matched_names = [skill_names.get(sk, sk) for sk in matched_skills]

        scored.append({
            "activity_id": act["id"],
            "title": act["title"],
            "type": act["type"],
            "duration_min": act["duration_min"],
            "difficulty": act["difficulty"],
            "matched_skills": matched_names,
            "relevance_score": round(total, 4),
            "base_skill_score": round(base, 4),
            "difficulty_bonus": round(diff_bonus, 4),
            "problem_type_bonus": round(type_bonus, 4),
            "matched_act_difficulty": act_diff_label,
        })

    scored.sort(key=lambda x: -x["relevance_score"])
    return scored[:top_k]
