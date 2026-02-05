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

# TODO: 시스템 프롬프트 정의
# 힌트: SYSTEM_PROMPT = "당신은 친절하고 도움이 되는 AI 어시스턴트입니다. 한국어로 답변해주세요."
SYSTEM_PROMPT = "당신은 AI 어시스턴트입니다."  # TODO를 완성하세요

# TODO: 시스템 메시지 포함하여 초기화
# 힌트: if "messages" not in st.session_state:
#           st.session_state.messages = [
#               {"role": "system", "content": SYSTEM_PROMPT}
#           ]
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]

# TODO: 사이드바에 대화 관리 패널
# 힌트: with st.sidebar:
#           st.write("### 💬 대화 관리")
#           if st.button("대화 초기화"):
#               st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
#               st.rerun()


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
        ai_response_stream = Complete(
            model="llama3.1-70b",
            prompt=conversation,
            session=session,
            stream=True
        )
        ai_response = st.write_stream(ai_response_stream)
    
    st.session_state.messages.append({"role": "assistant", "content": ai_response})
