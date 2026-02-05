"""
Day 2 - Step 3: 기본 RAG 챗봇

학습 목표:
- 검색된 컨텍스트로 답변 생성
- RAG 파이프라인 완성

실행:
streamlit run app_3_1.py
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
    st.warning("먼저 문서를 준비하세요")
    st.stop()

def cosine_similarity(vec1, vec2):
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

# 예시 질문 (sample_data/animals.txt 사용 시)
st.info("💡 예시: 사자는 어디에 살아? / 펭귄은 무엇을 먹어? / 가장 큰 동물은?")

user_question = st.text_input("질문하세요", placeholder="예: 기린의 목은 얼마나 길어?")

if user_question:
    # 1. 쿼리 임베딩
    query_sql = f"SELECT SNOWFLAKE.CORTEX.EMBED_TEXT_768('snowflake-arctic-embed-m', '{user_question}') as embedding"
    query_emb = session.sql(query_sql).collect()[0]['EMBEDDING']
    
    # 2. 유사 청크 찾기
    similarities = []
    for i, emb in enumerate(st.session_state['embeddings']):
        sim = cosine_similarity(query_emb, emb)
        similarities.append((i, sim))
    
    similarities.sort(key=lambda x: x[1], reverse=True)
    top_chunks = [st.session_state['chunks'][idx] for idx, _ in similarities[:3]]
    
    # TODO: 3. RAG 프롬프트 생성
    # 힌트: context = "\n\n".join(top_chunks)
    #       prompt = f"다음 문서를 참고하여 답변하세요:\n\n{context}\n\n질문: {user_question}"
    context = ""  # TODO를 완성하세요
    prompt = user_question  # TODO를 완성하세요

    # TODO: 4. LLM으로 답변 생성
    # 힌트: response = complete_llm(session, "llama3.1-70b", prompt)
    response = "TODO를 완성하세요"  # TODO를 완성하세요

    st.write("### 답변")
    st.write(response)
