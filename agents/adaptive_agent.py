DIFFICULTY_ORDER = ["easy", "medium", "hard"]


def next_difficulty(last_difficulty, is_correct):
    index = DIFFICULTY_ORDER.index(last_difficulty)
    if is_correct:
        return DIFFICULTY_ORDER[min(index + 1, 2)]
    return DIFFICULTY_ORDER[max(index - 1, 0)]


def choose_question(questions, mastery, preferred_topic=None, difficulty="medium", exclude_ids=None):
    exclude_ids = set(exclude_ids or [])
    candidates = [q for q in questions if q["id"] not in exclude_ids]

    if preferred_topic:
        topic_candidates = [q for q in candidates if q["topic"] == preferred_topic]
        if topic_candidates:
            candidates = topic_candidates

    exact = [q for q in candidates if q["difficulty"] == difficulty]
    if exact:
        candidates = exact

    candidates.sort(key=lambda q: mastery.get(q["topic"], 0.5))
    return candidates[0] if candidates else None
