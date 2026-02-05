"""
Day 3 - Step 2: 날씨 조회 Agent (정답)
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

def get_weather(city):
    """도시별 날씨 반환 (시뮬레이션)"""
    weather_data = {
        "서울": {"temp": 15, "condition": "맑음"},
        "부산": {"temp": 18, "condition": "구름 조금"},
        "제주": {"temp": 20, "condition": "흐림"},
        "대구": {"temp": 17, "condition": "맑음"},
        "인천": {"temp": 14, "condition": "안개"}
    }
    return weather_data.get(city, {"temp": 16, "condition": "정보 없음"})

user_input = st.text_input("질문", "서울 날씨 어때?")

if user_input and st.button("실행"):
    with st.spinner("Agent 실행 중..."):
        # 도시명 추출 (간단한 방식)
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
