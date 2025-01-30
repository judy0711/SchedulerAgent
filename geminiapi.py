import streamlit as st
import os
import google.generativeai as genai

# Securely retrieve API key
my_api_key = "AIzaSyDC3iSQUNqfLbgZOYMoEjbL9H7vzjpJBP0"  # Use environment variable or secrets
if not my_api_key:
    st.error("Error: Gemini API key not found.")
else:
    genai.configure(api_key=my_api_key)

# Initialize Gemini model
model = genai.GenerativeModel('gemini-pro')
chat_session = model.start_chat(history=[])  # Start chat session

# Initialize message history in session state
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "How may I help you today?"}]

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# User input
if prompt := st.chat_input("Enter your message here"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        # Generate response using Gemini API
        response = chat_session.send_message(prompt)
        response_text = response.text
        
        # Append assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response_text})
        
        with st.chat_message("assistant"):
            st.write(response_text)
    except Exception as e:
        st.error(f"Error communicating with Gemini API: {str(e)}")
