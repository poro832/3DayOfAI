# Day 2 - Step 3: RAG 챗봇

---

## 🎯 학습 목표

검색 결과를 활용하여 문서 기반 RAG 챗봇 구현

---

## 📚 실습 목록 (2개)

### app_3_1.py: 기본 RAG 챗봇

### app_3_2.py: 스트리밍 RAG 챗봇

---

## 💡 핵심 개념

- **RAG (Retrieval-Augmented Generation)**: 검색 + 생성 결합
- **컨텍스트 주입**: 검색된 청크를 프롬프트에 포함
- **프롬프트 엔지니어링**: 효과적인 답변을 위한 프롬프트 구성

---

## 📖 실습 가이드

### 실습 순서

1. **기본 RAG 챗봇** (app_3_1.py) - 검색 + LLM 응답
2. **스트리밍 RAG 챗봇** (app_3_2.py) - UX 개선

### 진행 방법

```bash
cd problems/Day2
streamlit run app_3_1.py
```

### 사전 조건

- Step 1-2 완료 (문서 업로드, 청킹, 임베딩 생성)
- `chunks.pkl`, `embeddings.pkl` 파일 존재

---

## 🎓 상세 실습 내용

### 실습 1: 기본 RAG 챗봇

**파일**: `app_3_1.py`

**목표**: 검색된 컨텍스트를 활용하여 질문에 답변하는 챗봇 구현

**RAG 파이프라인**:
```
사용자 질문 → 쿼리 임베딩 → 유사 청크 검색 → 프롬프트 구성 → LLM 응답
```

**핵심 코드**:
```python
# 프롬프트에 컨텍스트 주입
context = "\n\n".join(top_chunks)
prompt = f"""다음 문서를 참고하여 답변하세요:

[참고 문서]
{context}

[질문]
{user_question}
"""
```

**실행**:
```bash
streamlit run app_3_1.py
```

**체크포인트**:
- [ ] 쿼리 임베딩 생성 완료
- [ ] 유사 청크 검색 완료
- [ ] RAG 프롬프트 구성 완료
- [ ] LLM 응답 생성 완료

---

### 실습 2: 스트리밍 RAG 챗봇

**파일**: `app_3_2.py`

**목표**: 스트리밍 응답으로 사용자 경험 개선

**추가 기능**:
- 응답이 단어별로 출력되어 체감 속도 향상
- 로딩 스피너로 검색 중 상태 표시

**실행**:
```bash
streamlit run app_3_2.py
```

**체크포인트**:
- [ ] 스트리밍 응답 구현 완료
- [ ] 참고 문서 표시 완료

---

## ✅ 완료 체크리스트

- [ ] app_3_1.py - 기본 RAG 챗봇 완료
- [ ] app_3_2.py - 스트리밍 RAG 챗봇 완료

---

## 🔗 관련 문서

- [RAG 개념](https://docs.snowflake.com/en/user-guide/snowflake-cortex)
- [Snowflake Cortex Complete](https://docs.snowflake.com/en/sql-reference/functions/complete-snowflake-cortex)

---

**다음 단계**: [Day 2 - Step 4: 채팅 히스토리] →
