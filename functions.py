import os
import streamlit as st
import replicate

# Load Replicate API key from Streamlit secrets
replicate_api_token = st.secrets.get("replicate", {}).get("api_key")

# Set the token as an environment variable (Replicate uses this automatically)
if replicate_api_token:
    os.environ["REPLICATE_API_TOKEN"] = replicate_api_token


def get_bot_response(prompt: str, topic: str = "General") -> str:
    if not replicate_api_token:
        return "Error: Replicate API token not found."

    try:
        # Call Mistral model from Replicate
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
