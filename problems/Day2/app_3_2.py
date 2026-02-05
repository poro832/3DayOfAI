"""
Day 2 - Step 3-2: 스트리밍 RAG 챗봇

학습 목표:
- 스트리밍 응답 추가
- 사용자 경험 개선

실행:
streamlit run app_3_2.py
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
    st.warning("먼저 문서를 준비하세요")
    st.stop()

def cosine_similarity(vec1, vec2):
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

user_question = st.text_input("질문하세요")

if user_question:
    query_sql = f"SELECT SNOWFLAKE.CORTEX.EMBED_TEXT_768('snowflake-arctic-embed-m', '{user_question}') as embedding"
    query_emb = session.sql(query_sql).collect()[0]['EMBEDDING']
    
    similarities = []
    for i, emb in enumerate(st.session_state['embeddings']):
        sim = cosine_similarity(query_emb, emb)
        similarities.append((i, sim))
    
    similarities.sort(key=lambda x: x[1], reverse=True)
    top_chunks = [st.session_state['chunks'][idx] for idx, _ in similarities[:3]]
    
    context = "\n\n".join(top_chunks)
    prompt = f"다음 문서를 참고하여 답변하세요:\n\n{context}\n\n질문: {user_question}"
    
    # TODO: 스트리밍 응답 추가
    # 힌트: response_stream = Complete(model="llama3.1-70b", prompt=prompt, session=session, stream=True)
    #       st.write_stream(response_stream)
    
    st.write("### 답변")
