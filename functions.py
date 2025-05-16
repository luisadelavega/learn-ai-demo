import streamlit as st
import replicate


def get_bot_response(prompt: str) -> str:
    try:
        api_key = st.secrets["replicate"]["api_key"]
    except Exception:
        return "Error: Replicate API token not found."

    try:
        client = replicate.Client(api_token=api_key)

        formatted_prompt = (
            "<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\n"
            "You are a helpful assistant<|eot_id|><|start_header_id|>user<|end_header_id|>\n\n"
            f"{prompt}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n"
        )

        output_container = st.empty()
        final_response = ""

        for event in client.stream(
            "meta/meta-llama-3-70b-instruct",
            input={
                "prompt": formatted_prompt,
                "top_p": 0.9,
                "max_tokens": 512,
                "min_tokens": 0,
                "temperature": 0.6,
                "prompt_template": "<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\nYou are a helpful assistant<|eot_id|><|start_header_id|>user<|end_header_id|>\n\n{prompt}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n",
                "presence_penalty": 1.15,
                "frequency_penalty": 0.2
            },
        ):
            final_response += str(event)
            output_container.markdown(final_response)

        return final_response

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


