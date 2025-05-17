import streamlit as st
from functions import get_questions_for_topic, evaluate_user_response

# --- Page Config ---
st.set_page_config(page_title="Nubo Knowledge Checker", page_icon="🧠")

# --- Session State Initialization ---
st.session_state.setdefault("page", "User")
st.session_state.setdefault("chat_started", False)
st.session_state.setdefault("messages", [])
st.session_state.setdefault("question_index", 0)
st.session_state.setdefault("interaction_count", 0)
st.session_state.setdefault("answers", [])
st.session_state.setdefault("questions", [])
st.session_state.setdefault("final_topic", "")

# --- Sidebar Navigation ---
with st.sidebar:
    st.markdown("## 🔍 Navigation")
    if st.button("👤 User"):
        st.session_state.page = "User"
        st.session_state.chat_started = False
        st.session_state.messages = []
        st.session_state.question_index = 0
        st.session_state.interaction_count = 0
        st.session_state.answers = []
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
        st.session_state.interaction_count = 0
        st.session_state.answers = []
        st.session_state.final_topic = final_topic
        st.session_state.questions = get_questions_for_topic(final_topic)

        first_question = st.session_state.questions[0]
        st.session_state.messages.append({"role": "assistant", "content": first_question})

    # Show chat history
    if st.session_state.chat_started:
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        # ✅ Show chat_input ONLY if there are questions left
        if st.session_state.question_index < len(st.session_state.questions):
            prompt = st.chat_input("Your answer...")

            if prompt:
                st.session_state.messages.append({"role": "user", "content": prompt})
                with st.chat_message("user"):
                    st.markdown(prompt)

                question = st.session_state.questions[st.session_state.question_index]
                st.session_state.interaction_count += 1

                # Evaluate the response via LLM
                eval_result = evaluate_user_response(
                    question=question,
                    answer=prompt,
                    topic=st.session_state.final_topic,
                    attempts=st.session_state.interaction_count
                )

                # Display and store assistant's response
                st.session_state.messages.append({"role": "assistant", "content": eval_result})
                with st.chat_message("assistant"):
                    st.markdown(eval_result)

                # Check if it's time to move on
                if (
                    st.session_state.interaction_count >= 2  # matches max attempts in prompt
                    or "Let's move on to the next question" in eval_result
                    or "Generating your summary" in eval_result
                ):
                    st.session_state.answers.append({
                        "question": question,
                        "answer": prompt,
                        "evaluation": eval_result
                    })
                    st.session_state.question_index += 1
                    st.session_state.interaction_count = 0

                    if st.session_state.question_index < len(st.session_state.questions):
                        next_q = st.session_state.questions[st.session_state.question_index]
                        st.session_state.messages.append({"role": "assistant", "content": next_q})
                        with st.chat_message("assistant"):
                            st.markdown(next_q)

# --- MANAGER TAB ---
elif st.session_state.page == "Manager":
    st.subheader("📊 Manager Dashboard")
    st.info("This section is under development. Check back soon!")
