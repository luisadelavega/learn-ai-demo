import replicate
import streamlit as st

def get_bot_response(prompt: str) -> str:
    try:
        api_key = st.secrets["replicate"]["api_key"]
    except Exception:
        return "Error: Replicate API token not found."

    try:
        client = replicate.Client(api_token=api_key)

        # Format the prompt according to the model's expected template
        formatted_prompt = (
            "<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\n"
            "You are a helpful assistant<|eot_id|><|start_header_id|>user<|end_header_id|>\n\n"
            f"{prompt}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n"
        )

        # Create a Streamlit container to update content in-place
        output_container = st.empty()
        final_response = ""

        # Stream response
        for event in client.stream(
            "meta/meta-llama-3-70b-instruct",
            input={
                "top_p": 0.9,
                "prompt": formatted_prompt,
                "max_tokens": 512,
                "min_tokens": 0,
                "temperature": 0.6,
                "prompt_template": None,  # Not needed when using formatted prompt
                "presence_penalty": 1.15,
                "frequency_penalty": 0.2
            },
        ):
            final_response += str(event)
            output_container.markdown(final_response)

        return final_response

    except Exception as e:
        return f"Error calling Replicate: {str(e)}"
