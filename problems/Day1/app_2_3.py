"""
Step 2-3: AI 콘텐츠 생성기

학습 목표:
- Step 1~2에서 배운 것을 모두 활용하기
- selectbox로 옵션 선택하기
- 프롬프트 조합하기

실행:
streamlit run app_2_3.py
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

def stream_text(text):
    """텍스트를 스트리밍처럼 출력"""
    import time
    words = text.split()
    for word in words:
        yield word + ' '
        time.sleep(0.02)

session = get_snowflake_session()

st.title("🎨 AI 콘텐츠 생성기")
st.write("원하는 콘텐츠를 AI가 만들어드립니다!")

content_type = st.selectbox(
    "콘텐츠 유형",
    ["SNS 포스트", "시/노래 가사", "광고 카피", "이메일"]
)

tone = st.selectbox(
    "톤/스타일",
    ["전문적", "유머러스", "감성적", "MZ세대"]
)

topic = st.text_input("주제를 입력하세요", placeholder="예: 월요일 아침 커피")

if topic:
    # TODO: content_type, tone, topic을 조합한 프롬프트로 스트리밍 출력하기
    # 힌트: f-string으로 세 변수를 조합한 프롬프트를 만들고
    #       complete_llm() → stream_text() → st.write_stream() 순서로 호출
    pass
