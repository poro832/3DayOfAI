"""
Day 2 - Step 2-2: 유사도 검색

학습 목표:
- 코사인 유사도 계산
- 유사한 청크 찾기

실행:
streamlit run app_2_2.py
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

# TODO: 코사인 유사도 함수 작성
def cosine_similarity(vec1, vec2):
    """두 벡터의 코사인 유사도 계산"""
    # TODO: numpy 사용
    # 힌트: np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
    pass

user_query = st.text_input("검색어 입력")

if user_query and st.button("검색"):
    # TODO: 쿼리 임베딩 생성
    
    
    # TODO: 각 청크와 유사도 계산
    
    
    # TODO: 가장 유사한 청크 3개 찾기
    
    
    st.write("### 검색 결과")
