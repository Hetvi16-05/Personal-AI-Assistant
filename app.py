import streamlit as st
from modules.memory import add_memory, get_memory, save_memory
from modules.profile import update_profile, get_profile_summary

st.set_page_config(
    page_title="Personal AI Assistant",
    page_icon="🧠"
)

st.title("🧠 Personal AI Assistant")

# Sidebar — live profile view
with st.sidebar:
    st.header("👤 Your Profile")
    summary = get_profile_summary()
    if summary:
        st.markdown(summary)
    else:
        st.caption("No profile info yet. Tell me about yourself!")

    st.divider()
    st.header("💬 Commands")
    st.markdown("""
- `show memory` — list all memories
- `clear memory` — wipe memory
- `who am i` — show your profile
""")

if "messages" not in st.session_state:
    st.session_state.messages = []

user_input = st.chat_input("Ask me anything...")

if user_input:

    st.session_state.messages.append({"role": "user", "content": user_input})

    text = user_input.strip()
    lower = text.lower()

    # ── Memory commands ─────────────────────────────
    if lower == "show memory":
        memory = get_memory()
        response = (
            "🧠 **Here's what I remember:**\n\n" + "\n".join(f"- {m}" for m in memory)
            if memory else "🤔 I don't have anything in memory yet."
        )

    elif lower == "clear memory":
        save_memory([])
        response = "🗑️ Memory cleared!"

    # ── Profile commands ─────────────────────────────
    elif lower in ("who am i", "what do you know about me", "show profile"):
        summary = get_profile_summary()
        response = (
            "📋 **Here's what I know about you:**\n\n" + summary
            if summary else "🤷 I don't know much about you yet. Tell me your name, goal, or interests!"
        )

    # ── Profile detection: name ──────────────────────
    elif lower.startswith("my name is "):
        name = text[len("my name is "):].strip().rstrip(".")
        update_profile("name", name)
        add_memory(text)
        response = f"Nice to meet you, **{name}**! 👋 I'll remember that."

    elif lower.startswith("i am ") and not any(
        kw in lower for kw in ["preparing", "studying", "working", "learning"]
    ):
        name = text[len("i am "):].strip().rstrip(".")
        update_profile("name", name)
        add_memory(text)
        response = f"Got it! I'll call you **{name}**. 😊"

    # ── Profile detection: goal ──────────────────────
    elif any(lower.startswith(p) for p in ["my goal is ", "i want to ", "i aim to "]):
        goal = text.split(" ", 3)[-1].strip().rstrip(".")
        update_profile("goal", goal)
        add_memory(text)
        response = f"Great goal! 🎯 I've saved: *{goal}*. I'll help you get there!"

    elif "crack gate" in lower or "gate da" in lower or "gate exam" in lower:
        update_profile("goal", "Crack GATE DA")
        add_memory(text)
        response = "🎓 GATE DA — noted! That's a strong goal. Let's work towards it together."

    # ── Profile detection: interests ────────────────
    elif any(lower.startswith(p) for p in ["i like ", "i love ", "i enjoy ", "i am interested in "]):
        for prefix in ["i am interested in ", "i like ", "i love ", "i enjoy "]:
            if lower.startswith(prefix):
                interest = text[len(prefix):].strip().rstrip(".")
                break
        update_profile("interests", interest)
        add_memory(text)
        response = f"Cool! I've noted your interest in **{interest}**. 💡"

    # ── Profile detection: study topics ─────────────
    elif any(p in lower for p in ["studying ", "learning ", "preparing for "]):
        topic = text.split(" ", 1)[-1].strip().rstrip(".")
        update_profile("study_topics", topic)
        add_memory(text)
        response = f"📚 Got it — you're studying **{topic}**. I'll keep that in mind!"

    # ── Default: store to memory ─────────────────────
    else:
        add_memory(text)
        response = f"Got it! I've remembered: *{text}* 🧠"

    st.session_state.messages.append({"role": "assistant", "content": response})

# ── Display chat history ─────────────────────────────
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
