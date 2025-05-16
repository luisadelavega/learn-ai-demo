import streamlit as st
from functions import get_bot_response

st.set_page_config(page_title="Chatbot", page_icon="💬")

st.title("💬 Streamlit + Replicate Chatbot")

if "messages" not in st.session_state:
    st.session_state.messages = []

topic = st.selectbox("Choose a topic:", ["General", "Support", "Technical"], key="topic")

# Display previous messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

prompt = st.chat_input("Type your message...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get response from bot
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            reply = get_bot_response(prompt, topic)
            st.markdown(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})
