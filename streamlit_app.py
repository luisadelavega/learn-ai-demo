import streamlit as st
from functions import get_bot_response

# Page setup
st.set_page_config(page_title="Nubo Knowledge Checker", page_icon="🧠")

# Sidebar navigation
tab = st.sidebar.radio("Select tab", ["User", "Manager"])

# Shared header
st.title("🧠 Nubo Knowledge Checker")
st.subheader("Test your understanding and get instant feedback from Nubo.")

# --- USER TAB ---
if tab == "User":
    if "messages" not in st.session_state:
        st.session_state.messages = []

    topic = st.selectbox("Choose a topic:", ["General", "Support", "Technical"], key="topic")

    # Display chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Input for user message
    prompt = st.chat_input("Type your message...")

    if prompt:
        # Display user's message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Get and display assistant response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                reply = get_bot_response(prompt)
                st.markdown(reply)

        # Save assistant response
        st.session_state.messages.append({"role": "assistant", "content": reply})

# --- MANAGER TAB ---
elif tab == "Manager":
    st.subheader("📊 Manager Dashboard")
    st.info("This section is under development. Check back soon!")
