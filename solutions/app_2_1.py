"""
Step 2-1: 스트리밍 응답 구현 (정답)
"""

import streamlit as st
from snowflake.snowpark import Session

def get_snowflake_session():
    connection_parameters = st.secrets["connections"]["snowflake"]
    return Session.builder.configs(connection_parameters).create()
def complete_llm(session, model, prompt):
    """SQL 방식으로 Cortex LLM 호출"""
    escaped_prompt = prompt.replace("'", "''")
    sql = f"SELECT SNOWFLAKE.CORTEX.COMPLETE('{model}', '{escaped_prompt}')"
    result = session.sql(sql).collect()
    return result[0][0]

def stream_text(text):
    """텍스트를 스트리밍처럼 출력"""
    import time
    words = text.split()
    for word in words:
        yield word + ' '
        time.sleep(0.02)


session = get_snowflake_session()

st.title("✨ 스트리밍 챗봇")

user_question = st.text_input("질문을 입력하세요")

if user_question:
    st.write("### AI 답변")
    
    response_stream = stream_text(complete_llm(session, "llama3.1-70b", user_question))
    
    st.write_stream(response_stream)
