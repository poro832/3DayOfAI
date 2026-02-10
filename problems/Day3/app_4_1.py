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

# 분석 함수 구현
def get_stats():
    """데이터 기본 통계"""
    return {
        "총 제품 수": len(df),
        "평균 가격": f"{df['가격'].mean():,.0f}원",
        "총 판매량": f"{df['판매량'].sum():,}개",
        "평균 평점": f"{df['평점'].mean():.1f}점"
    }

def get_top_products(by="판매량", n=3):
    """상위 제품 조회"""
    # TODO: 상위 n개 추출 (1줄)
    # 힌트: df.nlargest(n, by)[["제품", by]].to_dict("records")
    return []  # TODO를 완성하세요

def filter_by_category(category):
    """카테고리별 필터링"""
    return df[df["카테고리"] == category].to_dict("records")

st.write("### 질문 예시")
st.write("- 전체 통계 보여줘")
st.write("- 가장 많이 팔린 제품은?")
st.write("- 평점이 가장 높은 제품")
st.write("- 전자기기 카테고리만")

user_input = st.text_input("질문", "가장 많이 팔린 제품은?")

if user_input and st.button("분석"):
    with st.spinner("분석 중..."):
        if any(word in user_input for word in ["통계", "전체", "요약"]):
            stats = get_stats()
            st.write("### 📈 데이터 통계")
            for key, value in stats.items():
                st.write(f"- **{key}**: {value}")

        elif any(word in user_input for word in ["많이", "판매", "인기"]):
            top = get_top_products(by="판매량", n=3)
            st.write("### 🏆 판매량 TOP 3")
            for i, item in enumerate(top, 1):
                st.write(f"{i}. **{item['제품']}** - {item['판매량']:,}개")

        elif any(word in user_input for word in ["평점", "높은", "좋은"]):
            top = get_top_products(by="평점", n=3)
            st.write("### ⭐ 평점 TOP 3")
            for i, item in enumerate(top, 1):
                st.write(f"{i}. **{item['제품']}** - {item['평점']}점")

        elif "전자기기" in user_input or "액세서리" in user_input:
            category = "전자기기" if "전자기기" in user_input else "액세서리"
            filtered = filter_by_category(category)
            st.write(f"### 📋 {category} 카테고리")
            st.dataframe(pd.DataFrame(filtered))

        else:
            data_desc = df.to_string()
            prompt = f"다음 데이터를 참고하여 질문에 답변하세요:\n\n{data_desc}\n\n질문: {user_input}"
            response = complete_llm(session, "llama3.1-70b", prompt)
            st.write(response)
