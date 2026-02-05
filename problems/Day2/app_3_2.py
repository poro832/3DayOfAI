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

# 예시 질문 (sample_data/animals.txt 사용 시)
st.info("💡 예시: 돌고래는 어떻게 의사소통해? / 기린은 하루에 얼마나 자? / 가장 빠른 동물은?")

user_question = st.text_input("질문하세요", placeholder="예: 펭귄은 어디에 살아?")

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
    # 힌트: def stream_text(text):
    #           import time
    #           words = text.split()
    #           for word in words:
    #               yield word + ' '
    #               time.sleep(0.02)
    #
    #       response = complete_llm(session, "llama3.1-70b", prompt)
    #       st.write_stream(stream_text(response))
    
    st.write("### 답변")
