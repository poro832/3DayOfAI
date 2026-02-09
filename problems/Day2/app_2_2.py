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

# TODO: 코사인 유사도 함수 작성
def cosine_similarity(vec1, vec2):
    """두 벡터의 코사인 유사도 계산"""
    # TODO: numpy의 dot(내적)과 norm(크기)을 사용하세요
    # 힌트: 코사인 유사도 = 내적 / (벡터A 크기 × 벡터B 크기)
    pass

# 예시 질문 (sample_data/animals.txt 사용 시)
st.info("💡 예시 질문: 사자, 코끼리 특징, 펭귄 먹이, 가장 빠른 동물")

user_query = st.text_input("검색어 입력", placeholder="예: 코끼리는 하루에 물을 얼마나 마셔?")

if user_query and st.button("검색"):
    # TODO: 쿼리 임베딩 생성
    
    
    # TODO: 각 청크와 유사도 계산
    
    
    # TODO: 가장 유사한 청크 3개 찾기
    
    
    st.write("### 검색 결과")
