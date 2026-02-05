"""
Step 2-1: 스트리밍 응답 구현

학습 목표:
- stream=True 옵션 사용하기
- st.write_stream()으로 타이핑 효과 만들기

실행:
streamlit run app_2_1.py
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


session = get_snowflake_session()

st.title("✨ 스트리밍 챗봇")

user_question = st.text_input("질문을 입력하세요")

if user_question:
    st.write("### AI 답변")

    # 스트리밍 효과를 위한 함수 (단어별로 출력)
    def stream_text(text):
        import time
        words = text.split()
        for word in words:
            yield word + ' '
            time.sleep(0.02)

    # TODO: LLM 응답을 받아서 스트리밍으로 출력하기
    # 힌트: response = complete_llm(session, "llama3.1-70b", user_question)
    #       st.write_stream(stream_text(response))
    
