"""
Day 2 - Step 2-2: 유사도 검색 (정답)
"""

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
    """SQL 방식으로 Cortex LLM 호출"""
    escaped_prompt = prompt.replace("'", "''")
    sql = f"SELECT SNOWFLAKE.CORTEX.COMPLETE('{model}', '{escaped_prompt}')"
    result = session.sql(sql).collect()
    return result[0][0]


session = get_snowflake_session()

st.title("🔍 유사도 검색")

# 코사인 유사도 설명
with st.expander("💡 코사인 유사도(Cosine Similarity)란?", expanded=True):
    st.markdown("""
    **코사인 유사도**: 두 벡터가 얼마나 같은 방향을 가리키는지 측정
    - 값 범위: -1 ~ 1 (보통 0 ~ 1)
    - **1에 가까울수록** 두 텍스트의 의미가 비슷함
    - **0에 가까울수록** 관련이 없음

    **작동 원리:**
    ```
    질문: "코끼리 특징"  →  벡터 A: [0.2, 0.8, ...]
    청크1: "코끼리는 큰 동물..." →  벡터 B: [0.3, 0.7, ...]  → 유사도: 0.95 ✓
    청크2: "펭귄은 남극에..."  →  벡터 C: [0.9, 0.1, ...]  → 유사도: 0.23 ✗
    ```

    **키워드 검색과 차이점:**
    - 키워드 검색: "코끼리"라는 **단어**가 있어야 찾음
    - 유사도 검색: "코끼리"가 없어도 **의미**가 비슷하면 찾음
      - 예: "큰 포유류", "상아를 가진 동물" 등도 매칭 가능
    """)

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
    st.warning("먼저 임베딩을 생성하세요")
    st.stop()

# 코사인 유사도 함수
def cosine_similarity(vec1, vec2):
    """두 벡터의 코사인 유사도 계산"""
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

# 예시 질문 (sample_data/animals.txt 사용 시)
st.info("💡 예시 질문: 사자, 코끼리 특징, 펭귄 먹이, 가장 빠른 동물")

user_query = st.text_input("검색어 입력", placeholder="예: 코끼리는 하루에 물을 얼마나 마셔?")

if user_query and st.button("검색"):
    with st.spinner("검색 중..."):
        # 쿼리 임베딩 생성
        query_sql = f"SELECT SNOWFLAKE.CORTEX.EMBED_TEXT_768('snowflake-arctic-embed-m', '{user_query}') as embedding"
        query_emb = session.sql(query_sql).collect()[0]['EMBEDDING']

        # 각 청크와 유사도 계산
        similarities = []
        for i, emb in enumerate(st.session_state['embeddings']):
            sim = cosine_similarity(query_emb, emb)
            similarities.append((i, sim))

        # 유사도 높은 순으로 정렬 후 상위 3개 표시
        similarities.sort(key=lambda x: x[1], reverse=True)

    st.write("### 검색 결과")
    for i, (idx, sim) in enumerate(similarities[:3]):
        st.write(f"**{i+1}. 유사도: {sim:.3f}**")
        st.write(st.session_state['chunks'][idx][:200] + "...")
        st.write("---")
