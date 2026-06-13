import streamlit as st

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

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": f"You said: {user_input}"
        }
    )

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
