import streamlit as st
import openai
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from functions_rag import (
    extract_pdf_chunks,
    embed_chunks,
    create_faiss_index,
    retrieve_relevant_chunks,
    rag_from_pdf,
)

# --- Initialize OpenAI client ---
def get_client():
    try:
        openai.api_key = st.secrets["openai"]["api_key"]
        return openai
    except Exception:
        st.error("OpenAI API key not found.")
        return None

# --- Build evaluation prompt with bot rules ---
def get_evaluation_prompt(question: str, answer: str, topic: str, attempts: int) -> str:
    text_top_chunks=" "
    if topic=="Maatschappelijke agenda 2023-2027":
        pdf_path = "dutch_policy.pdf"
        top_chunks = rag_from_pdf(pdf_path, question, k=3)
        text_top_chunks=f"Assess the user answer and/or elaborate the follow-up question (if needed) based on this information: {top_chunks}"
    else:
        text_top_chunks=" "
    final_text = f"""
You are a knowledge assessment evaluator for employee training on the topic of {topic}.

Follow these instructions carefully:

1. You must ONLY ask questions — do not explain, summarize, or change the topic. 
2. If the user's answer is vague, incomplete, or off-topic, ask a clarifying follow-up. Provide some context on the follow-up question. Refer to the previous answer provided by the user.
3. Ask only ONE follow-up question per question. If the answer is still unclear, move to the next question.
4. If the user tries to ask something unrelated, reply: My goal is to check your knowledge. Let's complete the assessment first.
5. If the answer is satisfactory, the follow-up question is not needed.
6. Be nice and add complements to the follow-up question whenever suitable.
{text_top_chunks}

Stay professional and constructive in your tone.

Current Attempt: {attempts}/2

---

Question: {question}

User Answer: {answer}

Now respond according to the rules above."""
    return final_text.strip()

# --- Evaluate response using OpenAI ---
def evaluate_user_response(question: str, answer: str, topic: str, attempts: int, model: str = "gpt-4o") -> str:
    client = get_client()
    if not client:
        return "Error: No OpenAI client."

    prompt = get_evaluation_prompt(question, answer, topic, attempts)

    try:
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a knowledge assessment evaluator."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        return f"Error evaluating response: {e}"

# --- Final overall evaluation after all Q&A ---
def evaluate_all_responses(qa_pairs: list, topic: str, model: str = "gpt-4o") -> str:
    client = get_client()
    if not client:
        return "Error: No OpenAI client."

    formatted = "\n\n".join([f"Q: {q}\nA: {a}" for q, a in qa_pairs])
    prompt = f"""
You are a knowledge assessment evaluator for employee training on the topic of {topic}.

Here is a complete set of questions and user answers:

{formatted}

Now provide a structured final evaluation that includes:
✅ Strengths  
⚠️ Areas to Improve  
💡 Suggestions  
⭐ Overall Rating (Needs Improvement / Good / Excellent)

Be concise, professional, and helpful.
""".strip()

    try:
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a final assessment evaluator."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        return f"Error generating final summary: {e}"

# --- Generate manager-level team summary ---
def generate_manager_summary(topic: str, combined_chats: str, model: str = "gpt-4o") -> str:
    client = get_client()
    if not client:
        return "Error: No OpenAI client."

    prompt = f"""
You are a team performance evaluator.

Summarize the following collected responses on the topic of {topic}.

Provide:
✅ General strengths shown across the team  
⚠️ Common areas the team needs to improve  
💡 Suggestions for team-wide development  
⭐ Overall team rating (Needs Improvement / Good / Excellent)

Do **not** mention individual users, runs, or past sessions. Focus on team-level insights.

---

Collected Team Responses:
{combined_chats}
""".strip()

    try:
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a team assessment summarizer."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        return f"Error generating manager summary: {e}"

# --- Save chat to Google Sheets ---
def save_chat_to_gsheet(topic: str, chat_text: str):
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df = conn.read(worksheet="Sheet1", ttl=0)

        if df is None or df.empty:
            # Create new dataframe if sheet is empty
            updated_df = pd.DataFrame([{"topic": topic, "chat": chat_text}])
        else:
            # Append new row using concat
            new_row = pd.DataFrame([{"topic": topic, "chat": chat_text}])
            updated_df = pd.concat([df, new_row], ignore_index=True)

        # Write back to sheet
        conn.update(worksheet="Sheet1", data=updated_df)
        #st.success("Chat saved to Google Sheets!")

    except Exception as e:
        st.error(f"Error saving to Google Sheets: {e}")

# --- Return 3 questions per topic ---
def get_questions_for_topic(topic: str) -> list:
    if topic == "Other":
        return ["What topic do you want to evaluate your knowledge of?"]

    default=[
        f"Imagine you're onboarding a new colleague. How would you explain why {topic} matters in their daily work?",
        f"You face a challenge involving {topic}. What's your first step to deal with it confidently?",
        f"What is one habit or checklist that could help your team avoid mistakes related to {topic}?",
        f"When has {topic} positively impacted your work — even if indirectly?",
        f"What tools or support would make you feel more confident handling situations involving {topic}?"]

    return {

    "GDPR": [
        "A customer requests deletion of all their personal data. What steps would you take — and how do you ensure it's done legally?",
        "You're preparing a presentation with real customer examples. How do you make sure you're GDPR-compliant?",
        "What’s a practical way to double-check you're not sharing personal data by mistake in everyday emails or files?",
        "Your colleague wants to store employee birthdays in a shared file. How would you handle this under GDPR?",
        "What's one habit you could adopt to help prevent personal data breaches in your work?"
    ],
    "Cybersecurity": [
        "You receive a slightly suspicious email from a colleague asking for a file. What signs would help you decide if it’s safe?",
        "You're working in a co-working space. What can you do to protect your screen and data?",
        "What’s a small step your team could take this week to boost cybersecurity awareness?",
        "You accidentally clicked on a suspicious link. What should you do immediately — and who should you inform?",
        "What’s one tool or feature (e.g., VPN, password manager) that you think more people in your team should be using?"
    ],
    "EU AI Act": [
        "Your team wants to use AI to screen job applications. What would you check to ensure compliance with the EU AI Act?",
        "How would you explain to a colleague why AI transparency and accountability matter under the new regulation?",
        "What practical steps can an organization take to identify if an AI tool falls into the 'high-risk' category?",
        "You’re reviewing an AI tool for use in a safety-critical area. What red flags would you look for?",
        "What kind of documentation or testing would help you trust an AI system more in your work?"
    ],
    "Maatschappelijke agenda 2023-2027": [
        "Your project may influence one of the goals in the Maatschappelijke agenda. How can you align your work with it?",
        "What is one concrete action employees can take to support the social themes in the agenda?",
        "If your team had to pick one societal challenge to address this year, which one would it be — and why?",
        "How do you think the agenda’s goals could change how we prioritize our projects in the future?",
        "What kind of collaboration across teams would help advance the objectives of the agenda?"]}.get(topic, default)

