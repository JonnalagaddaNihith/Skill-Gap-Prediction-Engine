"""Rule-based learning activities selected from BKT mastery and behavior signals."""

def recommend_activity(mastery, accuracy, hint_rate, avg_response_time, problem_type=None):
    if mastery < 0.40:
        priority = "High"
        activity = "Review the fundamentals, follow a guided tutorial, then complete 5 easy exercises."
    elif mastery < 0.70:
        priority = "Medium"
        activity = "Study worked examples and complete 8 progressively harder practice questions."
    else:
        priority = "Low"
        activity = "Attempt a mixed challenge set and revisit this skill in a spaced-revision session."
    reasons = []
    if accuracy < 0.60:
        reasons.append("recent correctness is low")
    if hint_rate > 0.35:
        reasons.append("hints are used frequently")
    if avg_response_time > 90:
        reasons.append("responses take longer than 90 seconds on average")
    if problem_type:
        activity += f" Include {str(problem_type).lower()} practice."
    return {"priority": priority, "activity": activity,
            "reason": "; ".join(reasons) if reasons else "Based on the estimated mastery level."}
