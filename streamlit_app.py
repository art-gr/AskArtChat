import streamlit as st
from openai import OpenAI

# Show title and description
st.title("💬 AskArtChat")
st.write(
    "DeepSeek AI Assistant – Smart, Fast, and Reliable. "
    "You can also learn how to build this app step by step by [following our tutorial](https://docs.streamlit.io/develop/tutorials/llms/build-conversational-apps)."
)

# Ask user for their Deepseek API Key
deepseek_api_key = st.text_input("Deepseek API Key", type="password")

if not deepseek_api_key:
    st.info("Please add your Deepseek API Key to continue.", icon="🗝️")
else:
    # Create OpenAI client with Deepseek base URL
    client = OpenAI(
        api_key=deepseek_api_key,
        base_url="https://api.deepseek.com"  # Removed /v1 suffix
    )

    # Initialize session state for messages if it doesn't exist
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display existing chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("What is up?"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        try:
            # Generate response using the OpenAI client
            stream = client.chat.completions.create(
                model="deepseek-chat",  # Using Deepseek's model
                messages=st.session_state.messages,  # Using just the conversation history
                stream=True,
            )

            # Display assistant response
            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                full_response = ""
                
                # Process the stream
                for chunk in stream:
                    if chunk.choices[0].delta.content is not None:
                        full_response += chunk.choices[0].delta.content
                        message_placeholder.markdown(full_response + "▌")
                
                message_placeholder.markdown(full_response)
                # Add assistant's message to chat history
                st.session_state.messages.append({"role": "assistant", "content": full_response})

        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
