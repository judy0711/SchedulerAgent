import streamlit as st
import os
import google.generativeai as genai
from collections import deque

# Securely retrieve API key
my_api_key = "GEMINI_API_KEY"  # Use environment variable or secrets
if not my_api_key:
    st.error("Error: Gemini API key not found.")
else:
    genai.configure(api_key=my_api_key)

# Initialize Gemini model
model = genai.GenerativeModel('gemini-pro')
chat_session = model.start_chat(history=[])  # Start chat session

# Initialize session state
if "tasks" not in st.session_state:
    st.session_state.tasks = deque()
if "messages" not in st.session_state:
    st.session_state.messages = []
if "started" not in st.session_state:
    st.session_state.started = False

# Show the start screen
if not st.session_state.started:
    st.markdown("<h1 style='text-align: center;'>📅 Daily Task Scheduler</h1>", unsafe_allow_html=True)
    
    
    # st.session_state.messages.append({"role": "assistant", "content": "Ask me to schedule your daily tasks!"})
    # if st.button("🚀 Start"):
    #     st.session_state.started = True
    #     st.rerun()

    # Centered Start Button
    if st.button("🚀 Start"):
        st.session_state.started = True
        st.rerun()
    
else:
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # Task input and Encouraging Message Side by Side
    col_task, col_encourage = st.columns([1, 1])

    with col_task:
        st.markdown("### 📝 Add a Task")
        with st.container(border=True):
            item = st.text_input("Task Item:", placeholder="Enter task description...")
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
                        # Prompt for the model
                       f"""
                        ### User's Daily Task Schedule & Encouragement

                        #### Tasks for Today:
                        {briefing_text}

                        #### Instructions:
                        1. Organize these tasks into the optimal schedule.
                        2. Use the **exact format** below for scheduling:
                        - Task 1: 9:00 AM - 10:00 AM (High Priority)
                        - Task 2: 10:00 AM - 11:00 AM (Medium Priority)
                        - Task 3: 11:00 AM - 12:30 PM (Low Priority)
                        (Ensure proper spacing between tasks.)
                        3. Provide a **daily briefing** summarizing the schedule in a paragraph.
                        4. Include an **encouraging message** based on the user’s preferences.

                        #### Formatting Guidelines:
                        **Schedule:** (Strictly follow this structure)
                        - Task 1: [Start Time] - [End Time]
                        - Task 2: [Start Time] - [End Time]
                        - Task 3: [Start Time] - [End Time]

                        **Daily Briefing:**
                        - A short paragraph summarizing the tasks.
                        - Provide encouragement and motivation with {encouraging_tone} tone.
                        - User's thought of the day: "{encouraging_message}"
                        """
                    )
                    response_text = response.text
                    st.markdown("### 📌 Daily Schedule & Encouragement:")
                    st.success(response_text)
                except Exception as e:
                    st.error(f"Error communicating with Gemini API: {str(e)}")
            else:
                st.warning("⚠️ No tasks to schedule.")