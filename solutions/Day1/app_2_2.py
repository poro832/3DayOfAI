"""
Step 2-2: 캐싱으로 성능 개선 (정답)
"""

import streamlit as st
from snowflake.snowpark import Session
import time

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

@st.cache_data
def get_ai_response(question, _session):
    response = complete_llm(_session, "llama3.1-70b", question)
    return response

session = get_snowflake_session()

st.title("⚡ 캐싱 성능 테스트")
st.write("같은 질문을 여러 번 해보세요!")

user_question = st.text_input("질문을 입력하세요")

if user_question:
    start_time = time.time()
    response = get_ai_response(user_question, session)
    elapsed = time.time() - start_time
    
    st.write("### AI 답변")
    st.write(response)
    
    st.info(f"⏱️ 응답 시간: {elapsed:.2f}초")
    
    if elapsed < 0.1:
        st.success("✅ 캐시에서 가져왔습니다!")
    else:
        st.warning("⏳ 첫 응답입니다. (캐시에 저장됨)")
