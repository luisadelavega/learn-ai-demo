import streamlit as st
from functions import get_questions_for_topic, evaluate_user_response, evaluate_all_responses

# --- Page Config ---
st.set_page_config(page_title="Nubo Knowledge Checker", page_icon="🧠")

# --- Session State Initialization ---
st.session_state.setdefault("page", "User")
st.session_state.setdefault("chat_started", False)
st.session_state.setdefault("messages", [])
st.session_state.setdefault("question_index", 0)
st.session_state.setdefault("attempt_count", 0)
st.session_state.setdefault("qa_pairs", [])
st.session_state.setdefault("final_topic", "")
st.session_state.setdefault("questions", [])
st.session_state.setdefault("final_summary_displayed", False)
st.session_state.setdefault("waiting_for_input", True)
st.session_state.setdefault("manager_summary", "")
st.session_state.setdefault("new_evaluation_available", False)

# --- Sidebar Navigation ---
with st.sidebar:
    st.markdown("## 🔍 Navigation")

    # --- User tab ---
    if st.button("👤 User"):
        st.session_state.page = "User"
        st.session_state.chat_started = False
        st.session_state.messages = []
        st.session_state.question_index = 0
        st.session_state.attempt_count = 0
        st.session_state.qa_pairs = []
        st.session_state.questions = []
        st.session_state.final_summary_displayed = False
        st.session_state.waiting_for_input = True

    # --- Manager tab with red alert ---
    if st.session_state.new_evaluation_available:
        manager_clicked = st.sidebar.markdown(
            f"<a href='/?page=Manager' style='color: red; font-weight: bold;'>📊 Manager (New)</a>",
            unsafe_allow_html=True
        )
        st.session_state.page = "Manager"
        st.session_state.new_evaluation_available = False
    else:
        if st.button("📊 Manager"):
            st.session_state.page = "Manager"

# --- Page Header ---
st.title("🧠 Nubo Knowledge Checker")
st.write("Test your understanding and get instant feedback from Nubo.")

# --- USER TAB LOGIC ---
if st.session_state.page == "User":
    selected_topic = st.selectbox(
        "Choose a topic:",
        ["EU AI Act", "GDPR", "Cybersecurity", "Other"],
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
        st.session_state.attempt_count = 0
        st.session_state.qa_pairs = []
        st.session_state.final_topic = final_topic
        st.session_state.questions = get_questions_for_topic(final_topic)
        st.session_state.final_summary_displayed = False
        st.session_state.waiting_for_input = True

        first_question = st.session_state.questions[0]
        st.session_state.messages.append({"role": "assistant", "content": first_question})

    # Show chat messages
    if st.session_state.chat_started:
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        if (
            st.session_state.question_index < len(st.session_state.questions)
            and st.session_state.waiting_for_input
        ):
            prompt = st.chat_input("Your answer...")

            if prompt:
                st.session_state.waiting_for_input = False
                st.session_state.messages.append({"role": "user", "content": prompt})
                with st.chat_message("user"):
                    st.markdown(prompt)

                current_q = st.session_state.questions[st.session_state.question_index]
                st.session_state.attempt_count += 1

                response = evaluate_user_response(
                    question=current_q,
                    answer=prompt,
                    topic=st.session_state.final_topic,
                    attempts=st.session_state.attempt_count
                )

                if st.session_state.attempt_count == 1:
                    # First response → show follow-up
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    with st.chat_message("assistant"):
                        st.markdown(response)
                    st.session_state.waiting_for_input = True

                else:
                    # Second response → move on
                    st.session_state.qa_pairs.append((current_q, prompt))
                    st.session_state.question_index += 1
                    st.session_state.attempt_count = 0
                    st.session_state.waiting_for_input = True

                    if st.session_state.question_index < len(st.session_state.questions):
                        next_q = st.session_state.questions[st.session_state.question_index]

                        # Transition message
                        transition_msg = "Thanks for your answer. Moving on to the next question..."
                        st.session_state.messages.append({"role": "assistant", "content": transition_msg})
                        with st.chat_message("assistant"):
                            st.markdown(transition_msg)

                        # Next question
                        st.session_state.messages.append({"role": "assistant", "content": next_q})
                        with st.chat_message("assistant"):
                            st.markdown(next_q)
                    else:
                        # All questions done → generate summary
                        with st.spinner("Generating your overall evaluation..."):
                            summary = evaluate_all_responses(
                                st.session_state.qa_pairs,
                                st.session_state.final_topic
                            )
                            st.session_state.messages.append({"role": "assistant", "content": summary})
                            st.session_state.final_summary_displayed = True

                            # Manager summary + red alert
                            st.session_state.manager_summary = f"### 📋 Team Assessment Summary for {st.session_state.final_topic}\n\n{summary}"
                            st.session_state.new_evaluation_available = True

                            with st.chat_message("assistant"):
                                st.markdown(summary)

# --- MANAGER TAB ---
elif st.session_state.page == "Manager":
    st.subheader("📊 Manager Dashboard")
    if st.session_state.manager_summary:
        st.markdown(st.session_state.manager_summary)
    else:
        st.info("No evaluations available yet. Ask a team member to complete the assessment.")
