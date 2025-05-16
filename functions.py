import replicate
import streamlit as st

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

