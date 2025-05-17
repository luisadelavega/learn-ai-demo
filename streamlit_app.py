import streamlit as st
from functions import get_bot_response, get_questions_for_topic

# --- Page Config ---
st.set_page_config(page_title="Nubo Knowledge Checker", page_icon="🧠")

# --- Session State Initialization ---
if "page" not in st.session_state:
    st.session_state.page = "User"

if "messages" not in st.session_state:
    st.session_state.messages = []

if "chat_started" not in st.session_state:
    st.session_state.chat_started = False

# --- Sidebar Navigation ---
with st.sidebar:
    st.markdown("## 🔍 Navigation")
    if st.button("👤 User"):
        st.session_state.page = "User"
        st.session_state.chat_started = False
        st.session_state.messages = []
    if st.button("📊 Manager"):
        st.session_state.page = "Manager"

# --- Page Header ---
st.title("🧠 Nubo Knowledge Checker")
st.subheader("Test your understanding and get instant feedback from Nubo.")

# --- USER TAB ---
if st.session_state.page == "User":
    # Use a selectbox to choose topic — the value is stored in session_state['topic']
    selected_topic = st.selectbox(
        "Choose a topic:", ["EU AI Act", "GDPR", "Cybersecurity", "Maatschappelijke agenda 2023-2027", "Other"], key="topic"
    )

    # Start button
    if st.button("▶️ Start"):
        st.session_state.chat_started = True
        st.session_state.messages = []

        # Ask the first question based on the selected topic
        first_question = get_questions_for_topic(selected_topic)[0]
        st.session_state.messages.append({
            "role": "assistant",
            "content": first_question
        })

    # Show chat only after Start is clicked
    if st.session_state.chat_started:
        # Display chat history
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        # Chat input
        prompt = st.chat_input("Type your message...")

        if prompt:
            # Show user's message
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            # Get assistant response
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    reply = get_bot_response(prompt)
                    #st.markdown(reply)

            # Store assistant reply
            st.session_state.messages.append({"role": "assistant", "content": reply})
    else:
        st.info("Select a topic and click 'Start' to begin the chat.")

# --- MANAGER TAB ---
elif st.session_state.page == "Manager":
    st.subheader("📊 Manager Dashboard")
    st.info("This section is under development. Check back soon!")

