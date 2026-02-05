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

### RAG (Retrieval-Augmented Generation)

> **비전공자를 위한 설명**
> - AI는 학습한 내용만 알고 있어서, 우리 회사 문서 내용은 모릅니다
> - RAG는 "질문과 관련된 문서를 먼저 찾아서 AI에게 알려주는" 방식입니다
> - 마치 오픈북 시험처럼, AI가 참고자료를 보고 답변합니다!

검색과 생성을 결합한 방식:

```
1. 사용자 질문 → 2. 질문을 벡터로 변환 → 3. 유사한 문서 검색
                                              ↓
4. LLM이 답변 생성 ← 5. 찾은 문서를 프롬프트에 포함
```

### RAG 프롬프트 구성

```python
context = "\n\n".join(top_chunks)
prompt = f"""다음 문서를 참고하여 질문에 답변하세요.

[참고 문서]
{context}

[질문]
{user_question}

[답변]"""
```

---

## 📖 실습 가이드

### 실습 순서

1. **기본 RAG 챗봇** (app_3_1.py) - 검색 + LLM 응답
2. **스트리밍 RAG 챗봇** (app_3_2.py) - UX 개선

### 사전 조건

- Step 1-2 완료 (`chunks.pkl`, `embeddings.pkl` 파일 필요)

### 진행 방법

```bash
cd problems/Day2
streamlit run app_3_1.py
```

---

## 🎓 상세 실습 내용

### 실습 1: 기본 RAG 챗봇

**파일**: `app_3_1.py`

**목표**: 검색된 컨텍스트를 활용하여 질문에 답변하는 챗봇 구현

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

def escape_sql_string(text):
    if text is None:
        return ""
    return text.replace("'", "''").replace("\\", "\\\\")

def cosine_similarity(vec1, vec2):
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

session = get_snowflake_session()

st.title("🤖 RAG 챗봇")

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
    st.warning("먼저 문서를 준비하세요 (app_1_1 ~ app_2_1 실행)")
    st.stop()

user_question = st.text_input("질문하세요")

if user_question:
    with st.spinner("답변 생성 중..."):
        # 1. 쿼리 임베딩
        safe_question = escape_sql_string(user_question)
        query_sql = f"SELECT SNOWFLAKE.CORTEX.EMBED_TEXT_768('snowflake-arctic-embed-m', '{safe_question}') as embedding"
        query_emb = session.sql(query_sql).collect()[0]['EMBEDDING']

        # 2. 유사 청크 찾기
        similarities = []
        for i, emb in enumerate(st.session_state['embeddings']):
            sim = cosine_similarity(query_emb, emb)
            similarities.append((i, sim))

        similarities.sort(key=lambda x: x[1], reverse=True)
        top_chunks = [st.session_state['chunks'][idx] for idx, _ in similarities[:3]]

        # 3. RAG 프롬프트 생성
        context = "\n\n".join(top_chunks)
        prompt = f"""당신은 친절한 AI 어시스턴트입니다. 반드시 한국어로 답변하세요.
다음 문서를 참고하여 질문에 답변하세요.

[참고 문서]
{context}

[질문]
{user_question}

[답변]"""

        # 4. LLM 답변 생성
        response = complete_llm(session, "llama3.1-70b", prompt)

    st.write("### 답변")
    st.write(response)

    with st.expander("📄 참고한 문서"):
        for i, chunk in enumerate(top_chunks):
            st.write(f"**문서 {i+1}**")
            st.write(chunk[:200] + "..." if len(chunk) > 200 else chunk)
            st.divider()
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

def escape_sql_string(text):
    if text is None:
        return ""
    return text.replace("'", "''").replace("\\", "\\\\")

def cosine_similarity(vec1, vec2):
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

session = get_snowflake_session()

st.title("💬 스트리밍 RAG 챗봇")

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
    st.warning("먼저 문서를 준비하세요 (app_1_1 ~ app_2_1 실행)")
    st.stop()

user_question = st.text_input("질문하세요")

if user_question:
    safe_question = escape_sql_string(user_question)
    query_sql = f"SELECT SNOWFLAKE.CORTEX.EMBED_TEXT_768('snowflake-arctic-embed-m', '{safe_question}') as embedding"

    with st.spinner("관련 문서 검색 중..."):
        query_emb = session.sql(query_sql).collect()[0]['EMBEDDING']

        similarities = []
        for i, emb in enumerate(st.session_state['embeddings']):
            sim = cosine_similarity(query_emb, emb)
            similarities.append((i, sim))

        similarities.sort(key=lambda x: x[1], reverse=True)
        top_chunks = [st.session_state['chunks'][idx] for idx, _ in similarities[:3]]

    context = "\n\n".join(top_chunks)
    prompt = f"""다음 문서를 참고하여 질문에 답변하세요.

[참고 문서]
{context}

[질문]
{user_question}

[답변]"""

    # 스트리밍 응답
    st.write("### 답변")
    response_stream = stream_text(complete_llm(session, "llama3.1-70b", prompt))
    st.write_stream(response_stream)

    with st.expander("📄 참고한 문서"):
        for i, chunk in enumerate(top_chunks):
            st.write(f"**문서 {i+1}**")
            st.write(chunk[:200] + "..." if len(chunk) > 200 else chunk)
            st.divider()
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
