import json
import os
from pathlib import Path

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from agents.adaptive_agent import choose_question, next_difficulty
from agents.diagnostic_agent import diagnose
from agents.planner_agent import build_plan
from agents.tutor_agent import ai_explain
from models.mastery_model import MasteryModel
from utils.student_profile import default_profile, update_profile

load_dotenv()

st.set_page_config(page_title="EduPilot AI", page_icon="🎓", layout="wide", initial_sidebar_state="expanded")

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
    st.session_state.clear()
    st.rerun()


st.markdown(
    """
    <style>
    .stApp { background: #f7f9fc; }
    [data-testid="stSidebar"] { background: #111827; }
    [data-testid="stSidebar"] * { color: #f9fafb !important; }
    .hero { padding: 28px 30px; border-radius: 22px; background: linear-gradient(135deg,#111827,#1e3a5f); color:white; margin-bottom:22px; }
    .hero h1 { font-size: 38px; margin:0; }
    .hero p { color:#dbeafe; font-size:17px; margin:8px 0 0; }
    .pill { display:inline-block; padding:6px 11px; border-radius:999px; background:#dbeafe; color:#1e3a5f; font-weight:700; font-size:12px; margin-bottom:10px; }
    .card { background:white; padding:20px; border-radius:18px; border:1px solid #e5e7eb; box-shadow:0 4px 16px rgba(15,23,42,.05); margin-bottom:16px; }
    .card-title { font-size:14px; color:#64748b; font-weight:700; text-transform:uppercase; letter-spacing:.04em; }
    .big { font-size:30px; font-weight:800; color:#111827; }
    .small { color:#64748b; font-size:13px; }
    .agent { background:#eef6ff; border-left:5px solid #2563eb; padding:15px 18px; border-radius:12px; margin:12px 0; }
    </style>
    """,
    unsafe_allow_html=True,
)

name = st.session_state.profile["name"]

with st.sidebar:
    st.markdown("# 🎓 EduPilot")
    st.caption("Adaptive AI Learning Companion")
    st.divider()
    st.markdown("### Student profile")
    name = st.text_input("Name", value=name)
    target = st.number_input("Target SAT score", 800, 1600, int(st.session_state.profile["target_score"]), 10)
    st.session_state.profile["name"] = name
    st.session_state.profile["target_score"] = target
    st.divider()
    st.markdown("**Agent status**")
    st.success("● Online")
    st.caption("Diagnosing • Adapting • Planning")
    if st.button("↻ Reset learning journey", use_container_width=True):
        reset()

st.markdown(
    f'''<div class="hero"><span class="pill">AI-POWERED EDUCATION AGENT</span><h1>Welcome back, {name} 👋</h1><p>Your learning path changes with you. EduPilot finds your weak areas, teaches you, and decides what you should practice next.</p></div>''',
    unsafe_allow_html=True,
)

