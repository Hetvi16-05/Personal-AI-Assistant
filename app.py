import streamlit as st
from modules.memory import add_memory, get_memory

st.set_page_config(
    page_title="Personal AI Assistant",
    page_icon="🧠"
)

st.title("🧠 Personal AI Assistant")

if "messages" not in st.session_state:
    st.session_state.messages = []

user_input = st.chat_input("Ask me anything...")

if user_input:

    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_input
        }
    )

    # --- Memory commands ---
    if user_input.lower() == "show memory":
        memory = get_memory()
        if memory:
            response = "🧠 **Here's what I remember:**\n\n" + "\n".join(f"- {m}" for m in memory)
        else:
            response = "🤔 I don't have anything in memory yet."

    elif user_input.lower() == "clear memory":
        from modules.memory import save_memory
        save_memory([])
        response = "🗑️ Memory cleared!"

    else:
        # Store every user message in persistent memory
        add_memory(user_input)
        response = f"Got it! I've remembered: *{user_input}*"

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": response
        }
    )

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
