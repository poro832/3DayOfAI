"""
Day 3 - Step 4: 데이터 분석 Agent

학습 목표:
- 데이터 분석 도구 구현
- 자연어 질문 → 분석 결과 변환

[참고] 이 실습은 Agent 개념 학습을 위한 '시뮬레이션'입니다.
실제 Cortex Analyst는 자연어를 SQL로 변환하여 DB를 조회합니다.

실행:
streamlit run app_4_1.py
"""

import streamlit as st
from snowflake.snowpark import Session
import pandas as pd

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

st.title("📊 데이터 분석 Agent")

# 샘플 데이터 생성
@st.cache_data
def get_sample_data():
    return pd.DataFrame({
        "제품": ["노트북", "스마트폰", "태블릿", "이어폰", "스마트워치"],
        "카테고리": ["전자기기", "전자기기", "전자기기", "액세서리", "액세서리"],
        "가격": [1500000, 1200000, 800000, 200000, 350000],
        "판매량": [150, 300, 200, 500, 180],
        "평점": [4.5, 4.8, 4.2, 4.0, 4.3]
    })

df = get_sample_data()

st.write("### 샘플 데이터")
st.dataframe(df)

# TODO: 분석 도구 정의 (get_stats, get_top_products)
# 힌트: app_1_1.py 패턴 참고, get_top_products는 by(정렬기준)와 n(개수) 파라미터 필요
tools = []  # TODO를 완성하세요

# TODO: 분석 함수 구현
def get_stats():
    """데이터 기본 통계"""
    # 힌트: df의 mean(), sum() 등을 활용하여 통계 딕셔너리 반환
    return {}  # TODO를 완성하세요

def get_top_products(by="판매량", n=3):
    """상위 제품 조회"""
    # 힌트: df.nlargest()로 상위 n개 추출
    return []  # TODO를 완성하세요

def filter_by_category(category):
    """카테고리별 필터링"""
    # 힌트: df[df["카테고리"] == category]로 필터링
    return []  # TODO를 완성하세요

st.write("### 질문 예시")
st.write("- 전체 통계 보여줘")
st.write("- 가장 많이 팔린 제품은?")
st.write("- 평점이 가장 높은 제품")
st.write("- 전자기기 카테고리만")

user_input = st.text_input("질문", "가장 많이 팔린 제품은?")

if user_input and st.button("분석"):
    with st.spinner("분석 중..."):
        # TODO: 키워드 기반 분석 수행
        # 힌트: 통계/판매/평점/카테고리 키워드에 따라 if-elif 분기
        #       각 분기에서 get_stats(), get_top_products(), filter_by_category() 호출
        #       매칭 안 되면 LLM에게 데이터와 함께 질문

        st.info("💡 TODO를 완성하세요")
