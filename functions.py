# functions.py

import os
import replicate
import streamlit as st

def get_bot_response(prompt: str, topic: str = "General") -> str:
    try:
        # Load API key from Streamlit secrets dynamically
        replicate_api_token = st.secrets["replicate"]["api_key"]
        os.environ["REPLICATE_API_TOKEN"] = replicate_api_token
    except Exception:
        return "Error: Replicate API token not found."

    try:
        output = replicate.run(
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
