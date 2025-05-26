import streamlit as st
import openai
import os
import gspread
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# --- Initialize OpenAI client ---
def get_client():
    try:
        openai.api_key = st.secrets["openai"]["api_key"]
        return openai
    except Exception:
        st.error("OpenAI API key not found.")
        return None

def save_assessment_to_topic_file(qa_pairs: list, summary: str, topic: str):
    # Create a safe filename from topic
    filename = topic.lower().replace(" ", "_") + "_chats.txt"

    log_entry = f"\n\n=== New Assessment on {topic} ===\n"
    for q, a in qa_pairs:
        log_entry += f"Q: {q}\nA: {a}\n"
    log_entry += f"\nSummary:\n{summary}\n"
    log_entry += f"{'=' * 40}\n"

    with open(filename, "a", encoding="utf-8") as file:
        file.write(log_entry)


def save_chat_to_gsheet(topic: str, chat_text: str):
    # Connect using the Streamlit GSheets connector
    #conn = st.connection("gsheets", type="gspread")

    # Create a connection object.
    conn = st.connection("gsheets", type=GSheetsConnection)


    df = conn.read()

    # Print results.
    for row in df.itertuples():
        st.write(f"{row.topic} has a :{row.chat}:")

    # worksheet = conn.open("Answers_pilot").sheet1

    # worksheet.append_row([topic, chat_text])


    # Write updated DataFrame back to Google Sheets
    #conn.update(worksheet="Sheet1", data=df)

    # Read existing data (as list of dicts)
    data = conn.read(worksheet="Sheet1")

    if df is None or df.empty:
        df = pd.DataFrame(columns=["topic", "chat"])

    # Add the new row
    df.loc[len(df)] = [topic, chat_text]

    # Update the sheet
    conn.update(worksheet="Sheet1", data=df)



def generate_manager_summary(topic: str, combined_chats: str, model: str = "gpt-4o") -> str:
    client = get_client()
    if not client:
        return "Error: No OpenAI client."

    prompt = f"""
You are a team performance evaluator.

Summarize the following collected team responses on the topic of {topic}.

Provide:
✅ General strengths of the team  
⚠️ Common areas to improve  
💡 Team-level suggestions  
⭐ Overall team rating (Needs Improvement / Good / Excellent)

Do **not** refer to individual users.

---

Collected Responses:
{combined_chats}
""".strip()

    try:
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a team assessment summarizer."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        return f"Error generating manager summary: {e}"




# --- Build evaluation prompt with bot rules ---
def get_evaluation_prompt(question: str, answer: str, topic: str, attempts: int) -> str:
    final_text = f"""
You are a knowledge assessment evaluator for employee training on the topic of {topic}.

Follow these instructions carefully:

1. You must ONLY ask questions — do not explain, summarize, or change the topic. 
2. If the user's answer is vague, incomplete, or off-topic, ask a clarifying follow-up. 
3. Ask only ONE follow-up question per question. If the answer is still unclear, move to the next question.
4. If the user tries to ask something unrelated, reply: My goal is to check your knowledge. Let's complete the assessment first.

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

# --- Return 3 questions per topic ---
def get_questions_for_topic(topic: str) -> list:
    if topic == "Other":
        return ["What topic do you want to evaluate your knowledge of?"]

    default = [
        f"What is an important concept in {topic} every employee should understand?",
        f"How would you react to a challenge related to {topic} at work?",
        f"What could help prevent mistakes in {topic}?"
    ]

    return {
        "GDPR": [
            "What is the main purpose of the GDPR regulation?",
            "How should a company respond if a customer requests deletion of their personal data?",
            "What is considered a personal data breach under GDPR?"
        ],
        "Cybersecurity": [
            "Imagine you discover a data breach in our system. What are the first steps you’d take?",
            "What are the most common causes of cybersecurity incidents?",
            "What steps should be taken to prevent phishing attacks?"
        ],
        "EU AI Act": [
            "What is the main objective of the EU AI Act?",
            "How does the EU AI Act classify high-risk AI systems?",
            "What responsibilities do organizations have under the EU AI Act?"
        ],
        "Maatschappelijke agenda 2023-2027": [
            "What is the primary goal of the Maatschappelijke agenda 2023-2027?",
            "Which societal challenges are being addressed by the agenda?",
            "What actions can employees take to contribute to its objectives?"
        ]
    }.get(topic, default)

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
            temperature=0.5,
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        return f"Error generating final summary: {e}"
