def diagnose(questions, answers):
    stats = {}
    for q, selected in zip(questions, answers):
        topic = q["topic"]
        stats.setdefault(topic, {"correct": 0, "total": 0})
        stats[topic]["total"] += 1
        stats[topic]["correct"] += int(selected == q["answer"])

    mastery = {
        topic: round(values["correct"] / values["total"], 2)
        for topic, values in stats.items()
    }
    weak = sorted(mastery, key=mastery.get)[:3]
    return {"mastery": mastery, "weak_topics": weak, "stats": stats}
