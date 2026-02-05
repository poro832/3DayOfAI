"""
Day 2 - Step 2: 벡터 임베딩 생성

학습 목표:
- Snowflake Cortex Embed로 벡터 생성
- 청크별 임베딩 저장

실행:
streamlit run app_2_1.py
"""

import streamlit as st
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

st.title("🔢 벡터 임베딩")

# 저장된 청크 로드 시도
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
    
    # TODO: 각 청크에 대해 임베딩 생성
    # 힌트: for chunk in chunks:
    #           query = f"SELECT SNOWFLAKE.CORTEX.EMBED_TEXT_768('snowflake-arctic-embed-m', '{chunk}') as embedding"
    #           result = session.sql(query).collect()
    #           embeddings.append(result[0]['EMBEDDING'])
    
    
    
    
    
    st.session_state['embeddings'] = embeddings

    # 파일로 저장 (다른 앱과 공유)
    with open(os.path.join(DATA_DIR, "embeddings.pkl"), "wb") as f:
        pickle.dump(embeddings, f)

    st.success(f"✅ {len(embeddings)}개 임베딩 생성 완료!")
