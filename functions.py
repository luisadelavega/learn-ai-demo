import streamlit as st
import openai

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
    final_text = f"""
You are a knowledge assessment evaluator for employee training on the topic of {topic}.

Follow these instructions carefully:

1. You must ONLY ask questions — do not explain, summarize, or change the topic.
2. If the user's answer is vague, incomplete, or off-topic, ask a clarifying follow-up.
3. Allow a maximum of 2 user responses per question. After 1 unclear answer, say: Let's move on to the next question.
4. If the user tries to ask something unrelated, reply: My goal is to check your knowledge. Let's complete the assessment first.
5. After the 3 question, generate a clear, structured evaluation summary that includes:
   - ✅ Strengths
   - ⚠️ Areas to improve
   - 💡 Suggestions
   - ⭐ Overall rating (Needs Improvement / Good / Excellent)

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

# --- Return 5 questions per topic ---
def get_questions_for_topic(topic: str) -> list:
    if topic == "Other":
        return ["What topic do you want to evaluate your knowledge of?"]

    default = [
        f"What is an important concept in {topic} every employee should understand?",
        f"How would you react to a challenge related to {topic} at work?",
        f"What could help prevent mistakes in {topic}?",
        f"How would you explain the importance of {topic} to a new colleague?",
        f"What’s the first thing to do when facing a problem in {topic}?"
    ]

    return {
        "GDPR": [
            "What is the main purpose of the GDPR regulation?",
            "How should a company respond if a customer requests deletion of their personal data?",
            "What does 'lawful basis for processing' mean in the context of GDPR?",
            "How should a company handle a data subject access request (DSAR)?",
            "What is considered a personal data breach under GDPR?"
        ],
        "Cybersecurity": [
            "Imagine you discover a data breach in our system. What are the first steps you’d take?",
            "What are the most common causes of cybersecurity incidents?",
            "How would you secure sensitive information you work with daily?",
            "What steps should be taken to prevent phishing attacks?",
            "What would you do if you receive a suspicious email asking for credentials?"
        ],
        "EU AI Act": [
            "What is the main objective of the EU AI Act?",
            "How does the EU AI Act classify high-risk AI systems?"
        ],
        "Maatschappelijke agenda 2023-2027": [
            "What is the primary goal of the Maatschappelijke agenda 2023-2027?",
            "How does this agenda influence your daily work or role?",
            "Which societal challenges are being addressed by the agenda?",
            "What actions can employees take to contribute to its objectives?",
            "Why is it important for organizations to align with this agenda?"
        ]
    }.get(topic, default)