if not st.session_state.diagnostic_done:
    diagnostic_questions = QUESTIONS[:6]
    idx = st.session_state.diagnostic_index
    st.markdown("## 🎯 Let's understand how you learn")
    st.write("Start with a short diagnostic. Your answers will shape the rest of your learning journey.")
    st.progress(idx / len(diagnostic_questions), text=f"Diagnostic progress · {idx}/{len(diagnostic_questions)}")

    if idx < len(diagnostic_questions):
        q = diagnostic_questions[idx]
        st.markdown(f'<div class="card"><div class="card-title">Question {idx + 1} of {len(diagnostic_questions)}</div><h2>{q["question"]}</h2><div class="small">{q["topic"]} · {q["subtopic"]} · {q["difficulty"].title()}</div></div>', unsafe_allow_html=True)
        choice = st.radio("Choose your answer", q["options"], key=f"diag_{q['id']}")
        if st.button("Submit answer →", type="primary", use_container_width=True):
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
    mastery = mastery_dict()
    attempts = sum(st.session_state.profile["attempts"].values())
    correct = sum(st.session_state.profile["correct"].values())
    accuracy = correct / attempts if attempts else 0
    weak = sorted(mastery, key=mastery.get)[:3] if mastery else []

    m1, m2, m3, m4 = st.columns(4)
    m1.markdown(f'<div class="card"><div class="card-title">Target SAT</div><div class="big">{st.session_state.profile["target_score"]}</div><div class="small">Your goal</div></div>', unsafe_allow_html=True)
    m2.markdown(f'<div class="card"><div class="card-title">Accuracy</div><div class="big">{round(accuracy*100)}%</div><div class="small">Across practice</div></div>', unsafe_allow_html=True)
    m3.markdown(f'<div class="card"><div class="card-title">Questions</div><div class="big">{attempts}</div><div class="small">Completed</div></div>', unsafe_allow_html=True)
    m4.markdown(f'<div class="card"><div class="card-title">Focus area</div><div class="big">{weak[0] if weak else "—"}</div><div class="small">Highest priority</div></div>', unsafe_allow_html=True)

    tabs = st.tabs(["🧠 Adaptive Tutor", "📊 Progress", "📅 Study Plan"])

    with tabs[0]:
        st.markdown("## Your AI tutor")
        if weak:
            st.markdown(f'<div class="agent"><b>🤖 EduPilot decided:</b> We are focusing on <b>{weak[0]}</b> because it is currently your weakest area. Your next question will be selected around that gap.</div>', unsafe_allow_html=True)

        if st.session_state.current_question is None:
            preferred = weak[0] if weak else None
            q = choose_question(QUESTIONS, mastery, preferred_topic=preferred, difficulty=st.session_state.difficulty, exclude_ids=st.session_state.completed_ids)
            if q is None:
                st.session_state.completed_ids = []
                q = choose_question(QUESTIONS, mastery, preferred_topic=preferred, difficulty=st.session_state.difficulty)
            st.session_state.current_question = q

        q = st.session_state.current_question
        st.markdown(f'<div class="card"><div class="card-title">Adaptive practice · {q["difficulty"].title()}</div><h2>{q["question"]}</h2><div class="small">{q["topic"]} · {q["subtopic"]}</div></div>', unsafe_allow_html=True)
        choice = st.radio("Your answer", q["options"], key=f"practice_{q['id']}_{len(st.session_state.profile['answers'])}")
        if st.button("Check answer", type="primary", use_container_width=True):
            selected = q["options"].index(choice)
            is_correct = selected == q["answer"]
            update_profile(st.session_state.profile, q, is_correct)
            st.session_state.completed_ids.append(q["id"])
            st.session_state.last_result = {"correct": is_correct, "selected": selected, "answer": q["answer"], "question": q}
            st.session_state.difficulty = next_difficulty(q["difficulty"], is_correct)
            st.session_state.current_question = None
            st.rerun()

        if st.session_state.last_result:
            result = st.session_state.last_result
            st.divider()
            if result["correct"]:
                st.success("✅ Correct — EduPilot is increasing the challenge for your next question.")
            else:
                st.warning("💡 Not quite — EduPilot is lowering the difficulty and reinforcing this concept.")
            explanation = ai_explain(result["question"], result["selected"], result["answer"], os.getenv("OPENAI_API_KEY"))
            st.markdown("### Tutor feedback")
            st.info(explanation)

    with tabs[1]:
        st.markdown("## 📊 Your learning profile")
        if mastery:
            data = pd.DataFrame({"Topic": list(mastery.keys()), "Mastery": [round(v * 100) for v in mastery.values()]})
            for _, row in data.iterrows():
                st.markdown(f"**{row['Topic']}** · {row['Mastery']}%")
                st.progress(int(row["Mastery"]), text="Mastery")

        if mastery:
            model = MasteryModel()
            st.markdown("### 🧪 AI mastery estimate")
            for topic, score in mastery.items():
                topic_attempts = st.session_state.profile["attempts"][topic]
                prediction = model.predict(score, topic_attempts)
                st.write(f"**{topic}** — estimated mastery probability: **{round(prediction*100)}%**")

        if weak:
            st.markdown("### 🔎 Current focus areas")
            for topic in weak:
                st.write(f"🔴 {topic} — {round(mastery[topic]*100)}% mastery")

    with tabs[2]:
        st.markdown("## 📅 Your dynamic study plan")
        st.markdown('<div class="agent"><b>Planner agent:</b> This plan is generated from your current mastery and will change as your performance changes.</div>', unsafe_allow_html=True)
        plan = build_plan(mastery)
        for day, item in enumerate(plan, 1):
            st.markdown(f'<div class="card"><div class="card-title">Day {day}</div><b>{item}</b></div>', unsafe_allow_html=True)

st.divider()
st.caption("EduPilot AI · Adaptive learning for students who deserve a personal tutor")
