"""
Step 5-2: 시스템 프롬프트 추가

학습 목표:
- 시스템 프롬프트로 AI 역할 정의하기
- 사이드바로 대화 관리하기

실행:
streamlit run app_5_2.py
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

st.title("🎯 완성형 챗봇")

# TODO: 시스템 프롬프트 정의 (AI의 역할과 성격을 지정)
# 힌트: AI의 역할, 답변 언어, 스타일 등을 문자열로 정의하세요
SYSTEM_PROMPT = "당신은 AI 어시스턴트입니다."  # TODO를 완성하세요

# TODO: 시스템 메시지 포함하여 초기화
# 힌트: messages 리스트에 system role 메시지를 첫 번째로 추가
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]

# TODO: 사이드바에 대화 관리 패널 (초기화 버튼)
# 힌트: with st.sidebar: 블록에 st.button()으로 초기화 기능 구현


for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.write(message["content"])

user_input = st.chat_input("메시지를 입력하세요...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)
    
    conversation = "\n".join([
        f"{msg['role']}: {msg['content']}"
        for msg in st.session_state.messages
    ])
    
    with st.chat_message("assistant"):
        ai_response = complete_llm(session, "llama3.1-70b", conversation)
        st.write(ai_response)
    
    st.session_state.messages.append({"role": "assistant", "content": ai_response})
