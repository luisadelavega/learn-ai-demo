import streamlit as st
from functions import get_bot_response, get_questions_for_topic, evaluate_user_response

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
    topic = st.selectbox(
        "Choose a topic:",
        ["EU AI Act", "GDPR", "Cybersecurity", "Maatschappelijke agenda 2023-2027", "Other"],
        key="topic"
    )

    # If topic is "Other", ask user to enter it
    if topic == "Other":
        custom_topic = st.text_input("What topic do you want to evaluate your knowledge of?", key="custom_topic")
        topic = custom_topic or "Other"

    if st.button("▶️ Start"):
        st.session_state.chat_started = True
        st.session_state.messages = []
        st.session_state.question_index = 0
        st.session_state.interaction_count = 0
        st.session_state.answers = []
        st.session_state.questions = get_questions_for_topic(topic)

        first_question = st.session_state.questions[0]
        st.session_state.messages.append({"role": "assistant", "content": first_question})

    # Show chat interface
    if st.session_state.chat_started:
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        prompt = st.chat_input("Your answer...")

        if prompt:
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            question = st.session_state.questions[st.session_state.question_index]

            # Rule 3: Off-topic check
            if any(x in prompt.lower() for x in ["what is", "explain", "can you", "how do", "?", "who", "when", "why"]) and "i think" not in prompt.lower():
                bot_reply = "My goal is to check your knowledge. Let's complete the assessment first."
            else:
                st.session_state.interaction_count += 1

                eval_result = evaluate_user_response(question, prompt, topic)

                if "Rating: Excellent" in eval_result or "Rating: Good" in eval_result:
                    st.session_state.answers.append({
                        "question": question,
                        "answer": prompt,
                        "evaluation": eval_result
                    })
                    st.session_state.question_index += 1
                    st.session_state.interaction_count = 0

                    if st.session_state.question_index < len(st.session_state.questions):
                        bot_reply = st.session_state.questions[st.session_state.question_index]
                    else:
                        bot_reply = "✅ Thank you for completing the assessment. Generating your summary..."
                elif st.session_state.interaction_count >= 3:
                    st.session_state.answers.append({
                        "question": question,
                        "answer": prompt,
                        "evaluation": "No clear answer after 3 attempts."
                    })
                    st.session_state.question_index += 1
                    st.session_state.interaction_count = 0

                    if st.session_state.question_index < len(st.session_state.questions):
                        bot_reply = st.session_state.questions[st.session_state.question_index]
                    else:
                        bot_reply = "✅ Thank you for completing the assessment. Generating your summary..."
                else:
                    bot_reply = "Could you clarify or elaborate a bit more on your answer?"

            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    st.markdown(bot_reply)

            st.session_state.messages.append({"role": "assistant", "content": bot_reply})

            # Final summary
            if st.session_state.question_index >= len(st.session_state.questions):
                with st.spinner("Generating summary..."):
                    strengths = []
                    improvements = []

                    for entry in st.session_state.answers:
                        eval_text = entry["evaluation"]
                        if "Strengths:" in eval_text:
                            strengths.append(eval_text.split("Strengths:")[1].split("Weaknesses:")[0].strip())
                        if "Weaknesses:" in eval_text:
                            improvements.append(eval_text.split("Weaknesses:")[1].split("Suggestions:")[0].strip())

                    summary = "### ✅ Knowledge Assessment Summary\n\n"
                    if strengths:
                        summary += "**Strengths:**\n- " + "\n- ".join(strengths) + "\n\n"
                    if improvements:
                        summary += "**Points to Improve:**\n- " + "\n- ".join(improvements)

                    st.markdown(summary)

# --- MANAGER TAB ---
elif st.session_state.page == "Manager":
    st.subheader("📊 Manager Dashboard")
    st.info("This section is under development. Check back soon!")
