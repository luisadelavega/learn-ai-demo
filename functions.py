import streamlit as st
from openai import OpenAI, OpenAIError

# --- Initialize OpenAI client ---
def get_client():
    try:
        api_key = st.secrets["openai"]["api_key"]
        return OpenAI(api_key=api_key)
    except Exception:
        st.error("OpenAI API key not found.")
        return None

# --- Evaluation Prompt Builder with Bot Behavior Rules ---
def get_evaluation_prompt(question: str, answer: str, topic: str, attempts: int) -> str:
    return f"""
You are a knowledge assessment evaluator for employee training on the topic of "{topic}".

Follow these instructions carefully:

1. Ask questions only — do not explain, summarize, or shift the topic.
2. If the user's answer is vague, incomplete, or off-topic, you can ask a follow-up question to ask it in more details.
3. Stop after 2 unclear replies and say: "Let's move on to the next question."
4. If the user asks something off-topic, respond with: "My goal is to check your knowledge. Let's complete the assessment first."
5. If this is the last question, give a short, structured evaluation with strengths and improvement points.
6. Keep your tone professional, clear, and supportive.

Current Attempt: {attempts}/3

---

Question: {question}

User Answer: {answer}

Now respond according to the rules.
""".strip()

# --- Call OpenAI to evaluate a user response ---
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
            "How does the EU AI Act classify high-risk AI systems?",
            "What responsibilities do organizations have under the EU AI Act?",
            "What kinds of AI practices are prohibited under the EU AI Act?",
            "How can companies ensure compliance with the EU AI Act during AI development?"
        ],
        "Maatschappelijke agenda 2023-2027": [
            "What is the primary goal of the Maatschappelijke agenda 2023-2027?",
            "How does this agenda influence your daily work or role?",
            "Which societal challenges are being addressed by the agenda?",
            "What actions can employees take to contribute to its objectives?",
            "Why is it important for organizations to align with this agenda?"
        ]
    }.get(topic, default)
