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

# 임베딩 설명
with st.expander("💡 벡터 임베딩(Embedding)이란?", expanded=True):
    st.markdown("""
    **임베딩**: 텍스트를 숫자(벡터)로 변환하는 것
    - 컴퓨터는 텍스트를 직접 이해할 수 없어서 숫자로 바꿔야 합니다
    - 비슷한 의미의 문장은 비슷한 숫자 패턴을 갖게 됩니다

    **예시:**
    ```
    "고양이는 귀엽다" → [0.12, -0.34, 0.56, ...]  (768개의 숫자)
    "강아지는 사랑스럽다" → [0.11, -0.32, 0.58, ...]  ← 비슷한 패턴!
    "오늘 날씨가 좋다" → [0.87, 0.23, -0.45, ...]  ← 다른 패턴
    ```

    **왜 768개?**
    - `snowflake-arctic-embed-m` 모델이 768차원 벡터를 생성합니다
    - 차원이 높을수록 더 세밀한 의미 표현이 가능합니다

    **활용**: 이 숫자들을 비교해서 "비슷한 내용 찾기"를 할 수 있습니다!
    """)

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

def escape_sql_string(text):
    """SQL 인젝션 방지 (특수문자 이스케이프)"""
    if text is None:
        return ""
    return text.replace("'", "''").replace("\\", "\\\\")

if st.button("임베딩 생성"):
    embeddings = []
    progress_bar = st.progress(0)
    status_text = st.empty()

    # TODO: 각 청크의 임베딩을 생성하여 embeddings에 추가하세요
    for i, chunk in enumerate(chunks):
        status_text.text(f"임베딩 생성 중... ({i+1}/{len(chunks)})")
        safe_chunk = escape_sql_string(chunk)
        # TODO: SQL로 임베딩 생성 후 embeddings에 추가 (2줄)
        # 힌트: SNOWFLAKE.CORTEX.EMBED_TEXT_768('snowflake-arctic-embed-m', '{safe_chunk}')
        pass
        progress_bar.progress((i + 1) / len(chunks))


    st.session_state['embeddings'] = embeddings

    # 파일로 저장 (다른 앱과 공유)
    with open(os.path.join(DATA_DIR, "embeddings.pkl"), "wb") as f:
        pickle.dump(embeddings, f)

    st.success(f"✅ {len(embeddings)}개 임베딩 생성 완료!")
