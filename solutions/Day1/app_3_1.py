"""
Step 3-1: 온도 조절 챗봇 (정답)

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

st.title("🎚️ 온도 조절 챗봇")

temperature = st.slider("Temperature (창의성)", 0.0, 1.0, 0.7)
st.write(f"현재 Temperature: {temperature}")

user_question = st.text_input("질문을 입력하세요")

if user_question:
    # temperature에 따라 프롬프트 스타일 조정
    if temperature < 0.3:
        style = "정확하고 간결하게 답변하세요."
    elif temperature < 0.7:
        style = "명확하게 답변하세요."
    else:
        style = "창의적이고 다양한 관점에서 답변하세요."

    prompt = f"{user_question}\n\n({style})"

    with st.spinner("생각하는 중..."):
        response = complete_llm(session, "llama3.1-70b", prompt)

    st.write("### AI 답변")
    st.write(response)
