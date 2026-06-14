import streamlit as st
import httpx
import os
import plotly.graph_objects as go
import plotly.express as px

API = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(
    page_title="Personal AI Assistant",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── CSS ──────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Outfit', sans-serif;
}

/* Main background radial gradient overlay */
.stApp {
    background: radial-gradient(circle at 10% 20%, rgba(20, 20, 35, 1) 0%, rgba(10, 10, 20, 1) 90%);
}

/* Glassmorphism metric cards */
.metric-card {
    background: rgba(255, 255, 255, 0.03);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 16px;
    padding: 1.3rem 1.5rem;
    margin-bottom: 1rem;
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
    transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
}
.metric-card:hover {
    transform: translateY(-4px);
    border-color: rgba(123, 44, 191, 0.4);
    box-shadow: 0 15px 35px 0 rgba(123, 44, 191, 0.15);
}
.metric-card h4 {
    color: #b0b0d0;
    font-size: 0.72rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.15em;
    margin: 0 0 0.5rem;
}
.metric-card p {
    background: linear-gradient(90deg, #4cc9f0, #7b2cbf);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size: 1.8rem;
    font-weight: 700;
    margin: 0;
}

/* Glassmorphism briefing card */
.coach-box {
    background: rgba(255, 255, 255, 0.02);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-left: 5px solid #7b2cbf;
    border-radius: 16px;
    padding: 1.75rem;
    color: #e2e8f0;
    line-height: 1.8;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.25);
    margin-bottom: 1.5rem;
}

/* Next Best Action box */
.action-box {
    background: linear-gradient(135deg, rgba(123, 44, 191, 0.12) 0%, rgba(58, 12, 163, 0.12) 100%);
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    border: 1px solid rgba(123, 44, 191, 0.35);
    border-radius: 16px;
    padding: 1.5rem;
    color: #d0d2ff;
    box-shadow: 0 8px 32px 0 rgba(123, 44, 191, 0.08);
    transition: all 0.3s ease;
}
.action-box:hover {
    border-color: rgba(76, 201, 240, 0.5);
    box-shadow: 0 15px 35px 0 rgba(76, 201, 240, 0.15);
}

/* Insight card overrides */
.insight-card {
    background: rgba(255, 255, 255, 0.03);
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 14px;
    padding: 1.25rem;
    margin-bottom: 0.8rem;
    color: #e2e8f0;
    transition: all 0.25s ease;
}
.insight-card:hover {
    background: rgba(255, 255, 255, 0.05);
    border-color: rgba(247, 37, 133, 0.3);
}
.insight-card .type-badge {
    font-size: 0.65rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.15em;
    color: #f72585;
    margin-bottom: 0.5rem;
}

