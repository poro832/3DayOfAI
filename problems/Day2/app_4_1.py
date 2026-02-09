"""
Day 2 - Step 4-1: 채팅 히스토리 추가

학습 목표:
- 대화 히스토리 유지
- 채팅 UI 구현

실행:
streamlit run app_4_1.py
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

st.title("💬 RAG 챗봇 with History")

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

# TODO: 메시지 히스토리 초기화
# 힌트: st.session_state에 messages 키가 없으면 빈 리스트로 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []

def cosine_similarity(vec1, vec2):
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

# 예시 질문 (sample_data/animals.txt 사용 시)
st.info("💡 예시: 코끼리는 하루에 얼마나 먹어? / 상어의 특징은? / 꿀벌은 어떻게 소통해?")

# TODO 1: 이전 메시지 표시 (3줄)
# 힌트: for 루프 → st.chat_message(role) → st.write(content)
pass  # TODO를 완성하세요

user_input = st.chat_input("질문하세요...")

if user_input:
    # TODO 2: 사용자 메시지를 히스토리에 추가하고 화면에 표시 (3줄)
    # 힌트: messages.append() + st.chat_message("user") + st.write()
    pass  # TODO를 완성하세요

    # RAG 검색
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

    # TODO 3: AI 응답을 스트리밍으로 표시하고 히스토리에 저장 (4줄)
    # 힌트: st.chat_message("assistant") 안에서 stream_text + st.write_stream
    #       그 후 messages.append()로 저장
    pass  # TODO를 완성하세요

