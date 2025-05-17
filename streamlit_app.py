import streamlit as st
from functions import get_bot_response

# Page setup
st.set_page_config(page_title="Nubo Knowledge Checker", page_icon="🧠")

# Initialize session state
if "page" not in st.session_state:
    st.session_state.page = "User"

if "messages" not in st.session_state:
    st.session_state.messages = []

if "chat_started" not in st.session_state:
    st.session_state.chat_started = False

# --- SIDEBAR NAVIGATION ---
with st.sidebar:
    st.markdown("## 🔍 Navigation")
    user_btn = st.button("👤 User")
    manager_btn = st.button("📊 Manager")

    if user_btn:
        st.session_state.page = "User"
        st.session_state.chat_started = False
        st.session_state.messages = []

    if manager_btn:
        st.session_state.page = "Manager"

# --- PAGE HEADER ---
st.title("🧠 Nubo Knowledge Checker")
st.subheader("Test your understanding and get instant feedback from Nubo.")

# --- USER TAB ---
if st.session_state.page == "User":
    topic = st.selectbox("Choose a topic:", ["General", "Support", "Technical"], key="topic")

    if st.button("▶️ Start"):
        st.session_state.chat_started = True

    if st.session_state.chat_started:
        # Show chat history
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        # Chat input
        prompt = st.chat_input("Type your message...")

        if prompt:
            # Append user message
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            # Get response from bot
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    reply = get_bot_response(prompt)
                    st.markdown(reply)

            # Append assistant message
            st.session_state.messages.append({"role": "assistant", "content": reply})
    else:
        st.info("Select a topic and click 'Start' to begin the chat.")

# --- MANAGER TAB ---
elif st.session_state.page == "Manager":
    st.subheader("📊 Manager Dashboard")
    st.info("This section is under development. Check back soon!")