/* Login/Register Panel */
.login-box {
    max-width: 440px;
    margin: 4rem auto;
    background: rgba(255, 255, 255, 0.03);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 24px;
    padding: 3rem 2.5rem;
    box-shadow: 0 20px 50px rgba(0, 0, 0, 0.4);
}
</style>
""", unsafe_allow_html=True)


# ── Helpers ───────────────────────────────────────────────
def get_headers():
    token = st.session_state.get("token", "")
    return {"Authorization": f"Bearer {token}"} if token else {}


def api_get(path: str):
    try:
        r = httpx.get(f"{API}{path}", headers=get_headers(), timeout=30)
        if r.status_code == 401:
            st.session_state.token = None
            st.rerun()
        r.raise_for_status()
        return r.json()
    except httpx.HTTPStatusError as e:
        st.error(f"Error: {e.response.json().get('detail', str(e))}")
        return None
    except Exception as e:
        st.error(f"Connection error: {e}")
        return None


def api_post(path: str, data: dict):
    try:
        r = httpx.post(f"{API}{path}", json=data, headers=get_headers(), timeout=60)
        if r.status_code == 401:
            st.session_state.token = None
            st.rerun()
        r.raise_for_status()
        return r.json()
    except httpx.HTTPStatusError as e:
        st.error(f"Error: {e.response.json().get('detail', str(e))}")
        return None
    except Exception as e:
        st.error(f"Connection error: {e}")
        return None


def api_patch(path: str, data: dict):
    try:
        r = httpx.patch(f"{API}{path}", json=data, headers=get_headers(), timeout=15)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        st.error(f"Error: {e}")
        return None


# ══════════════════════════════════════════════════════════
# AUTH — Login / Register
# ══════════════════════════════════════════════════════════
def show_auth():
    st.markdown('<div class="login-box">', unsafe_allow_html=True)
    st.markdown("## 🧠 Personal AI Assistant")
    st.markdown("Your AI-powered personal mentor")
    st.divider()

    tab_login, tab_register = st.tabs(["Login", "Register"])

    with tab_login:
        with st.form("login_form"):
            email = st.text_input("Email", placeholder="you@example.com")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login", use_container_width=True)
            if submitted and email and password:
                result = api_post("/auth/login", {"email": email, "password": password})
                if result:
                    st.session_state.token = result["access_token"]
                    st.session_state.user = result["user"]
                    st.success("Welcome back!")
                    st.rerun()

    with tab_register:
        with st.form("register_form"):
            name = st.text_input("Your Name")
            email = st.text_input("Email", placeholder="you@example.com")
            password = st.text_input("Password", type="password")
            skills = st.text_input("Skills (optional)", placeholder="Python, Statistics")
            interests = st.text_input("Interests (optional)", placeholder="AI, ML, GATE")
            submitted = st.form_submit_button("Create Account", use_container_width=True)
            if submitted and name and email and password:
                result = api_post("/auth/register", {
                    "name": name, "email": email, "password": password,
                    "skills": skills, "interests": interests
                })
                if result:
                    st.session_state.token = result["access_token"]
                    st.session_state.user = result["user"]
                    st.success("Account created!")
                    st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════
# MAIN APP
# ══════════════════════════════════════════════════════════
if not st.session_state.get("token"):
    show_auth()
    st.stop()

user = st.session_state.get("user", {})

# ── Sidebar ───────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"## 🧠 AI Assistant")
    st.markdown(f"**👤 {user.get('name', 'User')}**")
    if user.get("skills"):
        st.caption(f"🛠 {user['skills']}")
    st.divider()

    page = st.radio(
        "Navigate",
        ["🏠 Dashboard", "💬 Chat", "🎯 Goals", "📋 Tasks",
         "📁 Projects", "💡 Insights", "📈 Analytics", "📊 Weekly Review"],
        label_visibility="collapsed"
    )

    st.divider()
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.token = None
        st.session_state.user = None
        st.rerun()


# ══════════════════════════════════════════════════════════
# DASHBOARD
# ══════════════════════════════════════════════════════════
if page == "🏠 Dashboard":
    st.title(f"🏠 Good day, {user.get('name', '')}!")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("🤖 Daily Briefing")
        if st.button("🔄 Generate Today's Briefing", use_container_width=True):
            with st.spinner("Thinking..."):
                result = api_get("/ai/daily-coach")
                if result:
                    st.markdown(f'<div class="coach-box">{result["briefing"]}</div>',
                                unsafe_allow_html=True)
                    if result.get("top_tasks"):
                        st.markdown("**📌 Today's Focus:**")
                        for t in result["top_tasks"]:
                            st.markdown(f"- {t['title']} `{t['score']}`")

    with col2:
        st.subheader("⚡ Next Action")
        if st.button("🎯 What now?", use_container_width=True):
            with st.spinner("Calculating..."):
                result = api_get("/ai/next-action")
                if result and result.get("recommended_action"):
                    st.markdown(f"""
