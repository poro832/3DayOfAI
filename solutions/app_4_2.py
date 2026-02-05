"""
Step 4-2: 채팅 UI 만들기 (정답)
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

# 시스템 프롬프트 (한국어 응답 지시)
SYSTEM_PROMPT = "당신은 친절한 AI 어시스턴트입니다. 반드시 한국어로 짧고 간결하게 답변하세요."

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

    # 시스템 프롬프트와 함께 전달
    full_prompt = f"""[시스템 지시사항]
{SYSTEM_PROMPT}

[사용자 질문]
{user_input}

AI:"""

    with st.spinner("생각하는 중..."):
        ai_response = complete_llm(session, "llama3.1-70b", full_prompt)

    st.session_state.messages.append({"role": "assistant", "content": ai_response})
    with st.chat_message("assistant"):
        st.write(ai_response)
