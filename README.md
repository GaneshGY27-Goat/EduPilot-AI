# EduPilot AI 🚀

**An adaptive AI learning agent for personalized SAT preparation.**

EduPilot is more than a chatbot: it diagnoses learning gaps, adapts question difficulty, explains misconceptions, tracks mastery, and replans study priorities around the student.

## Hackathon Demo Flow

1. Take a short diagnostic assessment.
2. EduPilot identifies weak topics and estimates mastery.
3. The agent selects the next question based on performance.
4. Wrong answers trigger targeted explanations and easier scaffolding.
5. Correct answers increase mastery and unlock harder questions.
6. The personalized study plan changes automatically as the student improves.

## Features

- 🎯 Diagnostic assessment
- 🧠 Knowledge-gap detection
- 🤖 Adaptive question selection
- 📚 Step-by-step tutoring
- 📈 Topic mastery tracking
- 📅 Dynamic study planning
- 🌐 Low-bandwidth friendly Streamlit UI
- 🔌 Optional OpenAI-powered explanations and planning
- 📴 Demo mode works without an API key

## Tech Stack

- Python
- Streamlit
- Pandas
- Scikit-learn
- Optional OpenAI API

## Run Locally

```bash
git clone https://github.com/GaneshGY27-Goat/EduPilot-AI.git
cd EduPilot-AI
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

The app works in demo mode without an API key. To enable LLM explanations, create `.env` from `.env.example` and add your key.

## Project Structure

```text
EduPilot-AI/
├── app.py
├── agents/
│   ├── __init__.py
│   ├── diagnostic_agent.py
│   ├── tutor_agent.py
│   ├── adaptive_agent.py
│   └── planner_agent.py
├── models/
│   ├── __init__.py
│   └── mastery_model.py
├── data/
│   └── questions.json
├── utils/
│   ├── __init__.py
│   └── student_profile.py
├── requirements.txt
├── .env.example
└── .gitignore
```

## Agent Architecture

```text
Student
   ↓
Diagnostic Agent → Knowledge Profile
   ↓
Adaptive Agent → Next Best Question
   ↓
Tutor Agent → Explanation / Scaffolding
   ↓
Mastery Model → Updated Topic Scores
   ↓
Planner Agent → Updated Study Plan
   ↺
```

## Impact

EduPilot is designed around students who may not have access to expensive one-to-one tutoring. A lightweight, adaptive learning companion can provide individualized practice, feedback, and planning on an ordinary device. Future versions can add multilingual support, offline lesson packs, teacher dashboards, and voice tutoring.

## Important Note

This is a hackathon MVP. The SAT question bank is a small demonstration dataset and should not be treated as official College Board material.

## License

MIT