<div class="action-box">
<strong>✅ {result['recommended_action']}</strong><br>
<small style="color:#8888cc">Score: {result['score']} | Impact: {result.get('estimated_impact','')}</small>
<p style="margin-top:0.7rem;font-size:0.88rem;color:#a0a0cc;">{result.get('reason','')}</p>
<p style="font-size:0.82rem;color:#8080aa;font-style:italic;">{result.get('why_it_matters','')}</p>
</div>""", unsafe_allow_html=True)

    st.divider()
    goals_data = api_get("/goals") or []
    tasks_data = api_get("/tasks") or []
    pending = [t for t in tasks_data if t["status"] in ("pending", "in_progress")]
    completed = [t for t in tasks_data if t["status"] == "completed"]
    pct = round(len(completed) / max(len(tasks_data), 1) * 100)

    c1, c2, c3, c4 = st.columns(4)
    for col, label, val in zip(
        [c1, c2, c3, c4],
        ["Active Goals", "Pending Tasks", "Completed", "Completion %"],
        [len([g for g in goals_data if g["status"] == "active"]),
         len(pending), len(completed), f"{pct}%"]
    ):
        col.markdown(
            f'<div class="metric-card"><h4>{label}</h4><p>{val}</p></div>',
            unsafe_allow_html=True
        )


# ══════════════════════════════════════════════════════════
# CHAT
# ══════════════════════════════════════════════════════════
elif page == "💬 Chat":
    st.title("💬 AI Chat")

    sessions = api_get("/chat/sessions") or []

    col_left, col_right = st.columns([1, 3])

    with col_left:
        st.subheader("Sessions")
        if st.button("➕ New Session", use_container_width=True):
            result = api_post("/chat/sessions", {"title": "New Conversation"})
            if result:
                st.session_state.active_session = result["id"]
                st.rerun()

        for s in sessions:
            label = s["title"][:30] + ("..." if len(s["title"]) > 30 else "")
            if st.button(f"💬 {label}", key=f"sess_{s['id']}", use_container_width=True):
                st.session_state.active_session = s["id"]
                st.rerun()

    with col_right:
        session_id = st.session_state.get("active_session")
        if not session_id:
            st.info("Select or create a session to start chatting.")
        else:
            messages = api_get(f"/chat/sessions/{session_id}/messages") or []
            for msg in messages:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])

            user_input = st.chat_input("Ask your AI mentor...")
            if user_input:
                with st.chat_message("user"):
                    st.markdown(user_input)
                with st.chat_message("assistant"):
                    with st.spinner("Thinking..."):
                        result = api_post(
                            f"/chat/sessions/{session_id}/messages",
                            {"content": user_input}
                        )
                        if result:
                            st.markdown(result["assistant_message"]["content"])
                            st.rerun()


# ══════════════════════════════════════════════════════════
# GOALS
# ══════════════════════════════════════════════════════════
elif page == "🎯 Goals":
    st.title("🎯 Goals")

    with st.expander("➕ Add New Goal"):
        with st.form("new_goal"):
            title = st.text_input("Goal Title *")
            desc = st.text_area("Description", height=80)
            deadline = st.date_input("Deadline (optional)")
            if st.form_submit_button("Create Goal") and title:
                r = api_post("/goals", {"title": title, "description": desc,
                                        "deadline": str(deadline) + "T00:00:00"})
                if r:
                    st.success("✅ Goal created!")
                    st.rerun()

    goals = api_get("/goals") or []
    for g in goals:
        emoji = {"active": "🟢", "completed": "✅", "paused": "⏸️"}.get(g["status"], "⚪")
        with st.expander(f"{emoji} {g['title']}"):
            st.markdown(f"**Status:** {g['status']} | **Deadline:** {g['deadline'][:10] if g['deadline'] else 'None'}")
            st.markdown(g.get("description", "") or "")
            if st.button(f"🗺 Generate AI Roadmap", key=f"rm_{g['id']}"):
                with st.spinner("Generating roadmap with Gemini..."):
                    r = api_post("/ai/generate-roadmap", {"goal_id": g["id"]})
                    if r:
                        st.success("Roadmap generated!")
                        st.markdown(f"**{r['summary']}**")
                        for ms in r.get("milestones", []):
                            st.markdown(f"**{ms['period']} — {ms['title']}:** {ms['description']}")


# ══════════════════════════════════════════════════════════
# TASKS
# ══════════════════════════════════════════════════════════
elif page == "📋 Tasks":
    st.title("📋 Tasks")
    goals = api_get("/goals") or []
    goal_map = {g["id"]: g["title"] for g in goals}
    goal_options = {g["title"]: g["id"] for g in goals}

    tab1, tab2 = st.tabs(["📋 View", "➕ Add"])

    with tab1:
        status_filter = st.selectbox("Status", ["all", "pending", "in_progress", "completed"])
        path = f"/tasks?status={status_filter}" if status_filter != "all" else "/tasks"
        tasks = api_get(path) or []

        for t in tasks:
            emoji = {"pending": "🔵", "in_progress": "🟡", "completed": "✅", "cancelled": "❌"}.get(t["status"], "⚪")
            with st.expander(f"{emoji} {t['title']} — {goal_map.get(t.get('goal_id'), 'No goal')}"):
                st.markdown(t.get("description") or "")
                cols = st.columns(4)
                for col, label, val in zip(cols,
                    ["Impact", "Urgency", "Effort", "Alignment"],
                    [t['impact_score'], t['urgency_score'], t['effort_score'], t['alignment_score']]):
                    col.metric(label, f"{val}/10")

                ca, cb = st.columns(2)
                if t["status"] != "completed":
                    if ca.button("✅ Done", key=f"done_{t['id']}"):
                        api_patch(f"/tasks/{t['id']}", {"status": "completed"})
                        st.rerun()
                if cb.button("🗑 Delete", key=f"del_{t['id']}"):
                    httpx.delete(f"{API}/tasks/{t['id']}", headers=get_headers())
                    st.rerun()

    with tab2:
        with st.form("new_task"):
            title = st.text_input("Title *")
            desc = st.text_area("Description", height=70)
            goal_sel = st.selectbox("Goal", ["None"] + list(goal_options.keys()))
            deadline = st.date_input("Deadline")
            c1, c2, c3, c4 = st.columns(4)
            impact = c1.slider("Impact", 1, 10, 5)
            urgency = c2.slider("Urgency", 1, 10, 5)
            effort = c3.slider("Effort", 1, 10, 5)
            alignment = c4.slider("Alignment", 1, 10, 5)
            if st.form_submit_button("Create Task") and title:
                r = api_post("/tasks", {
                    "title": title, "description": desc,
                    "goal_id": goal_options.get(goal_sel) if goal_sel != "None" else None,
                    "deadline": str(deadline) + "T00:00:00",
                    "impact_score": float(impact), "urgency_score": float(urgency),
                    "effort_score": float(effort), "alignment_score": float(alignment)
                })
                if r:
                    st.success("✅ Task created!")
                    st.rerun()


# ══════════════════════════════════════════════════════════
# PROJECTS
# ══════════════════════════════════════════════════════════
elif page == "📁 Projects":
    st.title("📁 Projects")
    goals = api_get("/goals") or []
    goal_options = {g["title"]: g["id"] for g in goals}
    goal_map = {g["id"]: g["title"] for g in goals}

    with st.expander("➕ Add Project"):
        with st.form("new_project"):
            title = st.text_input("Title *")
            desc = st.text_area("Description", height=70)
            goal_sel = st.selectbox("Goal", ["None"] + list(goal_options.keys()))
            deadline = st.date_input("Deadline")
            if st.form_submit_button("Create Project") and title:
                r = api_post("/projects", {
                    "title": title, "description": desc,
                    "goal_id": goal_options.get(goal_sel) if goal_sel != "None" else None,
                    "deadline": str(deadline) + "T00:00:00"
                })
                if r:
                    st.success("✅ Project created!")
                    st.rerun()

    projects = api_get("/projects") or []
    for p in projects:
        emoji = {"active": "🟢", "completed": "✅", "on_hold": "⏸️"}.get(p["status"], "⚪")
        with st.expander(f"{emoji} {p['title']} → {goal_map.get(p.get('goal_id'), 'No goal')}"):
            st.markdown(p.get("description") or "")
            st.caption(f"Deadline: {p['deadline'][:10] if p['deadline'] else 'None'}")


# ══════════════════════════════════════════════════════════
# INSIGHTS
# ══════════════════════════════════════════════════════════
elif page == "💡 Insights":
    st.title("💡 AI Insights")
    st.caption("AI-generated insights based on your actual activity data.")

    if st.button("🔮 Generate Fresh Insights", use_container_width=True):
        with st.spinner("Analyzing your data with AI..."):
            insights = api_get("/insights")
            if insights:
                type_icons = {
                    "productivity": "⚡", "learning": "📚",
                    "goal_progress": "🎯", "recommendation": "💡"
                }
                for ins in insights:
                    icon = type_icons.get(ins.get("type", ""), "🔹")
                    st.markdown(f"""
