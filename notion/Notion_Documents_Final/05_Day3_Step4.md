# Day 3 - Step 4: 데이터 분석 Agent

---

## 🎯 학습 목표

자연어 질문을 데이터 분석 결과로 변환하는 Agent 구현

---

## 📚 실습 목록 (1개)

### app_4_1.py: 데이터 분석 Agent

---

## 💡 핵심 개념

### 데이터 분석 도구

```python
tools = [
    {"function": {"name": "get_stats", "description": "데이터 통계를 반환"}},
    {"function": {"name": "get_top_products", "description": "상위 제품 반환"}},
    {"function": {"name": "filter_by_category", "description": "카테고리별 필터링"}}
]
```

### 분석 함수 예시

```python
def get_stats():
    return {
        "총 제품 수": len(df),
        "평균 가격": f"{df['가격'].mean():,.0f}원",
        "총 판매량": f"{df['판매량'].sum():,}개"
    }

def get_top_products(by="판매량", n=3):
    return df.nlargest(n, by)[["제품", by]].to_dict("records")
```

---

## ⚠️ 참고 사항

| 이 실습 | 실제 Cortex Analyst |
|---------|---------------------|
| 하드코딩된 샘플 DataFrame | 실제 Snowflake 테이블 |
| 키워드 기반 분석 | 자연어 → SQL 변환 |

실제 Cortex Analyst: [공식 문서](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-analyst)

---

## 📖 실습 가이드

### 진행 방법

```bash
cd problems/Day3
streamlit run app_4_1.py
```

---

## 🎓 상세 실습 내용

### 실습: 데이터 분석 Agent

**파일**: `app_4_1.py`

**핵심 코드**:
```python
import streamlit as st
from snowflake.snowpark import Session
import pandas as pd

def get_snowflake_session():
    connection_parameters = st.secrets["connections"]["snowflake"]
    return Session.builder.configs(connection_parameters).create()

def complete_llm(session, model, prompt):
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

# 분석 도구 정의
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_stats",
            "description": "데이터 통계를 반환합니다",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_top_products",
            "description": "상위 제품을 반환합니다",
            "parameters": {
                "type": "object",
                "properties": {
                    "by": {"type": "string", "description": "정렬 기준"},
                    "n": {"type": "integer", "description": "개수"}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "filter_by_category",
            "description": "카테고리별 필터링",
            "parameters": {
                "type": "object",
                "properties": {
                    "category": {"type": "string", "description": "카테고리명"}
                }
            }
        }
    }
]

def get_stats():
    return {
        "총 제품 수": len(df),
        "평균 가격": f"{df['가격'].mean():,.0f}원",
        "총 판매량": f"{df['판매량'].sum():,}개",
        "평균 평점": f"{df['평점'].mean():.1f}점"
    }

def get_top_products(by="판매량", n=3):
    return df.nlargest(n, by)[["제품", by]].to_dict("records")

def filter_by_category(category):
    filtered = df[df["카테고리"] == category]
    return filtered.to_dict("records")

st.write("### 질문 예시")
st.write("- 전체 통계 보여줘")
st.write("- 가장 많이 팔린 제품은?")
st.write("- 평점이 가장 높은 제품 3개")
st.write("- 전자기기 카테고리만 보여줘")

user_input = st.text_input("질문", "가장 많이 팔린 제품은?")

if user_input and st.button("분석"):
    with st.spinner("분석 중..."):
        # 키워드 기반 도구 선택
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

        elif any(word in user_input for word in ["가격", "비싼", "저렴"]):
            if "저렴" in user_input:
                result = df.nsmallest(3, "가격")[["제품", "가격"]]
            else:
                result = df.nlargest(3, "가격")[["제품", "가격"]]
            st.write("### 💰 가격순")
            st.dataframe(result)

        elif "전자기기" in user_input:
            filtered = filter_by_category("전자기기")
            st.write("### 🖥️ 전자기기 카테고리")
            st.dataframe(pd.DataFrame(filtered))

        elif "액세서리" in user_input:
            filtered = filter_by_category("액세서리")
            st.write("### 🎧 액세서리 카테고리")
            st.dataframe(pd.DataFrame(filtered))

        else:
            data_desc = df.to_string()
            prompt = f"다음 데이터를 참고하여 질문에 답변하세요:\n\n{data_desc}\n\n질문: {user_input}"
            response = complete_llm(session, "llama3.1-70b", prompt)
            st.write("### 답변")
            st.write(response)
```

**샘플 데이터**:
| 제품 | 카테고리 | 가격 | 판매량 | 평점 |
|------|----------|------|--------|------|
| 노트북 | 전자기기 | 1,500,000 | 150 | 4.5 |
| 스마트폰 | 전자기기 | 1,200,000 | 300 | 4.8 |
| 태블릿 | 전자기기 | 800,000 | 200 | 4.2 |
| 이어폰 | 액세서리 | 200,000 | 500 | 4.0 |
| 스마트워치 | 액세서리 | 350,000 | 180 | 4.3 |

**테스트 질문**:
- "전체 통계 보여줘" → 통계 요약
- "가장 많이 팔린 제품은?" → 판매량 TOP 3
- "평점이 가장 높은 제품 3개" → 평점 TOP 3
- "전자기기 카테고리만 보여줘" → 필터링 결과

**체크포인트**:
- [ ] 샘플 데이터 로드 완료
- [ ] 분석 도구 정의 완료
- [ ] 자연어 → 분석 결과 변환 완료

---

## ✅ 완료 체크리스트

- [ ] app_4_1.py - 데이터 분석 Agent 완료

---

**다음 단계**: [Day 3 - Step 5: 배포 준비] →
