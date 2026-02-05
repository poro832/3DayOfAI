"""
Step 5-1: 컨텍스트 챗봇 구현

학습 목표:
- 대화 컨텍스트 유지하기
- 전체 히스토리를 프롬프트에 포함

실행:
streamlit run app_5_1.py
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

st.title("🧠 컨텍스트 챗봇")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

user_input = st.chat_input("메시지를 입력하세요...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)
    
    # TODO: 전체 대화 히스토리 구성
    # 힌트: conversation = "\n".join([
    #           f"{msg['role']}: {msg['content']}"
    #           for msg in st.session_state.messages
    #       ])
    conversation = user_input  # TODO를 완성하세요 (위 힌트 참고)

    # TODO: 컨텍스트 포함하여 AI 응답 생성
    with st.chat_message("assistant"):
        ai_response = complete_llm(session, "llama3.1-70b", conversation)
        st.write(ai_response)
    
    st.session_state.messages.append({"role": "assistant", "content": ai_response})
