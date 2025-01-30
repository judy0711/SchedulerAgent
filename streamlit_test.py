import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

if 'messages' not in st.session_state:
    st.session_state.messages = [{"role" : "assistant", "content" : "Hello! How can I help you today?"}]

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.write(m["content"])

if query := st.text_input("Type your message here"):
    st.session_state.messages.append({"role" : "user", "content" : query})
    st.session_state.messages.append({"role" : "assistant", "content" : "I'm sorry, I don't understand your question."})