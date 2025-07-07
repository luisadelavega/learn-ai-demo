import streamlit as st
from functions import (
    get_questions_for_topic,
    evaluate_user_response,
    evaluate_all_responses,
    save_chat_to_gsheet,
    generate_manager_summary,
)
import random
from streamlit_gsheets import GSheetsConnection

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

transition_messages = [
    "Thanks for your reply. I was also wondering...",
    "Thanks for your reply. That makes me curious about...",
    "Interesting! It also makes me think about...",
    "Thanks for sharing that. I’m curious how you see...",
    "I appreciate your input. What’s your take on...",
    "Thanks for your answer. It makes me wonder...",
    "Hmm, that’s helpful. What about...",
    "Great, thank you! I’m also interested in...",
    "That’s a good point. How would you approach...",
    "Thanks for your thoughts! I’m thinking about...",
    "Appreciate that! Let’s explore this further...",
]

# --- Sidebar Navigation ---
with st.sidebar:
    st.markdown("## 🔍 Navigation")

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

    if st.session_state.new_evaluation_available:
        st.sidebar.markdown(
            f"<span style='color: red; font-weight: bold;'>📊 Manager (New)</span>",
            unsafe_allow_html=True
        )
    if st.button("📊 Manager"):
        st.session_state.page = "Manager"
        st.session_state.new_evaluation_available = False

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
        st.session_state.attempt_count = 0
        st.session_state.qa_pairs = []
        st.session_state.final_topic = final_topic
        st.session_state.questions = get_questions_for_topic(final_topic)
        st.session_state.final_summary_displayed = False
        st.session_state.waiting_for_input = True

        first_question = st.session_state.questions[0]
        st.session_state.messages.append({"role": "assistant", "content": first_question})

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
                    # First response → save and ask follow-up
                    st.session_state.qa_pairs.append((current_q, prompt))
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    with st.chat_message("assistant"):
                        st.markdown(response)
                    st.session_state.waiting_for_input = True

                else:
                    # Second response → save follow-up, move to next
                    st.session_state.qa_pairs.append((f"Follow-up on: {current_q}", prompt))
                    st.session_state.question_index += 1
                    st.session_state.attempt_count = 0
                    st.session_state.waiting_for_input = True

                    if st.session_state.question_index < len(st.session_state.questions):
                        next_q = st.session_state.questions[st.session_state.question_index]
                        transition_msg = random.choice(transition_messages)

                        st.session_state.messages.append({"role": "assistant", "content": transition_msg})
                        with st.chat_message("assistant"):
                            st.markdown(transition_msg)

                        st.session_state.messages.append({"role": "assistant", "content": next_q})
                        with st.chat_message("assistant"):
                            st.markdown(next_q)
                    else:
                        # All questions done → generate summary
                        if not st.session_state.final_summary_displayed:
                            with st.spinner("Generating your overall evaluation..."):
                                summary = evaluate_all_responses(
                                    st.session_state.qa_pairs,
                                    st.session_state.final_topic
                                )
                                st.session_state.messages.append({"role": "assistant", "content": summary})
                                st.session_state.final_summary_displayed = True

                                # Save only current session's chat
                                chat_history = "\n".join(
                                    f"Q: {q} A: {a}" for q, a in st.session_state.qa_pairs
                                )
                                save_chat_to_gsheet(
                                    topic=st.session_state.final_topic,
                                    chat_text=chat_history
                                )

                                st.session_state.new_evaluation_available = True

                                with st.chat_message("assistant"):
                                    st.markdown(summary)

# --- MANAGER TAB ---
elif st.session_state.page == "Manager":
    st.subheader("📊 Manager Dashboard")

    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(worksheet="Sheet1", ttl=0)

    if df is None or df.empty:
        st.info("No evaluation data available yet.")
    else:
        topics = df["topic"].unique().tolist()
        selected_topic = st.selectbox("Select a topic:", topics)

        if st.button("Run Evaluation Summary"):
            topic_chats = df[df["topic"] == selected_topic]["chat"].tolist()
            combined_text = "\n\n".join(topic_chats)

            summary = generate_manager_summary(selected_topic, combined_text)

            st.markdown(f"### 📋 Team Summary for {selected_topic}")
            st.markdown(summary)
