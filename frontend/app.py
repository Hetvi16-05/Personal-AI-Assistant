import streamlit as st
import httpx

API = "http://localhost:8000"

st.set_page_config(
    page_title="Personal AI Assistant",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.metric-card {
    background: linear-gradient(135deg, #1e1e2e, #2a2a3e);
    border: 1px solid #3a3a5e;
    border-radius: 12px;
    padding: 1.2rem;
    margin-bottom: 0.8rem;
}
.metric-card h4 { color: #a0a0c0; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.1em; margin: 0 0 0.3rem; }
.metric-card p  { color: #ffffff; font-size: 1.4rem; font-weight: 700; margin: 0; }

.coach-box {
    background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
    border-left: 4px solid #6c63ff;
    border-radius: 12px;
    padding: 1.5rem;
    color: #e0e0ff;
    line-height: 1.7;
}
.action-box {
    background: linear-gradient(135deg, #1a1a2e, #16213e);
    border: 1px solid #6c63ff55;
    border-radius: 12px;
    padding: 1.2rem;
    color: #c0c0ff;
}
.score-pill {
    display: inline-block;
    background: #6c63ff22;
    border: 1px solid #6c63ff66;
    border-radius: 20px;
    padding: 2px 12px;
    font-size: 0.8rem;
    color: #a0a0ff;
    margin-left: 8px;
}
</style>
""", unsafe_allow_html=True)


# ── Helpers ───────────────────────────────────────────────
def api_get(path: str):
    try:
        r = httpx.get(f"{API}{path}", timeout=30)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        st.error(f"API error: {e}")
        return None


def api_post(path: str, data: dict):
    try:
        r = httpx.post(f"{API}{path}", json=data, timeout=60)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        st.error(f"API error: {e}")
        return None


def api_patch(path: str, data: dict):
    try:
        r = httpx.patch(f"{API}{path}", json=data, timeout=15)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        st.error(f"API error: {e}")
        return None


# ── Sidebar ───────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🧠 Personal AI Assistant")
    st.markdown("---")

    user = api_get("/users/me")
    if user:
        st.markdown(f"**👤 {user['name']}**")
        if user.get("skills"):
            st.caption(f"🛠 {user['skills']}")
        if user.get("interests"):
            st.caption(f"💡 {user['interests']}")
        st.markdown("---")

    page = st.radio(
        "Navigate",
        ["🏠 Dashboard", "💬 AI Chat", "🎯 Goals", "📋 Tasks", "📁 Projects", "📊 Weekly Review"],
        label_visibility="collapsed"
    )


# ══════════════════════════════════════════════════════════
# DASHBOARD
# ══════════════════════════════════════════════════════════
if page == "🏠 Dashboard":
    st.title("🏠 Dashboard")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("🤖 Daily Briefing")
        if st.button("🔄 Generate Today's Briefing", use_container_width=True):
            with st.spinner("Asking your AI coach..."):
                result = api_get("/ai/daily-coach")
                if result:
                    st.markdown(f'<div class="coach-box">{result["briefing"]}</div>', unsafe_allow_html=True)
                    if result.get("top_tasks"):
                        st.markdown("**📌 Top Tasks Today:**")
                        for t in result["top_tasks"]:
                            st.markdown(f"- {t['title']} `score: {t['score']}`")

    with col2:
        st.subheader("⚡ Next Best Action")
        if st.button("🎯 What should I do now?", use_container_width=True):
            with st.spinner("Calculating..."):
                result = api_get("/ai/next-action")
                if result:
                    if result.get("recommended_action"):
                        st.markdown(f"""
<div class="action-box">
<h4>✅ {result['recommended_action']}</h4>
<span class="score-pill">score: {result['score']}</span>
<p style="margin-top:0.8rem; color:#a0a0cc; font-size:0.9rem;">{result['reason']}</p>
</div>
""", unsafe_allow_html=True)
                    else:
                        st.info(result.get("reason", "No tasks found."))

    st.markdown("---")

    # Stats
    st.subheader("📊 Quick Stats")
    goals_data = api_get("/goals") or []
    tasks_data = api_get("/tasks") or []
    pending = [t for t in tasks_data if t["status"] in ("pending", "in_progress")]
    completed = [t for t in tasks_data if t["status"] == "completed"]

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f'<div class="metric-card"><h4>Active Goals</h4><p>{len([g for g in goals_data if g["status"]=="active"])}</p></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="metric-card"><h4>Pending Tasks</h4><p>{len(pending)}</p></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="metric-card"><h4>Completed</h4><p>{len(completed)}</p></div>', unsafe_allow_html=True)
    with c4:
        pct = round(len(completed) / len(tasks_data) * 100) if tasks_data else 0
        st.markdown(f'<div class="metric-card"><h4>Completion %</h4><p>{pct}%</p></div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════
# AI CHAT
# ══════════════════════════════════════════════════════════
elif page == "💬 AI Chat":
    st.title("💬 AI Chat")
    st.caption("Chat with your personal AI mentor. It knows your goals, tasks, and memory.")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    user_input = st.chat_input("Ask me anything...")

    if user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                result = api_post("/ai/chat", {"message": user_input})
                if result:
                    response = result.get("response", "Sorry, I couldn't generate a response.")
                    st.markdown(response)
                    st.session_state.chat_history.append({"role": "assistant", "content": response})


# ══════════════════════════════════════════════════════════
# GOALS
# ══════════════════════════════════════════════════════════
elif page == "🎯 Goals":
    st.title("🎯 Goals")

    with st.expander("➕ Add New Goal"):
        with st.form("new_goal"):
            title = st.text_input("Goal Title")
            desc = st.text_area("Description", height=80)
            deadline = st.date_input("Deadline (optional)")
            submitted = st.form_submit_button("Create Goal")
            if submitted and title:
                result = api_post("/goals", {
                    "title": title,
                    "description": desc,
                    "deadline": str(deadline) + "T00:00:00" if deadline else None
                })
                if result:
                    st.success(f"✅ Goal '{title}' created!")
                    st.rerun()

    goals = api_get("/goals") or []
    for g in goals:
        status_emoji = {"active": "🟢", "completed": "✅", "paused": "⏸️"}.get(g["status"], "⚪")
        with st.expander(f"{status_emoji} {g['title']}"):
            st.markdown(f"**Description:** {g['description'] or 'None'}")
            st.markdown(f"**Status:** {g['status']} | **Deadline:** {g['deadline'][:10] if g['deadline'] else 'None'}")

            # Generate roadmap
            if st.button(f"🗺 Generate AI Roadmap", key=f"roadmap_{g['id']}"):
                with st.spinner("Generating your personalized roadmap..."):
                    result = api_post("/ai/generate-roadmap", {"goal_id": g["id"]})
                    if result:
                        st.success("Roadmap generated!")
                        st.markdown(f"**Summary:** {result['summary']}")
                        for ms in result.get("milestones", []):
                            st.markdown(f"**{ms['period']} — {ms['title']}:** {ms['description']}")


# ══════════════════════════════════════════════════════════
# TASKS
# ══════════════════════════════════════════════════════════
elif page == "📋 Tasks":
    st.title("📋 Tasks")

    goals = api_get("/goals") or []
    goal_map = {g["id"]: g["title"] for g in goals}

    tab1, tab2 = st.tabs(["📋 View Tasks", "➕ Add Task"])

    with tab1:
        status_filter = st.selectbox("Filter by status", ["all", "pending", "in_progress", "completed"])
        path = "/tasks" if status_filter == "all" else f"/tasks?status={status_filter}"
        tasks = api_get(path) or []

        for t in tasks:
            status_emoji = {"pending": "🔵", "in_progress": "🟡", "completed": "✅", "cancelled": "❌"}.get(t["status"], "⚪")
            goal_name = goal_map.get(t.get("goal_id"), "No goal")
            with st.expander(f"{status_emoji} {t['title']} — {goal_name}"):
                st.markdown(f"**Description:** {t['description'] or 'None'}")
                st.markdown(f"**Deadline:** {t['deadline'][:10] if t['deadline'] else 'None'}")
                cols = st.columns(4)
                cols[0].metric("Impact", f"{t['impact_score']}/10")
                cols[1].metric("Urgency", f"{t['urgency_score']}/10")
                cols[2].metric("Effort", f"{t['effort_score']}/10")
                cols[3].metric("Alignment", f"{t['alignment_score']}/10")

                col_a, col_b = st.columns(2)
                if t["status"] != "completed":
                    if col_a.button("✅ Mark Complete", key=f"done_{t['id']}"):
                        api_patch(f"/tasks/{t['id']}", {"status": "completed"})
                        st.rerun()
                if col_b.button("🗑 Delete", key=f"del_{t['id']}"):
                    httpx.delete(f"{API}/tasks/{t['id']}")
                    st.rerun()

    with tab2:
        with st.form("new_task"):
            title = st.text_input("Task Title *")
            desc = st.text_area("Description", height=80)
            goal_options = {g["title"]: g["id"] for g in goals}
            selected_goal = st.selectbox("Link to Goal (optional)", ["None"] + list(goal_options.keys()))
            deadline = st.date_input("Deadline (optional)")
            st.markdown("**Scores (1–10)**")
            c1, c2, c3, c4 = st.columns(4)
            impact = c1.slider("Impact", 1, 10, 5)
            urgency = c2.slider("Urgency", 1, 10, 5)
            effort = c3.slider("Effort", 1, 10, 5)
            alignment = c4.slider("Alignment", 1, 10, 5)
            submitted = st.form_submit_button("Create Task")
            if submitted and title:
                payload = {
                    "title": title,
                    "description": desc,
                    "goal_id": goal_options.get(selected_goal) if selected_goal != "None" else None,
                    "deadline": str(deadline) + "T00:00:00" if deadline else None,
                    "impact_score": float(impact),
                    "urgency_score": float(urgency),
                    "effort_score": float(effort),
                    "alignment_score": float(alignment)
                }
                result = api_post("/tasks", payload)
                if result:
                    st.success(f"✅ Task '{title}' created!")
                    st.rerun()


# ══════════════════════════════════════════════════════════
# PROJECTS
# ══════════════════════════════════════════════════════════
elif page == "📁 Projects":
    st.title("📁 Projects")

    goals = api_get("/goals") or []
    goal_options = {g["title"]: g["id"] for g in goals}

    with st.expander("➕ Add New Project"):
        with st.form("new_project"):
            title = st.text_input("Project Title *")
            desc = st.text_area("Description", height=80)
            selected_goal = st.selectbox("Link to Goal", ["None"] + list(goal_options.keys()))
            deadline = st.date_input("Deadline (optional)")
            submitted = st.form_submit_button("Create Project")
            if submitted and title:
                result = api_post("/projects", {
                    "title": title,
                    "description": desc,
                    "goal_id": goal_options.get(selected_goal) if selected_goal != "None" else None,
                    "deadline": str(deadline) + "T00:00:00" if deadline else None
                })
                if result:
                    st.success(f"✅ Project '{title}' created!")
                    st.rerun()

    projects = api_get("/projects") or []
    goal_map = {g["id"]: g["title"] for g in goals}
    for p in projects:
        status_emoji = {"active": "🟢", "completed": "✅", "on_hold": "⏸️"}.get(p["status"], "⚪")
        linked_goal = goal_map.get(p.get("goal_id"), "No goal")
        with st.expander(f"{status_emoji} {p['title']} → {linked_goal}"):
            st.markdown(f"**Description:** {p['description'] or 'None'}")
            st.markdown(f"**Deadline:** {p['deadline'][:10] if p['deadline'] else 'None'}")


# ══════════════════════════════════════════════════════════
# WEEKLY REVIEW
# ══════════════════════════════════════════════════════════
elif page == "📊 Weekly Review":
    st.title("📊 Weekly Review")
    st.caption("AI-generated summary of your week's progress.")

    if st.button("🔄 Generate This Week's Review", use_container_width=True):
        with st.spinner("Analyzing your week..."):
            result = api_get("/ai/weekly-review")
            if result:
                c1, c2, c3 = st.columns(3)
                c1.metric("Tasks Completed", result["tasks_completed"])
                c2.metric("Completion Rate", f"{result['completion_percentage']}%")
                c3.metric("Most Active Goal", result["most_active_goal"] or "N/A")
                st.markdown("---")
                st.markdown(f'<div class="coach-box">{result["ai_summary"]}</div>', unsafe_allow_html=True)
