# Day 2: RAG 파이프라인 구축

**기간**: Day 11-22  
**목표**: "내 문서와 대화하는 챗봇"의 백엔드와 프론트엔드 전체 흐름 완성

---

## 🎯 학습 목표

1. **문서 처리** - PDF/TXT 업로드 및 텍스트 추출
2. **텍스트 청킹** - 효율적인 검색을 위한 분할
3. **벡터 임베딩** - Snowflake Cortex Embed로 벡터 생성
4. **유사도 검색** - 코사인 유사도 계산
5. **RAG 챗봇** - 검색된 컨텍스트로 답변 생성
6. **채팅 히스토리** - 대화 흐름 유지
7. **출처 표시** - 신뢰도 향상
8. **최종 통합** - 완성형 RAG 시스템

---

## 📚 실습 구성 (총 8개)

### Step 1: 문서 처리 (2개)
- **app_1_1.py** - 문서 업로드 (PDF/TXT)
- **app_1_2.py** - 텍스트 청킹

### Step 2: 벡터 검색 (2개)
- **app_2_1.py** - 벡터 임베딩 생성
- **app_2_2.py** - 유사도 검색 구현

### Step 3: RAG 챗봇 (2개)
- **app_3_1.py** - 기본 RAG 챗봇
- **app_3_2.py** - 스트리밍 RAG 챗봇

### Step 4: 통합 & 개선 (2개)
- **app_4_1.py** - 채팅 히스토리 추가
- **app_4_2.py** - 출처 표시 기능

---

## 🗺️ RAG 파이프라인

```
문서 업로드 → 청킹 → 벡터 임베딩 → 저장
                                        ↓
사용자 질문 → 쿼리 임베딩 → 유사도 검색 → 컨텍스트 추출
                                        ↓
                              LLM 답변 생성 → 출처 표시
```

---

## 💡 핵심 개념

### RAG (Retrieval Augmented Generation)
검색된 관련 문서를 활용하여 AI가 더 정확한 답변을 생성하는 기술

### 벡터 임베딩
```python
query = "SELECT SNOWFLAKE.CORTEX.EMBED_TEXT_768(
    'snowflake-arctic-embed-m',
    'text'
) as embedding"
```

### 코사인 유사도
```python
similarity = np.dot(vec1, vec2) / (
    np.linalg.norm(vec1) * np.linalg.norm(vec2)
)
```

### RAG 프롬프트
```python
context = "\n\n".join(retrieved_chunks)
prompt = f"다음 문서를 참고하여 답변하세요:\n\n{context}\n\n질문: {question}"
```

---

## ✅ 완료 체크리스트

- [ ] Step 1: 문서 처리 완료
- [ ] Step 2: 벡터 검색 완료
- [ ] Step 3: RAG 챗봇 완료
- [ ] Step 4: 통합 & 개선 완료

---

## 🚀 시작하기

**다음**: [Step 1 - 문서 처리] →
