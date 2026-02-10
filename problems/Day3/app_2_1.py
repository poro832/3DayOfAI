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

def get_weather(city):
    """도시별 날씨 반환 (시뮬레이션)"""
    weather_data = {
        "서울": {"temp": 15, "condition": "맑음"},
        # TODO: 나머지 4개 도시 추가 (4줄)
        # 힌트: "부산", "제주", "대구", "인천"
    }
    return weather_data.get(city, {"temp": 16, "condition": "정보 없음"})

user_input = st.text_input("질문", "서울 날씨 어때?")

if user_input and st.button("실행"):
    with st.spinner("Agent 실행 중..."):
        # 입력에서 도시명 추출
        cities = ["서울", "부산", "제주", "대구", "인천"]
        found_city = None
        for city in cities:
            if city in user_input:
                found_city = city
                break

        if found_city:
            weather = get_weather(found_city)
            st.write(f"### 🌤️ {found_city} 날씨")
            st.write(f"🌡️ 온도: {weather['temp']}°C")
            st.write(f"☁️ 상태: {weather['condition']}")
        else:
            response = complete_llm(session, "llama3.1-70b", user_input)
            st.write(response)
