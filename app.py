import json
import os
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

from agents.adaptive_agent import choose_question, next_difficulty
from agents.diagnostic_agent import diagnose
from agents.planner_agent import build_plan
from agents.tutor_agent import ai_explain
from models.mastery_model import MasteryModel
from utils.student_profile import default_profile, update_profile

load_dotenv()

st.set_page_config(page_title="EduPilot AI", page_icon="🎓", layout="wide")

DATA_PATH = Path(__file__).parent / "data" / "questions.json"
QUESTIONS = json.loads(DATA_PATH.read_text(encoding="utf-8"))

if "profile" not in st.session_state:
    st.session_state.profile = default_profile()
if "diagnostic_done" not in st.session_state:
    st.session_state.diagnostic_done = False
if "diagnostic_index" not in st.session_state:
    st.session_state.diagnostic_index = 0
if "diagnostic_answers" not in st.session_state:
    st.session_state.diagnostic_answers = []
if "current_question" not in st.session_state:
    st.session_state.current_question = None
if "last_result" not in st.session_state:
    st.session_state.last_result = None
if "difficulty" not in st.session_state:
    st.session_state.difficulty = "medium"
if "completed_ids" not in st.session_state:
    st.session_state.completed_ids = []


def mastery_dict():
    return dict(st.session_state.profile["mastery"])


def reset():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()


st.title("🎓 EduPilot AI")
st.caption("Your adaptive AI learning companion — diagnose → teach → adapt → improve")

with st.sidebar:
    st.header("Student Profile")
    name = st.text_input("Name", value=st.session_state.profile["name"])
    target = st.number_input("Target SAT score", 800, 1600, int(st.session_state.profile["target_score"]), 10)
    st.session_state.profile["name"] = name
    st.session_state.profile["target_score"] = target
    if st.button("Reset session"):
        reset()

if not st.session_state.diagnostic_done:
    st.subheader("🎯 Step 1 — Diagnostic Assessment")
    st.write("Answer a short assessment. EduPilot will identify your weakest areas and build your learning path.")
    diagnostic_questions = QUESTIONS[:6]
    idx = st.session_state.diagnostic_index

    if idx < len(diagnostic_questions):
        q = diagnostic_questions[idx]
        st.progress(idx / len(diagnostic_questions))
        st.markdown(f"### Question {idx + 1} of {len(diagnostic_questions)}")
        st.write(f"**{q['topic']} · {q['difficulty'].title()}**")
        st.write(q["question"])
        choice = st.radio("Choose an answer", q["options"], key=f"diag_{q['id']}")
        if st.button("Submit answer", type="primary"):
            selected = q["options"].index(choice)
            st.session_state.diagnostic_answers.append(selected)
            st.session_state.diagnostic_index += 1
            if st.session_state.diagnostic_index == len(diagnostic_questions):
                result = diagnose(diagnostic_questions, st.session_state.diagnostic_answers)
                for topic, score in result["mastery"].items():
                    st.session_state.profile["mastery"][topic] = score
                st.session_state.diagnostic_done = True
            st.rerun()
    else:
        st.session_state.diagnostic_done = True
        st.rerun()
else:
    tabs = st.tabs(["🧠 Adaptive Tutor", "📊 Progress", "📅 Study Plan"])

    with tabs[0]:
        st.subheader("🤖 Step 2 — Adaptive Tutor")
        mastery = mastery_dict()
        weak = sorted(mastery, key=mastery.get)[:3] if mastery else []
        preferred = weak[0] if weak else None

        if st.session_state.current_question is None:
            q = choose_question(
                QUESTIONS,
                mastery,
                preferred_topic=preferred,
                difficulty=st.session_state.difficulty,
                exclude_ids=st.session_state.completed_ids,
            )
            if q is None:
                st.session_state.completed_ids = []
                q = choose_question(QUESTIONS, mastery, preferred_topic=preferred, difficulty=st.session_state.difficulty)
            st.session_state.current_question = q

        q = st.session_state.current_question
        st.markdown(f"### {q['question']}")
        st.caption(f"Topic: {q['topic']} • Skill: {q['subtopic']} • Difficulty: {q['difficulty'].title()}")
        choice = st.radio("Your answer", q["options"], key=f"practice_{q['id']}_{len(st.session_state.profile['answers'])}")

        if st.button("Check answer", type="primary"):
            selected = q["options"].index(choice)
            correct = selected == q["answer"]
            update_profile(st.session_state.profile, q, correct)
            st.session_state.completed_ids.append(q["id"])
            st.session_state.last_result = {
                "correct": correct,
                "selected": selected,
                "answer": q["answer"],
                "question": q,
            }
            st.session_state.difficulty = next_difficulty(q["difficulty"], correct)
            st.session_state.current_question = None
            st.rerun()

        if st.session_state.last_result:
            result = st.session_state.last_result
            st.divider()
            if result["correct"]:
                st.success("✅ Correct! EduPilot is increasing the challenge.")
            else:
                st.error("❌ Not quite. EduPilot is scaffolding the next question.")
            explanation = ai_explain(
                result["question"],
                result["selected"],
                result["answer"],
                os.getenv("OPENAI_API_KEY"),
            )
            st.info(explanation)

    with tabs[1]:
        st.subheader("📊 Your Learning Profile")
        mastery = mastery_dict()
        if mastery:
            cols = st.columns(len(mastery))
            for col, (topic, score) in zip(cols, mastery.items()):
                col.metric(topic, f"{round(score * 100)}%")
                col.progress(float(score))

        attempts = sum(st.session_state.profile["attempts"].values())
        correct = sum(st.session_state.profile["correct"].values())
        accuracy = correct / attempts if attempts else 0
        st.metric("Overall accuracy", f"{round(accuracy * 100)}%")
        st.metric("Questions completed", attempts)
        st.metric("Target score", st.session_state.profile["target_score"])

        if mastery:
            weak = sorted(mastery, key=mastery.get)[:3]
            st.markdown("### 🔎 Current weak areas")
            for topic in weak:
                st.write(f"🔴 **{topic}** — {round(mastery[topic] * 100)}% mastery")

    with tabs[2]:
        st.subheader("📅 Dynamic Study Plan")
        plan = build_plan(mastery_dict())
        st.write("EduPilot continuously changes this plan as your mastery changes.")
        for day, item in enumerate(plan, 1):
            st.markdown(f"**Day {day}:** {item}")

st.divider()
st.caption("EduPilot AI • Hackathon MVP • Built for adaptive, accessible learning")
