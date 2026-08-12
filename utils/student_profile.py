from collections import defaultdict


def default_profile():
    return {
        "name": "Student",
        "target_score": 1400,
        "answers": [],
        "mastery": defaultdict(lambda: 0.50),
        "attempts": defaultdict(int),
        "correct": defaultdict(int),
        "history": [],
    }


def update_profile(profile, question, is_correct):
    topic = question["topic"]
    profile["attempts"][topic] += 1
    if is_correct:
        profile["correct"][topic] += 1

    attempts = profile["attempts"][topic]
    correct = profile["correct"][topic]
    profile["mastery"][topic] = round(correct / attempts, 2)
    profile["answers"].append({"question_id": question["id"], "topic": topic, "correct": is_correct})
    profile["history"].append({"topic": topic, "correct": is_correct})


def weak_topics(profile, limit=3):
    topics = list(profile["mastery"].items())
    topics.sort(key=lambda x: x[1])
    return [topic for topic, score in topics if profile["attempts"][topic] > 0][:limit]
