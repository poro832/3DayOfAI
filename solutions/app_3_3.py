"""
Step 3-3: 사이드바 활용 (정답)

참고: Snowflake Cortex SQL 방식은 temperature 옵션을 지원하지 않아
프롬프트에 창의성 지시를 추가하는 방식으로 구현했습니다.
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

    model = st.selectbox(
        "모델 선택",
        ["llama3.1-70b", "mixtral-8x7b"]
    )

    temperature = st.slider("Temperature", 0.0, 1.0, 0.7)

    detailed = st.checkbox("상세한 설명 포함")

user_question = st.text_input("질문을 입력하세요")

if user_question:
    # 프롬프트 구성
    prompt = user_question

    if detailed:
        prompt += "\n\n상세하고 구체적으로 설명해주세요."

    # temperature에 따라 스타일 추가
    if temperature < 0.3:
        prompt += "\n(정확하고 간결하게 답변하세요.)"
    elif temperature >= 0.7:
        prompt += "\n(창의적이고 다양한 관점에서 답변하세요.)"

    with st.spinner("생각하는 중..."):
        response = complete_llm(session, model, prompt)

    st.write("### AI 답변")
    st.write(response)
