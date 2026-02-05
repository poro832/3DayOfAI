"""
Step 2-2: 캐싱으로 성능 개선

학습 목표:
- @st.cache_data 데코레이터 사용하기
- 반복 호출 최적화

실행:
streamlit run app_2_2.py
"""

import streamlit as st
from snowflake.snowpark import Session
import time

# TODO: @st.cache_data 데코레이터 추가
def get_snowflake_session():
    connection_parameters = st.secrets["connections"]["snowflake"]
    return Session.builder.configs(connection_parameters).create()

def complete_llm(session, model, prompt):
    """SQL 방식으로 Cortex LLM 호출"""
    escaped_prompt = prompt.replace("'", "''")
    sql = f"SELECT SNOWFLAKE.CORTEX.COMPLETE('{model}', '{escaped_prompt}')"
    result = session.sql(sql).collect()
    return result[0][0]


# TODO: @st.cache_data 데코레이터 추가
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
