import replicate
import streamlit as st

def get_bot_response(prompt: str, topic: str = "General") -> str:
    try:
        api_key = st.secrets["replicate"]["api_key"]
    except Exception:
        return "Error: Replicate API token not found."

    try:
        client = replicate.Client(api_token=api_key)

        output = client.run(
            "mistralai/mistral-7b-instruct-v0.1",
            input={
                "prompt": prompt,
                "temperature": 0.7,
                "max_new_tokens": 300,
                "top_p": 0.9
            }
        )
        return "".join(output)
    except Exception as e:
        return f"Error calling Replicate: {str(e)}"
