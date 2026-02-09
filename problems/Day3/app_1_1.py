"""
Day 3 - Step 1: Function Calling 기초

학습 목표:
- Agent의 기본 개념 이해 (도구 정의 + 도구 선택 + 실행)
- 키워드 기반 도구 선택 패턴 학습

[참고] 이 실습은 Agent 개념 학습을 위한 '시뮬레이션'입니다.
실제 Cortex Agents API와 다르며, 키워드 매칭으로 도구를 선택합니다.

실행:
streamlit run app_1_1.py
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

# 도구 정의 (이미 완성됨 - 구조만 확인하세요)
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
    # TODO: 키워드 기반으로 도구 선택하기 (3줄)
    # 힌트: 시간 관련 키워드가 있으면 get_current_time(), 없으면 complete_llm()
    time_keywords = ["시간", "몇 시", "몇시", "time", "시계"]
    is_time_query = any(kw in user_input.lower() for kw in time_keywords)

    if is_time_query:
        result = get_current_time()
        st.write(f"⏰ 현재 시간: {result}")
    else:
        # TODO: LLM에게 직접 질문하여 응답 표시 (2줄)
        pass  # TODO를 완성하세요
