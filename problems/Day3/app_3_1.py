"""
Day 3 - Step 3: 다중 도구 Agent

학습 목표:
- 여러 도구를 가진 Agent 구현
- 사용자 의도에 따른 도구 라우팅

[참고] 이 실습은 Agent 개념 학습을 위한 '시뮬레이션'입니다.
도구 선택은 키워드 기반이며, 실제 Cortex Agents는 LLM이 자율 선택합니다.

실행:
streamlit run app_3_1.py
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

st.title("🛠️ 다중 도구 Agent")

# 여러 도구 정의
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_time",
            "description": "현재 시간을 반환합니다",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "수학 계산을 수행합니다",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {"type": "string", "description": "계산식 (예: 2+3*4)"}
                },
                "required": ["expression"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "날씨를 조회합니다",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "도시명"}
                },
                "required": ["city"]
            }
        }
    }
]

def get_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def calculate(expression):
    try:
        # 간단한 수식만 허용 (보안용)
        allowed = set("0123456789+-*/(). ")
        if all(c in allowed for c in expression):
            return str(eval(expression))
        return "허용되지 않은 문자가 포함되어 있습니다"
    except:
        return "계산 오류"

def get_weather(city):
    weather_data = {
        "서울": "15°C, 맑음",
        "부산": "18°C, 구름 조금",
        "제주": "20°C, 흐림"
    }
    return weather_data.get(city, "16°C, 정보 없음")

def execute_tool(tool_name, args=None):
    if tool_name == "get_time":
        return f"⏰ 현재 시간: {get_time()}"
    elif tool_name == "calculate":
        result = calculate(args.get("expression", "0"))
        return f"🧮 계산 결과: {result}"
    elif tool_name == "get_weather":
        city = args.get("city", "서울")
        return f"🌤️ {city} 날씨: {get_weather(city)}"
    return "알 수 없는 도구"

st.write("### 사용 가능한 도구")
st.write("- ⏰ 시간 조회: \"지금 몇 시야?\"")
st.write("- 🧮 계산기: \"123 * 456 계산해줘\"")
st.write("- 🌤️ 날씨 조회: \"서울 날씨 어때?\"")

user_input = st.text_input("질문", "지금 몇 시야?")

if user_input and st.button("실행"):
    with st.spinner("Agent 실행 중..."):
        # 키워드 기반 도구 선택 (간단한 패턴 매칭)
        if any(word in user_input for word in ["시간", "몇 시"]):
            result = execute_tool("get_time")
        elif any(word in user_input for word in ["계산", "+", "-", "*", "/"]):
            # 숫자와 연산자 추출
            import re
            nums = re.findall(r'[\d\+\-\*\/\(\)\.\s]+', user_input)
            expression = ''.join(nums).strip() if nums else "0"
            result = execute_tool("calculate", {"expression": expression})
        elif any(word in user_input for word in ["날씨", "기온", "온도"]):
            # TODO: 도시명 추출 후 날씨 조회 (3줄)
            # 힌트: cities = ["서울", "부산", "제주", ...] 에서 user_input에 포함된 도시 찾기
            #       execute_tool("get_weather", {"city": city})
            result = "TODO를 완성하세요"  # TODO를 완성하세요
        else:
            # LLM에게 직접 답변 요청
            result = complete_llm(session, "llama3.1-70b", user_input)

    st.write("### 결과")
    st.write(result)
