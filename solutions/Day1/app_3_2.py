"""
Step 3-2: 모델 선택 챗봇 (정답)
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

st.title("🤖 모델 선택 챗봇")

selected_model = st.selectbox(
    "모델 선택",
    ["llama3.1-70b", "llama3.1-405b", "mixtral-8x7b"]
)

detailed = st.checkbox("상세한 설명 포함")

user_question = st.text_input("질문을 입력하세요")

if user_question:
    prompt = user_question
    if detailed:
        prompt = f"{user_question}\n\n상세하고 구체적으로 설명해주세요."
    
    with st.spinner("생각하는 중..."):
        response = complete_llm(session, selected_model, prompt)
    
    st.write("### AI 답변")
    st.write(response)
