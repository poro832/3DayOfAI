# Day 1 - Step 4: 세션 상태 & 채팅 UI

---

## 🎯 학습 목표

대화 히스토리를 유지하는 채팅 인터페이스 구현

---

## 📚 실습 목록 (2개)

### app_4_1.py: 세션 상태 기초

### app_4_2.py: 채팅 UI 만들기

---

## 💡 핵심 개념

### st.session_state

페이지 새로고침 시에도 데이터를 유지:

```python
# 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []

# 추가
st.session_state.messages.append({"role": "user", "content": text})

# 삭제
st.session_state.messages = []
```

### 채팅 UI 컴포넌트

```python
# 채팅 메시지 표시
with st.chat_message("user"):
    st.write("사용자 메시지")

with st.chat_message("assistant"):
    st.write("AI 응답")

# 채팅 입력
user_input = st.chat_input("메시지를 입력하세요...")
```

---

## 📖 실습 가이드

### 진행 방법

```bash
cd problems/Day1
streamlit run app_4_1.py
```

---

## 🎓 상세 실습 내용

### 실습 1: 세션 상태 기초

**파일**: `app_4_1.py`

**목표**: 세션 상태로 메시지 목록 관리

**핵심 코드**:
```python
import streamlit as st

st.title("💾 세션 상태 기초")

# 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []

st.write(f"### 저장된 메시지: {len(st.session_state.messages)}개")

# 메시지 추가
new_message = st.text_input("새 메시지를 입력하세요")

if st.button("추가") and new_message:
    st.session_state.messages.append(new_message)
    st.rerun()

# 메시지 표시
for i, msg in enumerate(st.session_state.messages):
    st.write(f"{i+1}. {msg}")

# 메시지 삭제
if st.button("모두 삭제"):
    st.session_state.messages = []
    st.rerun()
```

**체크포인트**:
- [ ] st.session_state 초기화 완료
- [ ] 메시지 추가 기능 완료
- [ ] 메시지 삭제 기능 완료

---

### 실습 2: 채팅 UI 만들기

**파일**: `app_4_2.py`

**목표**: st.chat_message와 st.chat_input으로 채팅 UI 구현

**핵심 코드**:
```python
import streamlit as st
from snowflake.snowpark import Session

@st.cache_resource
def get_snowflake_session():
    connection_parameters = st.secrets["connections"]["snowflake"]
    return Session.builder.configs(connection_parameters).create()

def complete_llm(session, model, prompt):
    escaped_prompt = prompt.replace("'", "''")
    sql = f"SELECT SNOWFLAKE.CORTEX.COMPLETE('{model}', '{escaped_prompt}')"
    result = session.sql(sql).collect()
    return result[0][0]

session = get_snowflake_session()

st.title("💬 채팅 UI")

# 시스템 프롬프트
SYSTEM_PROMPT = "당신은 친절한 AI 어시스턴트입니다. 반드시 한국어로 짧고 간결하게 답변하세요."

# 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []

# 이전 메시지 표시
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# 사용자 입력
user_input = st.chat_input("메시지를 입력하세요...")

if user_input:
    # 사용자 메시지 저장 및 표시
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    # 프롬프트 구성
    full_prompt = f"""[시스템 지시사항]
{SYSTEM_PROMPT}

[사용자 질문]
{user_input}

AI:"""

    # AI 응답
    with st.spinner("생각하는 중..."):
        ai_response = complete_llm(session, "llama3.1-70b", full_prompt)

    # AI 메시지 저장 및 표시
    st.session_state.messages.append({"role": "assistant", "content": ai_response})
    with st.chat_message("assistant"):
        st.write(ai_response)
```

**체크포인트**:
- [ ] st.chat_message() 사용 완료
- [ ] st.chat_input() 사용 완료
- [ ] 메시지 히스토리 저장 완료

---

## ✅ 완료 체크리스트

- [ ] app_4_1.py - 세션 상태 기초 완료
- [ ] app_4_2.py - 채팅 UI 만들기 완료

---

## 🔗 관련 문서

- [Streamlit Session State](https://docs.streamlit.io/library/api-reference/session-state)
- [Streamlit Chat Elements](https://docs.streamlit.io/library/api-reference/chat)

---

**다음 단계**: [Day 1 - Step 5: 완성형 챗봇] →
