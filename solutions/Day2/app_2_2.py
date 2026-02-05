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

def escape_sql_string(text):
    """SQL 인젝션 방지를 위한 이스케이프"""
    if text is None:
        return ""
    return text.replace("'", "''").replace("\\", "\\\\")

def cosine_similarity(vec1, vec2):
    """코사인 유사도 계산"""
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

try:
    session = get_snowflake_session()
except Exception as e:
    st.error(f"Snowflake 연결 실패: {e}")
    st.stop()

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
    try:
        with st.spinner("검색 중..."):
            # SQL 인젝션 방지
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

    except Exception as e:
        st.error(f"검색 실패: {e}")
