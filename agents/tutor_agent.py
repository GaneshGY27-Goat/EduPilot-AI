import os


def explain(question, selected, correct):
    base = question.get("explanation", "Review the concept and try a similar problem.")
    if selected == correct:
        return f"Great work! You chose the correct answer. {base}"
    return f"Let's slow down and learn from this mistake. You selected option {selected + 1}, but the correct answer is option {correct + 1}. {base}"


def ai_explain(question, selected, correct, api_key=None):
    if not api_key:
        return explain(question, selected, correct)

    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        response = client.responses.create(
            model="gpt-4o-mini",
            input=f"You are a patient SAT tutor. Explain this question in simple steps. Question: {question['question']} Options: {question['options']}. Student selected option {selected + 1}. Correct option {correct + 1}. Give a short explanation and one tip."
        )
        return response.output_text
    except Exception:
        return explain(question, selected, correct)
