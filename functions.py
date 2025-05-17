import streamlit as st
import replicate
import openai
from openai import OpenAI

def get_bot_response(prompt: str, model: str = "gpt-4o-mini") -> str:


    try:
        api_key = st.secrets["openai"]["api_key"]
    except Exception:
        return "Error: OpenAI API key not found in Streamlit secrets."

    client = OpenAI(api_key=api_key)

    models = client.models.list()
    st.write([m.id for m in models.data])

    try:
        output_container = st.empty()
        final_response = ""

        stream = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.6,
            top_p=0.9,
            presence_penalty=1.15,
            frequency_penalty=0.2,
            stream=True
        )

        for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                token = chunk.choices[0].delta.content
                final_response += token
                output_container.markdown(final_response)

        return final_response

    except Exception as e:
        return f"Error calling OpenAI API: {str(e)}"


def get_evaluation_prompt(question: str, answer: str, topic: str) -> str:
    return f"""
You are an expert in training employees on the topic of {topic}.

Your task is to evaluate a single answer to an open-ended question. Use the following structure:

Question:
{question}

User Answer:
{answer}

Your evaluation must include:
✅ Strengths: What is correct or well thought-out.  
⚠️ Weaknesses: What is missing, incorrect, or potentially risky.  
💡 Suggestions: 1–2 practical tips for improvement.  
⭐ Rating: One of the following - Needs Improvement / Good / Excellent

Keep your tone constructive and professional.

Respond in this format:
Strengths:
- ...
Weaknesses:
- ...
Suggestions:
- ...
Rating: ...
""".strip()


def evaluate_user_response(question: str, answer: str, topic: str) -> str:
    prompt = get_evaluation_prompt(question, answer, topic)
    return get_bot_response(prompt)


def get_questions_for_topic(topic: str) -> list:
    default = [
        f"What is an important concept in {topic} every employee should understand?",
        f"How would you react to a challenge related to {topic} at work?",
        f"What could help prevent mistakes in {topic}?",
        f"How would you explain {topic}'s importance to a new colleague?",
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
        ]
    }.get(topic, default)


