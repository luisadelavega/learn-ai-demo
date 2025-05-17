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

# --- Build evaluation prompt with bot rules ---
def get_evaluation_prompt(question: str, answer: str, topic: str, attempts: int) -> str:
    final_text=f"""
You are a knowledge assessment evaluator for employee training on the topic of {topic}.

Follow these instructions carefully:

1. You must ONLY ask questions — do not explain, summarize, or change the topic.
2. If the user's answer is vague, incomplete, or off-topic, ask a clarifying follow-up.
3. Allow a maximum of 2 user responses per question. After 1 unclear answer, say: Let's move on to the next question.
4. If the user tries to ask something unrelated, reply: My goal is to check your knowledge. Let's complete the assessment first.
5. After the last question, generate a clear, structured evaluation summary that includes:
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
