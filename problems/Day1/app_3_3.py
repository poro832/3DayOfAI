"""
Step 3-3: 사이드바 활용

학습 목표:
- st.sidebar로 UI 분리하기
- 설정 패널 만들기

참고: Snowflake Cortex SQL 방식은 temperature 옵션을 지원하지 않아
프롬프트에 창의성 지시를 추가하는 방식으로 구현합니다.

실행:
streamlit run app_3_3.py
"""

import streamlit as st
from snowflake.snowpark import Session

@st.cache_resource
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

st.title("⚙️ 설정 가능한 챗봇")

# TODO: 사이드바에 설정 패널 만들기 (모델 선택, Temperature, 상세 설명)
# 힌트: with st.sidebar: 블록 안에 selectbox, slider, checkbox를 배치하세요
model = "llama3.1-70b"  # TODO를 완성하세요
temperature = 0.7  # TODO를 완성하세요
detailed = False  # TODO를 완성하세요

user_question = st.text_input("질문을 입력하세요")

if user_question:
    # TODO: 옵션(detailed, temperature)에 따라 프롬프트 구성하기
    # 힌트: detailed가 True이면 상세 설명 요청을 추가하고,
    #       temperature 값에 따라 응답 스타일 지시를 추가하세요

    prompt = user_question  # TODO를 완성하세요

    with st.spinner("생각하는 중..."):
        response = complete_llm(session, model, prompt)

    st.write("### AI 답변")
    st.write(response)
