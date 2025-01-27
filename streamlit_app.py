import streamlit as st
import requests
import json

# Show title and description
st.title("💬 AskArtChat")
st.write(
    "DeekSeek AI Assistant – Smart, Fast, and Reliable. "
    "You can also learn how to build this app step by step by [following our tutorial](https://docs.streamlit.io/develop/tutorials/llms/build-conversational-apps)."
)

# Ask user for their Deepseek API Key
deepseek_api_key = st.text_input("Deepseek API Key", type="password")

if not deepseek_api_key:
    st.info("Please add your Deepseek API Key to continue.", icon="🗝️")
else:
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

        # Prepare the API request
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {deepseek_api_key}"
        }
        
        data = {
            "model": "deepseek-reasoner",
            "messages": [
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            "stream": True
        }

        try:
            # Make streaming request to Deepseek API
            with st.chat_message("assistant"):
                # Initialize placeholder for streaming response
                message_placeholder = st.empty()
                full_response = ""

                # Stream the response
                with requests.post(
                    "https://api.deepseek.com/",
                    headers=headers,
                    json=data,
                    stream=True
                ) as response:
                    response.raise_for_status()  # Raise an error for bad status codes
                    
                    for line in response.iter_lines():
                        if line:
                            line = line.decode('utf-8')
                            if line.startswith('data: '):
                                try:
                                    json_str = line[6:]  # Remove 'data: ' prefix
                                    if json_str.strip() == '[DONE]':
                                        break
                                    chunk = json.loads(json_str)
                                    if chunk.get('choices') and chunk['choices'][0].get('delta', {}).get('content'):
                                        content = chunk['choices'][0]['delta']['content']
                                        full_response += content
                                        # Update placeholder with accumulated response
                                        message_placeholder.markdown(full_response + "▌")
                                except json.JSONDecodeError:
                                    continue

                # Update placeholder one final time without cursor
                message_placeholder.markdown(full_response)
                
                # Add assistant's message to chat history
                st.session_state.messages.append({"role": "assistant", "content": full_response})

        except requests.exceptions.RequestException as e:
            st.error(f"An error occurred while communicating with the API: {str(e)}")
        except Exception as e:
            st.error(f"An unexpected error occurred: {str(e)}")
