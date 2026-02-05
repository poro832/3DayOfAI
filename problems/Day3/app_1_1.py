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

# TODO: 도구 정의
# 힌트: tools = [{
#     "type": "function",
#     "function": {
#         "name": "get_current_time",
#         "description": "현재 시간을 반환합니다",
#         "parameters": {"type": "object", "properties": {}}
#     }
# }]


# TODO: 함수 구현
def get_current_time():
    """현재 시간 반환"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

user_input = st.text_input("질문", "지금 몇 시야?")

if user_input and st.button("실행"):
    # TODO: LLM에게 도구 제공
    # 힌트: response = Complete(
    #           model="llama3.1-70b",
    #           prompt=user_input,
    #           tools=tools,
    #           session=session
    #       )

    # TODO: 도구 호출 확인
    # 힌트: if "tool_calls" in response:
    #           result = get_current_time()
    #           st.write(f"⏰ {result}")
    pass  # TODO를 완성하면 이 줄을 삭제하세요
