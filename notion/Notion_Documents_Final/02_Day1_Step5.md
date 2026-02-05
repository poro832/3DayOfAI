# Day 1 - Step 5: 완성형 챗봇

---

## 🎯 학습 목표

전체 대화 컨텍스트를 유지하는 완성형 챗봇

---

## 📚 실습 목록 (2개)

### app_5_1.py: 컨텍스트 챗봇 구현

### app_5_2.py: 시스템 프롬프트 추가

---

## 💡 핵심 개념

### 대화 컨텍스트

이전 대화 내용을 LLM에게 전달하여 맥락 유지:

```python
# 대화 히스토리를 문자열로 변환
conversation_history = "\n".join([
    f"{'사용자' if msg['role'] == 'user' else 'AI'}: {msg['content']}"
    for msg in st.session_state.messages
])

# 프롬프트에 포함
full_prompt = f"""[대화 내용]
{conversation_history}

AI:"""
```

### 시스템 프롬프트

AI의 역할과 응답 스타일을 지정:

```python
SYSTEM_PROMPT = "당신은 친절한 AI 어시스턴트입니다. 반드시 한국어로 짧고 간결하게 답변하세요."
```

---

## 📖 실습 가이드

### 진행 방법

```bash
cd problems/Day1
streamlit run app_5_1.py
```

---

## 🎓 상세 실습 내용

### 실습 1: 컨텍스트 챗봇 구현

**파일**: `app_5_1.py`

**목표**: 이전 대화를 기억하는 챗봇 구현

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

def stream_text(text):
    import time
    words = text.split()
    for word in words:
        yield word + ' '
        time.sleep(0.02)

session = get_snowflake_session()

st.title("🧠 컨텍스트 챗봇")

SYSTEM_PROMPT = "당신은 한국어 AI 어시스턴트입니다. 오직 질문에 대한 답변만 한국어로 출력하세요."

if "messages" not in st.session_state:
    st.session_state.messages = []

# 이전 메시지 표시
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

user_input = st.chat_input("메시지를 입력하세요...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    # 대화 히스토리를 프롬프트로 구성
    conversation_history = "\n".join([
        f"{'사용자' if msg['role'] == 'user' else 'AI'}: {msg['content']}"
        for msg in st.session_state.messages
    ])

    full_prompt = f"""[시스템 지시사항]
{SYSTEM_PROMPT}

[대화 내용]
{conversation_history}

AI:"""

    with st.chat_message("assistant"):
        ai_response_stream = stream_text(complete_llm(session, "llama3.1-70b", full_prompt))
        ai_response = st.write_stream(ai_response_stream)

    st.session_state.messages.append({"role": "assistant", "content": ai_response})
```

**체크포인트**:
- [ ] 대화 히스토리 문자열 구성 완료
- [ ] 스트리밍 응답 구현 완료
- [ ] 컨텍스트 유지 테스트 완료

---

### 실습 2: 시스템 프롬프트 추가

**파일**: `app_5_2.py`

**목표**: 사이드바에서 시스템 프롬프트 편집 및 대화 초기화 기능 추가

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

def stream_text(text):
    import time
    words = text.split()
    for word in words:
        yield word + ' '
        time.sleep(0.02)

session = get_snowflake_session()

st.title("🎯 완성형 챗봇")

DEFAULT_SYSTEM_PROMPT = "당신은 친절한 AI 어시스턴트입니다. 반드시 한국어로 짧고 간결하게 답변하세요."

if "messages" not in st.session_state:
    st.session_state.messages = []

if "system_prompt" not in st.session_state:
    st.session_state.system_prompt = DEFAULT_SYSTEM_PROMPT

# 사이드바 설정
with st.sidebar:
    st.write("### ⚙️ 설정")

    new_prompt = st.text_area(
        "시스템 프롬프트",
        value=st.session_state.system_prompt,
        height=100
    )
    if new_prompt != st.session_state.system_prompt:
        st.session_state.system_prompt = new_prompt

    st.divider()

    st.write("### 💬 대화 관리")

    if st.button("대화 초기화"):
        st.session_state.messages = []
        st.rerun()

    msg_count = len(st.session_state.messages)
    st.write(f"메시지 수: {msg_count}개")

# 이전 메시지 표시
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

user_input = st.chat_input("메시지를 입력하세요...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    conversation_history = "\n".join([
        f"{'사용자' if msg['role'] == 'user' else 'AI'}: {msg['content']}"
        for msg in st.session_state.messages
    ])

    full_prompt = f"""[시스템 지시사항]
{st.session_state.system_prompt}

[대화 내용]
{conversation_history}

AI:"""

    with st.chat_message("assistant"):
        ai_response_stream = stream_text(complete_llm(session, "llama3.1-70b", full_prompt))
        ai_response = st.write_stream(ai_response_stream)

    st.session_state.messages.append({"role": "assistant", "content": ai_response})
```

**체크포인트**:
- [ ] 시스템 프롬프트 편집 기능 완료
- [ ] 대화 초기화 기능 완료
- [ ] 메시지 수 표시 완료

---

## ✅ 완료 체크리스트

- [ ] app_5_1.py - 컨텍스트 챗봇 구현 완료
- [ ] app_5_2.py - 시스템 프롬프트 추가 완료

---

## 🎉 Day 1 완료!

**Day 1에서 배운 내용**:
- Snowflake 연결 및 LLM 호출
- 스트리밍 응답 및 캐싱
- Streamlit 위젯 활용
- 세션 상태 관리
- 채팅 UI 구현
- 컨텍스트 유지 챗봇

---

**다음**: [Day 2 - RAG 파이프라인] →
