import streamlit as st
import os
import google.generativeai as genai
from collections import deque

# Securely retrieve API key
my_api_key = "AIzaSyDC3iSQUNqfLbgZOYMoEjbL9H7vzjpJBP0"  # Use environment variable or secrets
if not my_api_key:
    st.error("Error: Gemini API key not found.")
else:
    genai.configure(api_key=my_api_key)

# Initialize Gemini model
model = genai.GenerativeModel('gemini-pro')
chat_session = model.start_chat(history=[])  # Start chat session

# Initialize task list in session state as a queue
if "tasks" not in st.session_state:
    st.session_state.tasks = deque()

# Initialize message history in session state
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Ask me to schedule your daily tasks!"}]
    st.session_state.messages.append({"role": "user", "content": "I can help you organize your tasks and provide a daily briefing."})
    
    button = st.button("📅 Get Started")

# Display chat history
st.markdown("<h1 style='text-align: center;'>Daily Task Scheduler</h1>", unsafe_allow_html=True)

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Task input and Encouraging Message Side by Side
col_task, col_encourage = st.columns([1, 1])  # Task input takes more space than Encouraging Message


with col_task:
    st.markdown("### 📝 Add a Task")
    with st.container(border=True):
        item = st.text_input("Task Item:", placeholder="Enter task description...")
        #col1, col2, col3 = st.columns([1, 1, 1])
        col1, col2 = st.columns([1, 1])
        col3 = st.columns([1])[0]
        with col1:
            due_date = st.date_input("Due Date:")
        with col2:
            time_estimation = st.number_input("Time Estimation (hours):", min_value=0.5, step=0.5)
        with col3:
            priority = st.selectbox("Priority:", ["High", "Medium", "Low"])
        if st.button("➕ Add Task", use_container_width=True):
            if item:
                task = {
                    "Item": item,
                    "Due Date": due_date,
                    "Time Estimation": time_estimation,
                    "Priority": priority
                }
                st.session_state.tasks.append(task)
                st.success("✅ Task added successfully!")
                st.rerun()
            else:
                st.warning("⚠️ Please enter a task item.")

with col_encourage:
    st.markdown("### 🌟 Encouraging Message")
    with st.container(border=True):
        encouraging_tone = st.selectbox("Choose the tone for the encouragement:", ["Motivational", "Calm & Reassuring", "Energetic", "Professional", "Friendly"])
        encouraging_message = st.text_area("Enter any thoughts you have for the day:", placeholder="Thoughts...")

# Sorting tasks by due date and priority
priority_order = {"High": 1, "Medium": 2, "Low": 3}
st.session_state.tasks = deque(sorted(st.session_state.tasks, key=lambda x: (x["Due Date"], priority_order[x["Priority"]])))

# Display tasks with individual remove buttons
st.markdown("### ✅ Your To-Do List:")
if st.session_state.tasks:
    for idx, task in enumerate(list(st.session_state.tasks), start=1):
        col_task, col_remove = st.columns([4, 1])
        with col_task:
            st.write(f"{idx}. **{task['Item']}** - 📅 {task['Due Date']} - ⏳ {task['Time Estimation']}h - 🔥 {task['Priority']}")
        with col_remove:
            if st.button(f"❌ Remove {idx}", key=f"remove_{idx}"):
                st.session_state.tasks.remove(task)
                st.rerun()
else:
    st.write("No tasks available.")

# Buttons for task management
st.markdown("---")

col1 = st.columns([1])[0]

with col1:
    if st.button("📅 Generate Schedule & Briefing", use_container_width=True):
        if st.session_state.tasks:
            briefing_text = "\n".join([f"{task['Item']} (Due: {task['Due Date']}, Time: {task['Time Estimation']}h, Priority: {task['Priority']})" for task in st.session_state.tasks])
            try:
                response = chat_session.send_message(
                    f"Todo list for today: {briefing_text}. Arrange the todo list and give a daily briefing with encouragement for the day."
                    f" Tone of encouragement message: {encouraging_tone}. User's thought of the day: {encouraging_message}"
                )
                response_text = response.text
                st.markdown("### 📌 Daily Schedule & Encouragement:")
                st.success(response_text)
            except Exception as e:
                st.error(f"Error communicating with Gemini API: {str(e)}")
        else:
            st.warning("⚠️ No tasks to schedule.")
