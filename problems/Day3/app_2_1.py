"""
Day 3 - Step 2: 날씨 조회 Agent

학습 목표:
- 파라미터가 있는 도구 정의 방법
- 사용자 입력에서 파라미터 추출

[참고] 이 실습은 Agent 개념 학습을 위한 '시뮬레이션'입니다.
날씨 데이터는 하드코딩된 샘플이며, 실제 API 연동이 아닙니다.

실행:
streamlit run app_2_1.py
"""

import streamlit as st
from snowflake.snowpark import Session
import json

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

st.title("🌤️ 날씨 조회 Agent")

# 도구 정의
tools = [{
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "도시의 현재 날씨를 반환합니다",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "도시 이름 (예: 서울, 부산)"
                }
            },
            "required": ["city"]
        }
    }
}]

# TODO: 날씨 함수 구현
def get_weather(city):
    """도시별 날씨 반환 (시뮬레이션)"""
    # 힌트: 도시별 temp와 condition을 딕셔너리로 정의하고
    #       dict.get()으로 해당 도시 정보 반환 (없으면 기본값)
    pass

user_input = st.text_input("질문", "서울 날씨 어때?")

if user_input and st.button("실행"):
    with st.spinner("Agent 실행 중..."):
        # TODO: 입력에서 도시명 추출하기 (키워드 매칭)
        # 힌트: 도시 리스트를 만들고 user_input에 포함된 도시를 찾기
        found_city = None  # TODO를 완성하세요

        # TODO: 도시가 발견되면 날씨 조회, 아니면 LLM 응답
        # 힌트: found_city가 있으면 get_weather() 호출 후 결과 표시,
        #       없으면 complete_llm()으로 일반 응답

        st.info("💡 TODO를 완성하세요")
