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

# TODO: 여러 도구 정의 (get_time, calculate, get_weather)
# 힌트: app_1_1.py의 도구 정의 패턴을 참고하여
#       3개의 도구를 리스트로 정의하세요
#       calculate는 expression, get_weather는 city 파라미터 필요
tools = []  # TODO를 완성하세요

# TODO: 각 도구의 함수 구현
def get_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def calculate(expression):
    # TODO: 계산기 구현
    # 힌트: 허용된 문자만 체크 후 eval()로 계산 (보안 주의!)
    return "0"  # TODO를 완성하세요

def get_weather(city):
    # TODO: 날씨 조회 구현 (샘플 데이터)
    # 힌트: 도시별 날씨 딕셔너리를 만들고 dict.get()으로 조회
    return "정보 없음"  # TODO를 완성하세요

# 도구 실행 함수
def execute_tool(tool_name, args=None):
    if tool_name == "get_time":
        return get_time()
    elif tool_name == "calculate":
        return calculate(args.get("expression", "0"))
    elif tool_name == "get_weather":
        return get_weather(args.get("city", "서울"))
    return "알 수 없는 도구"

st.write("### 사용 가능한 도구")
st.write("- ⏰ 시간 조회")
st.write("- 🧮 계산기")
st.write("- 🌤️ 날씨 조회")

user_input = st.text_input("질문", "지금 몇 시야?")

if user_input and st.button("실행"):
    # TODO: 키워드 기반 도구 선택 (시뮬레이션)
    # 힌트: 시간/계산/날씨 관련 키워드를 if-elif로 분기하여
    #       각각 get_time(), calculate(), get_weather() 호출
    #       매칭 안 되면 LLM에게 직접 질문

    st.info("💡 TODO를 완성하세요")
