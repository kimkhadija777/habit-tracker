import streamlit as st
import pandas as pd
import datetime
import json
import os

st.set_page_config(
    page_title="Atomic Habit Tracker",
    page_icon="⚡",
    layout="wide"
)

DATA_FILE = "habits_data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {
        "identity": "I am a consistent individual building system-driven success.",
        "habits": [
            {
                "name": "Solve 1 Coding Problem",
                "identity": "Computer Scientist",
                "cue": "After my evening tea",
                "reward": "10 minutes relaxation",
                "logs": {},
                "streak": 0
            }
        ]
    }

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

def calculate_streak(logs):
    today = datetime.date.today()
    streak = 0
    current_day = today
    
    while True:
        d_str = current_day.isoformat()
        if logs.get(d_str, False):
            streak += 1
            current_day -= datetime.timedelta(days=1)
        elif current_day == today:
            current_day -= datetime.timedelta(days=1)
        else:
            break
    return streak

if "data" not in st.session_state:
    st.session_state.data = load_data()

st.title("⚡ Atomic Habit Tracker")
st.caption("Build identity-based habits with 1% daily improvements.")

st.subheader("🎯 Core Identity Focus")
new_identity = st.text_input("Define who you are becoming:", st.session_state.data["identity"])
if new_identity != st.session_state.data["identity"]:
    st.session_state.data["identity"] = new_identity
    save_data(st.session_state.data)

st.divider()

with st.expander("➕ Add a New Atomic Habit", expanded=False):
    with st.form("new_habit_form"):
        col1, col2 = st.columns(2)
        with col1:
            h_name = st.text_input("Habit Name", placeholder="e.g., Read 10 Pages")
            h_identity = st.text_input("Identity Tag", placeholder="e.g., Lifelong Learner")
        with col2:
            h_cue = st.text_input("Cue / Habit Stack", placeholder="e.g., After I sit in bed")
            h_reward = st.text_input("Reward", placeholder="e.g., Check off tracker")
        
        submitted = st.form_submit_button("Create Habit")
        if submitted and h_name.strip():
            new_habit = {
                "name": h_name.strip(),
                "identity": h_identity.strip() or "Disciplined Self",
                "cue": h_cue.strip() or "Immediate Action",
                "reward": h_reward.strip() or "Satisfaction",
                "logs": {},
                "streak": 0
            }
            st.session_state.data["habits"].append(new_habit)
            save_data(st.session_state.data)
            st.success(f"Added habit: {h_name}")
            st.rerun()

st.subheader("📅 Log Today's Habits")
today_str = datetime.date.today().isoformat()

if not st.session_state.data["habits"]:
    st.info("No habits added yet. Expand the section above to add one!")
else:
    for idx, habit in enumerate(st.session_state.data["habits"]):
        cols = st.columns([0.05, 0.55, 0.4])
        
        is_done = habit["logs"].get(today_str, False)
        checked = cols[0].checkbox("", value=is_done, key=f"habit_{idx}")
        
        cols[1].markdown(f"**[{habit['identity']}]** {habit['name']}")
        cols[1].caption(f"**Cue:** {habit['cue']} | **Reward:** {habit['reward']}")
        
        streak = calculate_streak(habit["logs"])
        cols[2].markdown(f"🔥 **Streak:** {streak} days")
        
        if checked != is_done:
            st.session_state.data["habits"][idx]["logs"][today_str] = checked
            st.session_state.data["habits"][idx]["streak"] = streak
            save_data(st.session_state.data)
            st.rerun()

st.divider()

st.subheader("📊 Performance Summary")
if st.session_state.data["habits"]:
    summary_data = []
    for h in st.session_state.data["habits"]:
        logs = h["logs"]
        total_days = len(logs)
        completed_days = sum(1 for status in logs.values() if status)
        rate = round((completed_days / total_days * 100), 1) if total_days > 0 else 0.0
        
        summary_data.append({
            "Identity": h["identity"],
            "Habit Name": h["name"],
            "Active Streak": f"🔥 {calculate_streak(h['logs'])} Days",
            "Completion Rate": f"{rate}%",
            "Cue": h["cue"]
        })
    
    st.dataframe(pd.DataFrame(summary_data), use_container_width=True)
