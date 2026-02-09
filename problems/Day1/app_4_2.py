"""
Step 4-2: 채팅 UI 만들기

학습 목표:
- st.chat_message로 말풍선 만들기
- st.chat_input으로 입력 받기

실행:
streamlit run app_4_2.py
"""

import streamlit as st
from snowflake.snowpark import Session

@st.cache_resource
def get_snowflake_session():
    connection_parameters = st.secrets["connections"]["snowflake"]
    return Session.builder.configs(connection_parameters).create()

def complete_llm(session, model, prompt):
    """SQL 방식으로 Cortex LLM 호출"""
    escaped_prompt = prompt.replace("'", "''")
    sql = f"SELECT SNOWFLAKE.CORTEX.COMPLETE('{model}', '{escaped_prompt}')"
    result = session.sql(sql).collect()
    return result[0][0]


session = get_snowflake_session()

st.title("💬 채팅 UI")

# TODO: messages 초기화 (빈 리스트)
if "messages" not in st.session_state:
    st.session_state.messages = []

# TODO: 이전 메시지 표시
# 힌트: st.chat_message()로 role에 맞는 말풍선을 만들어 표시


# TODO: 사용자 입력
# 힌트: st.chat_input()을 사용하세요
user_input = st.chat_input("메시지를 입력하세요...")

if user_input:
    # TODO: 사용자 메시지 추가 및 표시
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)
    
    # AI 응답
    with st.spinner("생각하는 중..."):
        ai_response = complete_llm(session, "llama3.1-70b", user_input)
    
    # TODO: AI 메시지 추가 및 표시
    st.session_state.messages.append({"role": "assistant", "content": ai_response})
    with st.chat_message("assistant"):
        st.write(ai_response)
