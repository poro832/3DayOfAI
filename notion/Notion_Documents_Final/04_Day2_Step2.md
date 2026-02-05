# Day 2 - Step 2: 벡터 검색

---

## 🎯 학습 목표

텍스트를 벡터로 변환하고 유사한 청크 찾기

---

## 📚 실습 목록 (2개)

### app_2_1.py: 벡터 임베딩 생성

### app_2_2.py: 유사도 검색 구현

---

## 💡 핵심 개념

### 벡터 임베딩이란?

> **비전공자를 위한 설명**
> - 컴퓨터는 "사과"와 "배"가 비슷한 과일인지 모릅니다
> - 하지만 "사과" → [0.1, 0.8, 0.3, ...], "배" → [0.2, 0.7, 0.4, ...] 처럼 숫자로 바꾸면 비교 가능!
> - 비슷한 의미의 단어는 비슷한 숫자 배열(벡터)이 됩니다

텍스트를 768차원 벡터로 변환:

```python
query = f"""
SELECT SNOWFLAKE.CORTEX.EMBED_TEXT_768(
    'snowflake-arctic-embed-m',
    '{safe_text}'
) as embedding
"""
result = session.sql(query).collect()
embedding = result[0]['EMBEDDING']
```

### 코사인 유사도

두 벡터 간의 유사도 계산:

```python
import numpy as np

def cosine_similarity(vec1, vec2):
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
```

### SQL 인젝션 방지

```python
def escape_sql_string(text):
    if text is None:
        return ""
    return text.replace("'", "''").replace("\\", "\\\\")
```

---

## 📖 실습 가이드

### 실습 순서

1. **벡터 임베딩 생성** (app_2_1.py) → `embeddings.pkl` 생성
2. **유사도 검색** (app_2_2.py) → 검색 기능 구현

### 사전 조건

- Step 1 완료 (`chunks.pkl` 파일 필요)

### 진행 방법

```bash
cd problems/Day2
streamlit run app_2_1.py
```

---

## 🎓 상세 실습 내용

### 실습 1: 벡터 임베딩 생성

**파일**: `app_2_1.py`

**목표**: 모든 청크를 벡터로 변환

**핵심 코드**:
```python
import streamlit as st
import pickle
import os
from snowflake.snowpark import Session

DATA_DIR = os.path.dirname(os.path.abspath(__file__))

def get_snowflake_session():
    connection_parameters = st.secrets["connections"]["snowflake"]
    return Session.builder.configs(connection_parameters).create()

def escape_sql_string(text):
    """SQL 인젝션 방지를 위한 이스케이프"""
    if text is None:
        return ""
    return text.replace("'", "''").replace("\\", "\\\\")

session = get_snowflake_session()

st.title("🔢 벡터 임베딩")

# 저장된 청크 로드
chunks_path = os.path.join(DATA_DIR, "chunks.pkl")
if os.path.exists(chunks_path):
    with open(chunks_path, "rb") as f:
        st.session_state['chunks'] = pickle.load(f)

if 'chunks' not in st.session_state:
    st.warning("먼저 텍스트를 청킹하세요 (app_1_2.py)")
    st.stop()

chunks = st.session_state['chunks']
st.write(f"청크 개수: {len(chunks)}개")

if st.button("임베딩 생성"):
    embeddings = []
    progress_bar = st.progress(0)
    status_text = st.empty()

    for i, chunk in enumerate(chunks):
        status_text.text(f"임베딩 생성 중... ({i+1}/{len(chunks)})")

        safe_chunk = escape_sql_string(chunk)
        query = f"""
        SELECT SNOWFLAKE.CORTEX.EMBED_TEXT_768(
            'snowflake-arctic-embed-m',
            '{safe_chunk}'
        ) as embedding
        """
        result = session.sql(query).collect()
        embeddings.append(result[0]['EMBEDDING'])

        progress_bar.progress((i + 1) / len(chunks))

    st.session_state['embeddings'] = embeddings

    # 파일로 저장
    with open(os.path.join(DATA_DIR, "embeddings.pkl"), "wb") as f:
        pickle.dump(embeddings, f)

    status_text.empty()
    st.success(f"✅ {len(embeddings)}개 임베딩 생성 완료!")
    st.write(f"벡터 차원: {len(embeddings[0])}")
```

**체크포인트**:
- [ ] EMBED_TEXT_768 SQL 호출 완료
- [ ] 진행률 표시 완료
- [ ] embeddings.pkl 저장 완료

---

### 실습 2: 유사도 검색 구현

**파일**: `app_2_2.py`

**목표**: 검색어와 유사한 청크 찾기

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

def escape_sql_string(text):
    if text is None:
        return ""
    return text.replace("'", "''").replace("\\", "\\\\")

def cosine_similarity(vec1, vec2):
    """코사인 유사도 계산"""
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

session = get_snowflake_session()

st.title("🔍 유사도 검색")

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
    st.warning("먼저 임베딩을 생성하세요 (app_2_1.py)")
    st.stop()

user_query = st.text_input("검색어 입력")

if user_query and st.button("검색"):
    with st.spinner("검색 중..."):
        # 쿼리 임베딩 생성
        safe_query = escape_sql_string(user_query)
        query_sql = f"""
        SELECT SNOWFLAKE.CORTEX.EMBED_TEXT_768(
            'snowflake-arctic-embed-m',
            '{safe_query}'
        ) as embedding
        """
        query_embedding = session.sql(query_sql).collect()[0]['EMBEDDING']

        # 유사도 계산
        similarities = []
        for i, emb in enumerate(st.session_state['embeddings']):
            sim = cosine_similarity(query_embedding, emb)
            similarities.append((i, sim))

        # 정렬
        similarities.sort(key=lambda x: x[1], reverse=True)

        # 상위 3개 표시
        st.write("### 검색 결과")
        for i, (idx, sim) in enumerate(similarities[:3]):
            st.write(f"**{i+1}. 유사도: {sim:.3f}**")
            chunk_text = st.session_state['chunks'][idx]
            st.write(chunk_text[:200] + "..." if len(chunk_text) > 200 else chunk_text)
            st.write("---")
```

**체크포인트**:
- [ ] 쿼리 임베딩 생성 완료
- [ ] 코사인 유사도 계산 완료
- [ ] 상위 결과 표시 완료

---

## ✅ 완료 체크리스트

- [ ] app_2_1.py - 벡터 임베딩 생성 완료
- [ ] app_2_2.py - 유사도 검색 구현 완료

---

## 🔗 관련 문서

- [NumPy Documentation](https://numpy.org/doc/)
- [Snowflake Cortex Embed](https://docs.snowflake.com/en/user-guide/snowflake-cortex/embed)

---

**다음 단계**: [Day 2 - Step 3: RAG 챗봇] →
