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

with st.sidebar:
    st.write("### ⚙️ 설정")

    # TODO: 각 위젯을 사이드바 안에 배치하세요
    # 힌트: st.selectbox(), st.slider(), st.checkbox() 사용
    model = "llama3.1-70b"  # TODO: st.selectbox("모델 선택", [...])로 교체
    temperature = 0.7  # TODO: st.slider("Temperature", 0.0, 1.0, 0.7)로 교체
    detailed = False  # TODO: st.checkbox("상세한 설명 포함")로 교체

user_question = st.text_input("질문을 입력하세요")

if user_question:
    # TODO: 옵션에 따라 extra 지시를 추가하세요
    extra = ""
    if detailed:
        extra += " 예시와 함께 상세하게 설명하세요."  # 이미 완성됨
    if temperature > 0.7:
        extra += ""  # TODO: 창의적 답변 지시 추가
    prompt = f"{user_question}{extra}"

    with st.spinner("생각하는 중..."):
        response = complete_llm(session, model, prompt)

    st.write("### AI 답변")
    st.write(response)
