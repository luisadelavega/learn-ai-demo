import streamlit as st
from functions import get_questions_for_topic, evaluate_user_response

# --- Page Config ---
st.set_page_config(page_title="Nubo Knowledge Checker", page_icon="🧠")

# --- Session State Initialization ---
st.session_state.setdefault("page", "User")
st.session_state.setdefault("chat_started", False)
st.session_state.setdefault("messages", [])
st.session_state.setdefault("question_index", 0)
st.session_state.setdefault("final_topic", "")
st.session_state.setdefault("questions", [])

# --- Sidebar Navigation ---
with st.sidebar:
    st.markdown("## 🔍 Navigation")
    if st.button("👤 User"):
        st.session_state.page = "User"
        st.session_state.chat_started = False
        st.session_state.messages = []
        st.session_state.question_index = 0
        st.session_state.questions = []
    if st.button("📊 Manager"):
        st.session_state.page = "Manager"

# --- Page Header ---
st.title("🧠 Nubo Knowledge Checker")
st.write("Test your understanding and get instant feedback from Nubo.")

# --- USER TAB LOGIC ---
if st.session_state.page == "User":
    selected_topic = st.selectbox(
        "Choose a topic:",
        ["EU AI Act", "GDPR", "Cybersecurity", "Maatschappelijke agenda 2023-2027", "Other"],
        key="topic"
    )

    if selected_topic == "Other":
        custom_topic = st.text_input("What topic do you want to evaluate your knowledge of?", key="custom_topic")
        final_topic = custom_topic.strip() if custom_topic else "Other"
    else:
        final_topic = selected_topic

    if st.button("▶️ Start"):
        st.session_state.chat_started = True
        st.session_state.messages = []
        st.session_state.question_index = 0
        st.session_state.final_topic = final_topic
        st.session_state.questions = get_questions_for_topic(final_topic)

        first_question = st.session_state.questions[0]
        st.session_state.messages.append({"role": "assistant", "content": first_question})

    # Show question and response history
    if st.session_state.chat_started:
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        # Allow user to answer current question
        if st.session_state.question_index < len(st.session_state.questions):
            prompt = st.chat_input("Your answer...")

            if prompt:
                st.session_state.messages.append({"role": "user", "content": prompt})
                with st.chat_message("user"):
                    st.markdown(prompt)

                question = st.session_state.questions[st.session_state.question_index]

                # Get bot's reply
                bot_reply = evaluate_user_response(
                    question=question,
                    answer=prompt,
                    topic=st.session_state.final_topic,
                    attempts=1  # static since we don’t track attempts here
                )

                st.session_state.messages.append({"role": "assistant", "content": bot_reply})
                with st.chat_message("assistant"):
                    st.markdown(bot_reply)

                # # Move to next question
                # st.session_state.question_index += 1

                # if st.session_state.question_index < len(st.session_state.questions):
                #     next_q = st.session_state.questions[st.session_state.question_index]
                #     st.session_state.messages.append({"role": "assistant", "content": next_q})

# --- MANAGER TAB ---
elif st.session_state.page == "Manager":
    st.subheader("📊 Manager Dashboard")
    st.info("This section is under development. Check back soon!")

