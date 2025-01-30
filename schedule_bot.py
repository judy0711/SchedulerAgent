import streamlit as st
import openai
import datetime

# Streamlit UI 설정
st.set_page_config(page_title="직장인 업무 스케줄링 챗봇", layout="centered")
st.title("📅 직장인 업무 스케줄링 챗봇")

# OpenAI API 키 설정 
OPENAI_API_KEY = "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"
openai.api_key = OPENAI_API_KEY

# 대화 상태 및 업무 일정 저장
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "무엇을 도와드릴까요?"}]
if "schedule" not in st.session_state:
    st.session_state.schedule = []

# 기존 메시지 표시
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.write(m["content"])

# 사용자 입력 받기
if prompt := st.chat_input("업무를 입력하세요"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # OpenAI API 호출
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "너는 직장인을 위한 업무 스케줄링 챗봇이야. 사용자가 입력한 업무를 일정으로 등록하거나, 기존 일정을 관리하는 역할을 해."},
            *st.session_state.messages,
            {"role": "user", "content": prompt}
        ]
    )
    
    #bot_response = response["choices"][0]["message"]["content"]
    bot_response = response.choices[0].message.content
    st.session_state.messages.append({"role": "assistant", "content": bot_response})
    
    with st.chat_message("assistant"):
        st.markdown(bot_response)
    
    # 업무 일정 등록 기능
    if "일정 등록" in prompt or "스케줄.? 추가" in prompt:
        date = st.date_input("날짜 선택")
        time = st.time_input("시간 선택")
        task = st.text_input("업무 내용을 입력하세요")
        
        if st.button("일정 저장"):
            st.session_state.schedule.append({
                "date": date.strftime("%Y-%m-%d"),
                "time": time.strftime("%H:%M"),
                "task": task
            })
            st.success(f"✅ 일정이 등록되었습니다: {date} {time} - {task}")
    
    # 기존 일정 조회 기능
    if "일정 확인" in prompt or "스케줄 보기" in prompt:
        if st.session_state.schedule:
            st.write("📅 등록된 일정 목록:")
            for s in st.session_state.schedule:
                st.write(f"- {s['date']} {s['time']} → {s['task']}")
        else:
            st.write("📌 현재 등록된 일정이 없습니다.")
