# Day 2 - Step 4: 채팅 히스토리 & 출처 표시

---

## 🎯 학습 목표

대화 히스토리 유지 및 답변의 신뢰도를 높이는 출처 표시 기능 구현

---

## 📚 실습 목록 (2개)

### app_4_1.py: 채팅 히스토리 추가

### app_4_2.py: 출처 표시 기능

---

## 💡 핵심 개념

- **대화 히스토리**: 이전 대화를 기억하여 맥락 유지
- **출처 표시**: 답변에 사용된 문서 청크 표시
- **신뢰도 향상**: 사용자가 답변의 근거를 확인 가능

---

## 📖 실습 가이드

### 실습 순서

1. **채팅 히스토리** (app_4_1.py) - 대화 맥락 유지
2. **출처 표시** (app_4_2.py) - 참고 문서 표시

### 진행 방법

```bash
cd problems/Day2
streamlit run app_4_1.py
```

---

## 🎓 상세 실습 내용

### 실습 1: 채팅 히스토리 추가

**파일**: `app_4_1.py`

**목표**: 여러 턴의 대화를 기억하는 RAG 챗봇 구현

**핵심 구현**:
```python
# 메시지 히스토리 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []

# 이전 메시지 표시
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# 새 메시지 저장
st.session_state.messages.append({"role": "user", "content": user_input})
st.session_state.messages.append({"role": "assistant", "content": response})
```

**실행**:
```bash
streamlit run app_4_1.py
```

**체크포인트**:
- [ ] 메시지 히스토리 초기화 완료
- [ ] 이전 메시지 표시 완료
- [ ] 새 메시지 저장 완료

---

### 실습 2: 출처 표시 기능

**파일**: `app_4_2.py`

**목표**: 답변과 함께 참고한 문서 청크를 표시

**핵심 구현**:
```python
# 출처 표시
with st.expander("📄 참고 문서"):
    for i, chunk in enumerate(top_chunks):
        st.write(f"**출처 {i+1}**")
        st.write(chunk[:150] + "...")

# 메시지에 출처 정보 포함
st.session_state.messages.append({
    "role": "assistant",
    "content": response,
    "sources": top_chunks  # 출처 정보 저장
})
```

**실행**:
```bash
streamlit run app_4_2.py
```

**체크포인트**:
- [ ] 출처 표시 UI 완료
- [ ] 메시지에 출처 정보 저장 완료

---

## ✅ 완료 체크리스트

- [ ] app_4_1.py - 채팅 히스토리 완료
- [ ] app_4_2.py - 출처 표시 완료

---

## 🎉 Day 2 완료!

**Day 2에서 배운 내용**:
- 문서 업로드 및 텍스트 추출
- 텍스트 청킹 (오버랩 포함)
- 벡터 임베딩 생성
- 코사인 유사도 검색
- RAG 챗봇 구현
- 채팅 히스토리 및 출처 표시

**다음**: [Day 3 - Agent & 배포] →
