"""
Day 2 - Step 4-2: 출처 표시 (정답)
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
        
        with st.expander("📄 참고 문서"):
            for i, chunk in enumerate(top_chunks):
                st.write(f"**출처 {i+1}**")
                st.write(chunk[:150] + "...")
    
    st.session_state.messages.append({
        "role": "assistant",
        "content": response,
        "sources": top_chunks
    })
