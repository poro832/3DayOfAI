"""
Day 3 - Step 1: Function Calling 기초 (정답)
"""

import streamlit as st
from snowflake.snowpark import Session
from datetime import datetime

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

st.title("🕐 시간 조회 Agent")

# 도구 정의
tools = [{
    "type": "function",
    "function": {
        "name": "get_current_time",
        "description": "현재 시간을 반환합니다",
        "parameters": {"type": "object", "properties": {}}
    }
}]

def get_current_time():
    """현재 시간 반환"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

user_input = st.text_input("질문", "지금 몇 시야?")

if user_input and st.button("실행"):
    # 시간 관련 키워드 확인
    time_keywords = ["시간", "몇 시", "몇시", "time", "시계"]
    is_time_query = any(kw in user_input.lower() for kw in time_keywords)

    if is_time_query:
        result = get_current_time()
        st.write(f"⏰ 현재 시간: {result}")
    else:
        response = complete_llm(session, "llama3.1-70b", user_input)
        st.write(response)
