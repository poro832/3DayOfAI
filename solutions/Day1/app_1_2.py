"""
Step 1-2: 첫 LLM 호출 (정답)

학습 목표:
- complete_llm() 함수로 LLM 호출하기 (SQL 방식)
- 사용자 입력 받기
- AI 응답 출력하기

실행:
streamlit run app_1_2.py
"""

import streamlit as st
from snowflake.snowpark import Session

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

st.title("🤖 나의 첫 AI 대화")

# 사용자 입력
user_question = st.text_input("질문을 입력하세요")

# AI 응답
if user_question:
    with st.spinner("생각하는 중..."):
        response = complete_llm(session, "llama3.1-70b", user_question)

    st.write("### AI 답변")
    st.write(response)
