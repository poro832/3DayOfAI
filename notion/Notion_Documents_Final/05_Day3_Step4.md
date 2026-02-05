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

**샘플 데이터**:
```
| 제품 | 카테고리 | 가격 | 판매량 | 평점 |
|------|----------|------|--------|------|
| 노트북 | 전자기기 | 1,500,000 | 150 | 4.5 |
| 스마트폰 | 전자기기 | 1,200,000 | 300 | 4.8 |
| 태블릿 | 전자기기 | 800,000 | 200 | 4.2 |
| 이어폰 | 액세서리 | 200,000 | 500 | 4.0 |
| 스마트워치 | 액세서리 | 350,000 | 180 | 4.3 |
```

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
