"""
Step 3-2: 모델 선택 챗봇

학습 목표:
- st.selectbox로 모델 선택하기
- st.checkbox로 옵션 추가하기

실행:
streamlit run app_3_2.py
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

# TODO: 모델 선택 셀렉트박스
# 힌트: selected_model = st.selectbox(
#           "모델 선택",
#           ["llama3.1-70b", "llama3.1-405b", "mixtral-8x7b"]
#       )
selected_model = "llama3.1-70b"  # TODO를 완성하세요

# TODO: 상세 설명 체크박스
# 힌트: detailed = st.checkbox("상세한 설명 포함")
detailed = False  # TODO를 완성하세요

user_question = st.text_input("질문을 입력하세요")

if user_question:
    prompt = user_question
    if detailed:
        prompt = f"{user_question}\n\n상세하고 구체적으로 설명해주세요."
    
    with st.spinner("생각하는 중..."):
        response = Complete(
            model=selected_model,
            prompt=prompt,
            session=session
        )
    
    st.write("### AI 답변")
    st.write(response)
