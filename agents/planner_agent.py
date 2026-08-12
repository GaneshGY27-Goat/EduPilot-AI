def build_plan(mastery, days=7):
    if not mastery:
        return ["Take the diagnostic assessment", "Complete 10 mixed practice questions", "Review mistakes"]

    ordered = sorted(mastery.items(), key=lambda item: item[1])
    plan = []
    for topic, score in ordered:
        if score < 0.5:
            intensity = "High priority"
        elif score < 0.75:
            intensity = "Practice"
        else:
            intensity = "Maintain"
        plan.append(f"{intensity}: {topic} — {round(score * 100)}% mastery")

    plan.append("Finish the week with a mixed mini-test and review every mistake.")
    return plan
