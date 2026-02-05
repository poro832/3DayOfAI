"""
Day 2 - Step 3-2: 스트리밍 RAG 챗봇 (정답)
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

def stream_text(text):
    """텍스트를 스트리밍처럼 출력"""
    import time
    words = text.split()
    for word in words:
        yield word + ' '
        time.sleep(0.02)


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
    try:
        # 1. 쿼리 임베딩 (SQL 인젝션 방지)
        safe_question = escape_sql_string(user_question)
        query_sql = f"SELECT SNOWFLAKE.CORTEX.EMBED_TEXT_768('snowflake-arctic-embed-m', '{safe_question}') as embedding"

        with st.spinner("관련 문서 검색 중..."):
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
        prompt = f"""다음 문서를 참고하여 질문에 답변하세요.

[참고 문서]
{context}

[질문]
{user_question}

[답변]"""

        # 4. 스트리밍 응답
        st.write("### 답변")
        response_stream = stream_text(complete_llm(session, "llama3.1-70b", prompt))
        st.write_stream(response_stream)

        with st.expander("📄 참고한 문서"):
            for i, chunk in enumerate(top_chunks):
                st.write(f"**문서 {i+1}**")
                st.write(chunk[:200] + "..." if len(chunk) > 200 else chunk)
                st.divider()

    except Exception as e:
        st.error(f"오류 발생: {e}")
