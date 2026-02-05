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

### 대화 히스토리

이전 대화를 기억하여 맥락 유지:

```python
if "messages" not in st.session_state:
    st.session_state.messages = []

# 메시지 추가
st.session_state.messages.append({"role": "user", "content": user_input})
st.session_state.messages.append({"role": "assistant", "content": response})
```

### 출처 표시

답변에 사용된 문서 청크를 함께 표시:

```python
with st.expander("📄 참고 문서"):
    for i, chunk in enumerate(top_chunks):
        st.write(f"**출처 {i+1}**")
        st.write(chunk[:150] + "...")
```

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

**핵심 코드**:
```python
import streamlit as st
import numpy as np
import pickle
import os
from snowflake.snowpark import Session

DATA_DIR = os.path.dirname(os.path.abspath(__file__))

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

st.title("💬 RAG 챗봇 with History")

# 저장된 데이터 로드
chunks_path = os.path.join(DATA_DIR, "chunks.pkl")
embeddings_path = os.path.join(DATA_DIR, "embeddings.pkl")

if os.path.exists(chunks_path):
    with open(chunks_path, "rb") as f:
        st.session_state['chunks'] = pickle.load(f)
if os.path.exists(embeddings_path):
    with open(embeddings_path, "rb") as f:
        st.session_state['embeddings'] = pickle.load(f)

if 'embeddings' not in st.session_state:
    st.warning("먼저 문서를 준비하세요")
    st.stop()

# 메시지 히스토리 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []

def cosine_similarity(vec1, vec2):
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

# 이전 메시지 표시
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

user_input = st.chat_input("질문하세요...")

if user_input:
    # 사용자 메시지 추가
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    # RAG 검색
    query_sql = f"SELECT SNOWFLAKE.CORTEX.EMBED_TEXT_768('snowflake-arctic-embed-m', '{user_input}') as embedding"
    query_emb = session.sql(query_sql).collect()[0]['EMBEDDING']

    similarities = []
    for i, emb in enumerate(st.session_state['embeddings']):
        sim = cosine_similarity(query_emb, emb)
        similarities.append((i, sim))

    similarities.sort(key=lambda x: x[1], reverse=True)
    top_chunks = [st.session_state['chunks'][idx] for idx, _ in similarities[:3]]

    context = "\n\n".join(top_chunks)
    prompt = f"""당신은 친절한 AI 어시스턴트입니다. 반드시 한국어로 짧고 간결하게 답변하세요.
다음 문서를 참고하여 답변하세요:

{context}

질문: {user_input}

답변:"""

    # AI 응답
    with st.chat_message("assistant"):
        response_stream = stream_text(complete_llm(session, "llama3.1-70b", prompt))
        response = st.write_stream(response_stream)

    st.session_state.messages.append({"role": "assistant", "content": response})
```

**체크포인트**:
- [ ] 메시지 히스토리 초기화 완료
- [ ] 이전 메시지 표시 완료
- [ ] 새 메시지 저장 완료

---

### 실습 2: 출처 표시 기능

**파일**: `app_4_2.py`

**목표**: 답변과 함께 참고한 문서 청크를 표시

**핵심 코드**:
```python
import streamlit as st
import numpy as np
import pickle
import os
from snowflake.snowpark import Session

DATA_DIR = os.path.dirname(os.path.abspath(__file__))

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

st.title("📚 출처 표시 RAG 챗봇")

# 저장된 데이터 로드
chunks_path = os.path.join(DATA_DIR, "chunks.pkl")
embeddings_path = os.path.join(DATA_DIR, "embeddings.pkl")

if os.path.exists(chunks_path):
    with open(chunks_path, "rb") as f:
        st.session_state['chunks'] = pickle.load(f)
if os.path.exists(embeddings_path):
    with open(embeddings_path, "rb") as f:
        st.session_state['embeddings'] = pickle.load(f)

if 'embeddings' not in st.session_state:
    st.warning("먼저 문서를 준비하세요")
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []

def cosine_similarity(vec1, vec2):
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

# 이전 메시지 표시 (출처 포함)
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])
        if "sources" in message:
            with st.expander("📄 참고 문서"):
                for i, source in enumerate(message["sources"]):
                    st.write(f"**출처 {i+1}**")
                    st.write(source[:150] + "...")

user_input = st.chat_input("질문하세요...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    query_sql = f"SELECT SNOWFLAKE.CORTEX.EMBED_TEXT_768('snowflake-arctic-embed-m', '{user_input}') as embedding"
    query_emb = session.sql(query_sql).collect()[0]['EMBEDDING']

    similarities = []
    for i, emb in enumerate(st.session_state['embeddings']):
        sim = cosine_similarity(query_emb, emb)
        similarities.append((i, sim))

    similarities.sort(key=lambda x: x[1], reverse=True)
    top_chunks = [st.session_state['chunks'][idx] for idx, _ in similarities[:3]]

    context = "\n\n".join(top_chunks)
    prompt = f"다음 문서를 참고하여 답변하세요:\n\n{context}\n\n질문: {user_input}"

    with st.chat_message("assistant"):
        response_stream = stream_text(complete_llm(session, "llama3.1-70b", prompt))
        response = st.write_stream(response_stream)

        # 출처 표시
        with st.expander("📄 참고 문서"):
            for i, chunk in enumerate(top_chunks):
                st.write(f"**출처 {i+1}**")
                st.write(chunk[:150] + "...")

    # 출처 정보와 함께 메시지 저장
    st.session_state.messages.append({
        "role": "assistant",
        "content": response,
        "sources": top_chunks
    })
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
