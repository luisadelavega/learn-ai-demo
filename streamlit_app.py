import streamlit as st
import replicate

def get_bot_response(prompt: str) -> str:
    try:
        # Load API key from Streamlit secrets
        api_key = st.secrets["replicate"]["api_key"]
    except Exception:
        return "Error: Replicate API token not found."

    try:
        # Initialize Replicate client
        client = replicate.Client(api_token=api_key)

        # Format the prompt using model's required template
        formatted_prompt = (
            "<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\n"
            "You are a helpful assistant<|eot_id|><|start_header_id|>user<|end_header_id|>\n\n"
            f"{prompt}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n"
        )

        # Streamlit placeholder for dynamic updates
        output_container = st.empty()
        final_response = ""

        # Stream the response from Replicate
        for event in client.stream(
            "meta/meta-llama-3-70b-instruct",
            input={
                "prompt": formatted_prompt,
                "top_p": 0.9,
                "max_tokens": 512,
                "min_tokens": 0,
                "temperature": 0.6,
                "prompt_template": "",  # <-- Required, must be string not None
                "presence_penalty": 1.15,
                "frequency_penalty": 0.2
            },
        ):
            final_response += str(event)
            output_container.markdown(final_response)

        return final_response

    except Exception as e:
        return f"Error calling Replicate: {str(e)}"


# Streamlit UI
st.set_page_config(page_title="Chat with LLaMA 3", page_icon="🦙")
st.title("🦙 Chat with LLaMA 3 (70B Instruct)")

prompt = st.text_input("Ask a question:")

if prompt:
    st.write("Generating response...")
    reply = get_bot_response(prompt)
    st.markdown("**Full response:**")
    st.markdown(reply)
