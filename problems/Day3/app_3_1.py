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

# TODO: 여러 도구 정의
# 힌트: tools = [
#     {
#         "type": "function",
#         "function": {
#             "name": "get_time",
#             "description": "현재 시간을 반환합니다",
#             "parameters": {"type": "object", "properties": {}}
#         }
#     },
#     {
#         "type": "function",
#         "function": {
#             "name": "calculate",
#             "description": "수학 계산을 수행합니다",
#             "parameters": {
#                 "type": "object",
#                 "properties": {
#                     "expression": {"type": "string", "description": "계산식"}
#                 },
#                 "required": ["expression"]
#             }
#         }
#     },
#     {
#         "type": "function",
#         "function": {
#             "name": "get_weather",
#             "description": "날씨를 조회합니다",
#             "parameters": {
#                 "type": "object",
#                 "properties": {
#                     "city": {"type": "string", "description": "도시명"}
#                 },
#                 "required": ["city"]
#             }
#         }
#     }
# ]
tools = []  # TODO를 완성하세요

# TODO: 각 도구의 함수 구현
def get_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def calculate(expression):
    # 힌트: eval() 사용 (보안 주의: 학습용으로만 사용)
    pass

def get_weather(city):
    pass

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
    # TODO: LLM 호출 및 도구 실행
    # 힌트: response = Complete(model="llama3.1-70b", prompt=user_input, tools=tools, session=session)
    #       # 응답 분석 후 적절한 도구 실행

    st.info("💡 TODO를 완성하세요")
