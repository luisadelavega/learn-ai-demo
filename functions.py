import streamlit as st
import replicate
import openai


def get_bot_response(prompt: str, topic: str = "General") -> str:
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Or "gpt-4" if you have access
            messages=[
                {"role": "system", "content": f"You are a helpful assistant specialized in {topic.lower()}."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0
        )
        return response.choices[0].message["content"].strip()
    except Exception as e:
        return f"Error from OpenAI: {str(e)}"

    except Exception as e:
        return f"Error calling Replicate: {str(e)}"


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


