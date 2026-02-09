"""
Step 1-2: 첫 LLM 호출

학습 목표:
- Complete() 함수로 LLM 호출하기
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

# TODO: 사용자 질문 입력받기
# 힌트: st.text_input() 함수를 사용하세요
user_question = None  # TODO를 완성하세요

# TODO: 질문이 있을 때 AI 응답 받기
if user_question:
    # TODO: complete_llm 함수로 AI 응답을 받고, st.write()로 출력하세요
    # 힌트: st.spinner()로 로딩 표시, complete_llm()으로 응답 받기
    pass  # TODO를 완성하면 이 줄을 삭제하세요
