"""
Day 3 - Step 4: 데이터 분석 Agent

학습 목표:
- CSV 데이터 분석 도구 구현
- 데이터 기반 질의응답

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

# TODO: 분석 도구 정의
# 힌트: tools = [
#     {
#         "type": "function",
#         "function": {
#             "name": "get_stats",
#             "description": "데이터 통계를 반환합니다",
#             "parameters": {"type": "object", "properties": {}}
#         }
#     },
#     {
#         "type": "function",
#         "function": {
#             "name": "get_top_products",
#             "description": "상위 제품을 반환합니다",
#             "parameters": {
#                 "type": "object",
#                 "properties": {
#                     "by": {"type": "string", "description": "정렬 기준 (판매량/가격/평점)"},
#                     "n": {"type": "integer", "description": "개수"}
#                 }
#             }
#         }
#     }
# ]
tools = []  # TODO를 완성하세요

# TODO: 분석 함수 구현
def get_stats():
    """데이터 기본 통계"""
    # 힌트: 평균 가격, 총 판매량, 평균 평점 등 반환
    pass

def get_top_products(by="판매량", n=3):
    """상위 제품 조회"""
    # 힌트: df.nlargest(n, by) 사용
    pass

def filter_by_category(category):
    """카테고리별 필터링"""
    # 힌트: df[df["카테고리"] == category]
    pass

user_input = st.text_input("질문", "가장 많이 팔린 제품은?")

if user_input and st.button("분석"):
    # TODO: 질문에 따라 적절한 분석 수행
    # 힌트: 키워드 기반으로 도구 선택

    st.info("💡 TODO를 완성하세요")
