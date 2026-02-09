"""
Step 2-3: AI 콘텐츠 생성기 (정답)

Step 1~2에서 배운 것을 모두 활용하는 통합 실습!
- Snowflake 연결
- LLM 호출
- 스트리밍 출력
- 캐싱
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

# 콘텐츠 유형 선택
content_type = st.selectbox(
    "콘텐츠 유형",
    ["SNS 포스트", "시/노래 가사", "광고 카피", "이메일"]
)

# 톤/스타일 선택
tone = st.selectbox(
    "톤/스타일",
    ["전문적", "유머러스", "감성적", "MZ세대"]
)

# 주제 입력
topic = st.text_input("주제를 입력하세요", placeholder="예: 월요일 아침 커피")

if topic and st.button("✨ 생성하기"):
    # 프롬프트 조합
    prompt = f"""다음 조건에 맞는 {content_type}를 작성해주세요.

톤/스타일: {tone}
주제: {topic}

한국어로 작성하고, 해당 콘텐츠 유형에 맞는 형식으로 작성해주세요."""

    st.write("### 생성 결과")
    with st.spinner("생성 중..."):
        response = complete_llm(session, "llama3.1-70b", prompt)
    st.write_stream(stream_text(response))