<div class="insight-card">
<div class="type-badge">{icon} {ins.get('type', '').replace('_', ' ').title()}</div>
<div>{ins.get('content', '')}</div>
</div>""", unsafe_allow_html=True)

    st.divider()
    st.subheader("📜 Past Insights")
    history = api_get("/insights/history") or []
    type_icons = {"productivity": "⚡", "learning": "📚", "goal_progress": "🎯", "recommendation": "💡"}
    for ins in history[:10]:
        icon = type_icons.get(ins.get("insight_type", ""), "🔹")
        st.markdown(f"""
<div class="insight-card">
<div class="type-badge">{icon} {ins.get('insight_type','').replace('_',' ').title()} · {ins.get('generated_at','')[:10]}</div>
<div>{ins.get('content','')}</div>
</div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════
# ANALYTICS
# ══════════════════════════════════════════════════════════
elif page == "📈 Analytics":
    st.title("📈 Analytics")

    goals = api_get("/goals") or []
    tasks = api_get("/tasks") or []
    projects = api_get("/projects") or []

    if not tasks and not goals:
        st.info("Add some goals and tasks to see your analytics!")
        st.stop()

    # ── Row 1: Quick metrics ──────────────────────────────
    total = len(tasks)
    completed = [t for t in tasks if t["status"] == "completed"]
    pending = [t for t in tasks if t["status"] == "pending"]
    in_progress = [t for t in tasks if t["status"] == "in_progress"]
    active_goals = [g for g in goals if g["status"] == "active"]

    c1, c2, c3, c4 = st.columns(4)
    for col, label, val in zip(
        [c1, c2, c3, c4],
        ["Total Tasks", "Completed", "In Progress", "Active Goals"],
        [total, len(completed), len(in_progress), len(active_goals)]
    ):
        col.markdown(f'<div class="metric-card"><h4>{label}</h4><p>{val}</p></div>',
                     unsafe_allow_html=True)

    st.divider()

    col_a, col_b = st.columns(2)

    with col_a:
        # Task Status Donut
        if tasks:
            status_counts = {
                "Completed": len(completed),
                "In Progress": len(in_progress),
                "Pending": len(pending),
            }
            fig = go.Figure(data=[go.Pie(
                labels=list(status_counts.keys()),
                values=list(status_counts.values()),
                hole=0.55,
                marker_colors=["#6c63ff", "#f0a500", "#444466"]
            )])
            fig.update_layout(
                title="Task Status Breakdown",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font_color="#c0c0ff",
                showlegend=True,
                margin=dict(t=40, b=0, l=0, r=0)
            )
            st.plotly_chart(fig, use_container_width=True)

    with col_b:
        # Goal Progress Bars
        if goals and tasks:
            goal_map = {g["id"]: g["title"] for g in goals}
            goal_total = {}
            goal_done = {}
            for t in tasks:
                gid = t.get("goal_id")
                if gid:
                    goal_total[gid] = goal_total.get(gid, 0) + 1
                    if t["status"] == "completed":
                        goal_done[gid] = goal_done.get(gid, 0) + 1

            goal_names, goal_pcts = [], []
            for gid, total_count in goal_total.items():
                done = goal_done.get(gid, 0)
                pct = round(done / total_count * 100, 1) if total_count > 0 else 0
                goal_names.append(goal_map.get(gid, f"Goal {gid}")[:25])
                goal_pcts.append(pct)

            if goal_names:
                fig2 = go.Figure(go.Bar(
                    x=goal_pcts, y=goal_names,
                    orientation='h',
                    marker_color="#6c63ff",
                    text=[f"{p}%" for p in goal_pcts],
                    textposition='outside'
                ))
                fig2.update_layout(
                    title="Goal Progress %",
                    xaxis=dict(range=[0, 110], showgrid=False),
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font_color="#c0c0ff",
                    margin=dict(t=40, b=0, l=0, r=60)
                )
                st.plotly_chart(fig2, use_container_width=True)

    st.divider()

    # Task Score Distribution
    if tasks:
        impact_scores = [t["impact_score"] for t in tasks]
        urgency_scores = [t["urgency_score"] for t in tasks]
        titles = [t["title"][:20] + ("..." if len(t["title"]) > 20 else "") for t in tasks]

        fig3 = go.Figure()
        fig3.add_trace(go.Scatter(
            x=urgency_scores, y=impact_scores,
            mode="markers+text",
            text=titles,
            textposition="top center",
            marker=dict(
                size=12, color=impact_scores,
                colorscale="Viridis", showscale=True,
                colorbar=dict(title="Impact")
            )
        ))
        fig3.update_layout(
            title="Task Priority Matrix (Urgency vs Impact)",
            xaxis_title="Urgency", yaxis_title="Impact",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#c0c0ff",
            margin=dict(t=40, b=40, l=40, r=40)
        )
        st.plotly_chart(fig3, use_container_width=True)


# ══════════════════════════════════════════════════════════
# WEEKLY REVIEW
# ══════════════════════════════════════════════════════════
elif page == "📊 Weekly Review":
    st.title("📊 Weekly Review")
    if st.button("🔄 Generate This Week's Review", use_container_width=True):
        with st.spinner("Analyzing your week..."):
            result = api_get("/ai/weekly-review")
            if result:
                c1, c2, c3 = st.columns(3)
                c1.metric("Tasks Completed", result["tasks_completed"])
                c2.metric("Completion Rate", f"{result['completion_percentage']}%")
                c3.metric("Most Active Goal", result["most_active_goal"] or "N/A")
                st.divider()
                st.markdown(f'<div class="coach-box">{result["ai_summary"]}</div>',
                            unsafe_allow_html=True)
