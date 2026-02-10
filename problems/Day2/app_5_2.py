"""
Day 2 - Step 5-2: 하이브리드 검색

학습 목표:
- 키워드 검색 + 시맨틱 검색 결합
- 각 방식의 장단점 이해
- 하이브리드 스코어링

실행: streamlit run problems/Day2/app_5_2.py
"""

import streamlit as st
import numpy as np
import pickle
import os
import re
from snowflake.snowpark import Session
from collections import Counter

DATA_DIR = os.path.dirname(os.path.abspath(__file__))


def get_snowflake_session():
    connection_parameters = st.secrets["connections"]["snowflake"]
    return Session.builder.configs(connection_parameters).create()


def complete_llm(session, model, prompt):
    escaped_prompt = prompt.replace("'", "''")
    sql = f"SELECT SNOWFLAKE.CORTEX.COMPLETE('{model}', '{escaped_prompt}')"
    result = session.sql(sql).collect()
    return result[0][0]


def escape_sql_string(text):
    if text is None:
        return ""
    return text.replace("'", "''").replace("\\", "\\\\")


def cosine_similarity(vec1, vec2):
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))


# 키워드 검색 함수들
def tokenize(text):
    """간단한 토큰화"""
    text = text.lower()
    tokens = re.findall(r'\b\w+\b', text)
    return tokens


def bm25_score(query_tokens, doc_tokens, all_docs, k1=1.5, b=0.75):
    """BM25 스코어 계산"""
    doc_len = len(doc_tokens)
    avg_doc_len = sum(len(tokenize(d)) for d in all_docs) / len(all_docs)

    score = 0
    doc_counter = Counter(doc_tokens)
    n_docs = len(all_docs)

    for term in query_tokens:
        if term not in doc_counter:
            continue

        # 문서 빈도
        df = sum(1 for d in all_docs if term in tokenize(d))
        df = max(df, 1)

        # IDF
        idf = np.log((n_docs - df + 0.5) / (df + 0.5) + 1)

        # TF with BM25 normalization
        tf = doc_counter[term]
        tf_norm = (tf * (k1 + 1)) / (tf + k1 * (1 - b + b * doc_len / avg_doc_len))

        score += idf * tf_norm

    return score


def keyword_search(query, documents, top_k=5):
    """키워드 기반 검색 (BM25)"""
    query_tokens = tokenize(query)

    scores = []
    for i, doc in enumerate(documents):
        doc_tokens = tokenize(doc)
        score = bm25_score(query_tokens, doc_tokens, documents)
        scores.append((i, score))

    scores.sort(key=lambda x: x[1], reverse=True)
    return scores[:top_k]


try:
    session = get_snowflake_session()
except Exception as e:
    st.error(f"Snowflake 연결 실패: {e}")
    st.stop()

st.title("🔀 하이브리드 검색")

with st.expander("💡 하이브리드 검색이란?", expanded=True):
    st.markdown("""
    ### 키워드 검색 + 시맨틱 검색의 결합

    | 방식 | 장점 | 단점 |
    |------|------|------|
    | **키워드 (BM25)** | 정확한 단어 매칭, 빠름 | 동의어 못 찾음 |
    | **시맨틱 (Vector)** | 의미 이해, 동의어 매칭 | 정확한 단어 무시할 수 있음 |
    | **하이브리드** | 두 장점 결합 | 가중치 조정 필요 |

    ### 예시
    ```
    쿼리: "빠른 고양이과 동물"

    키워드 검색:
    ✓ "치타는 빠른 고양이과 동물입니다" (정확 매칭)
    ✗ "가장 빠른 육상동물" (키워드 없음)

    시맨틱 검색:
    ✓ "치타는 시속 120km로 달립니다" (의미 유사)
    ✓ "가장 빠른 육상동물" (의미 유사)

    하이브리드:
    ✓ 두 결과를 모두 포함!
    ```

    ### 점수 결합 방법
    - **가중 평균**: hybrid = α × keyword + (1-α) × semantic
    - **RRF (Reciprocal Rank Fusion)**: 순위 기반 결합
    """)

# 데이터 로드
chunks_path = os.path.join(DATA_DIR, "chunks.pkl")
embeddings_path = os.path.join(DATA_DIR, "embeddings.pkl")

if os.path.exists(chunks_path) and os.path.exists(embeddings_path):
    with open(chunks_path, "rb") as f:
        chunks = pickle.load(f)
    with open(embeddings_path, "rb") as f:
        embeddings = pickle.load(f)
    st.success(f"✅ {len(chunks)}개 문서 로드됨")
else:
    st.warning("먼저 임베딩을 생성하세요 (app_2_1.py)")
    st.stop()

# 검색 설정
st.write("### ⚙️ 검색 설정")

col1, col2 = st.columns(2)
with col1:
    search_mode = st.selectbox(
        "검색 모드",
        ["하이브리드", "키워드만", "시맨틱만"]
    )
with col2:
    if search_mode == "하이브리드":
        alpha = st.slider(
            "키워드 가중치 (α)",
            0.0, 1.0, 0.5,
            help="0 = 시맨틱만, 1 = 키워드만"
        )
    else:
        alpha = 1.0 if search_mode == "키워드만" else 0.0

top_k = st.slider("결과 개수", 1, 10, 5)

st.info("💡 예시: 빠른 동물, 물을 많이 마시는, 아프리카 서식지")

query = st.text_input("검색어", placeholder="예: 가장 빠른 동물")

if query and st.button("🔍 검색"):
    st.write("### 📊 검색 결과")

    results = {}

    # 1. 키워드 검색
    if alpha > 0:
        with st.spinner("키워드 검색 중..."):
            keyword_results = keyword_search(query, chunks, top_k=len(chunks))
            # 점수 정규화 (0-1)
            max_kw_score = max(s for _, s in keyword_results) if keyword_results else 1
            keyword_scores = {
                idx: score / max_kw_score
                for idx, score in keyword_results
            }
            results["keyword"] = keyword_results[:top_k]

    # 2. 시맨틱 검색
    if alpha < 1:
        with st.spinner("시맨틱 검색 중..."):
            safe_query = escape_sql_string(query)
            query_sql = f"""
            SELECT SNOWFLAKE.CORTEX.EMBED_TEXT_768(
                'snowflake-arctic-embed-m',
                '{safe_query}'
            ) as embedding
            """
            query_emb = session.sql(query_sql).collect()[0]['EMBEDDING']

            semantic_results = []
            for i, emb in enumerate(embeddings):
                sim = cosine_similarity(query_emb, emb)
                semantic_results.append((i, sim))

            semantic_results.sort(key=lambda x: x[1], reverse=True)
            # 점수는 이미 0-1
            semantic_scores = {idx: score for idx, score in semantic_results}
            results["semantic"] = semantic_results[:top_k]

    # 3. 하이브리드 점수 계산
    if search_mode == "하이브리드":
        hybrid_scores = {}
        all_indices = set(keyword_scores.keys()) | set(semantic_scores.keys())

        for idx in all_indices:
            kw_score = keyword_scores.get(idx, 0)
            sem_score = semantic_scores.get(idx, 0)
            # TODO: 가중 평균 계산 (1줄)
            # 힌트: alpha * kw_score + (1 - alpha) * sem_score
            hybrid_scores[idx] = 0  # TODO를 완성하세요

        hybrid_results = sorted(hybrid_scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
        results["hybrid"] = hybrid_results

    # 결과 표시
    if search_mode == "하이브리드":
        # 탭으로 세 가지 결과 비교
        tab1, tab2, tab3 = st.tabs(["🔀 하이브리드", "🔤 키워드", "🧠 시맨틱"])

        with tab1:
            st.write(f"**하이브리드 결과** (α={alpha})")
            for rank, (idx, score) in enumerate(results["hybrid"], 1):
                with st.container():
                    col1, col2 = st.columns([1, 5])
                    with col1:
                        st.metric(f"#{rank}", f"{score:.3f}")
                    with col2:
                        st.write(chunks[idx][:200] + "..." if len(chunks[idx]) > 200 else chunks[idx])
                    st.divider()

        with tab2:
            st.write("**키워드 결과 (BM25)**")
            for rank, (idx, score) in enumerate(results["keyword"], 1):
                kw_norm = keyword_scores[idx]
                st.write(f"**#{rank}** (점수: {kw_norm:.3f})")
                st.caption(chunks[idx][:150] + "...")
                st.divider()

        with tab3:
            st.write("**시맨틱 결과 (Cosine)**")
            for rank, (idx, score) in enumerate(results["semantic"], 1):
                st.write(f"**#{rank}** (점수: {score:.3f})")
                st.caption(chunks[idx][:150] + "...")
                st.divider()

        # 결과 비교 분석
        st.write("### 🔄 결과 비교")

        kw_top = set(idx for idx, _ in results["keyword"])
        sem_top = set(idx for idx, _ in results["semantic"])
        hyb_top = set(idx for idx, _ in results["hybrid"])

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("키워드에만 있음", len(kw_top - sem_top))
        with col2:
            st.metric("시맨틱에만 있음", len(sem_top - kw_top))
        with col3:
            st.metric("공통 결과", len(kw_top & sem_top))

    else:
        # 단일 모드
        mode_key = "keyword" if search_mode == "키워드만" else "semantic"
        mode_name = "키워드 (BM25)" if search_mode == "키워드만" else "시맨틱 (Cosine)"

        st.write(f"**{mode_name} 결과**")
        for rank, (idx, score) in enumerate(results[mode_key], 1):
            with st.container():
                col1, col2 = st.columns([1, 5])
                with col1:
                    st.metric(f"#{rank}", f"{score:.3f}")
                with col2:
                    st.write(chunks[idx][:200] + "..." if len(chunks[idx]) > 200 else chunks[idx])
                st.divider()

# 가중치 실험
with st.expander("🔬 가중치 실험"):
    st.write("다양한 α 값에서 상위 결과가 어떻게 변하는지 확인")

    if query:
        # 여러 alpha 값으로 테스트
        test_alphas = [0.0, 0.25, 0.5, 0.75, 1.0]

        # 이미 계산된 점수 재사용
        if 'keyword_scores' in dir() and 'semantic_scores' in dir():
            results_by_alpha = {}

            for a in test_alphas:
                scores = {}
                for idx in set(keyword_scores.keys()) | set(semantic_scores.keys()):
                    kw = keyword_scores.get(idx, 0)
                    sem = semantic_scores.get(idx, 0)
                    scores[idx] = a * kw + (1 - a) * sem

                top_idx = sorted(scores.items(), key=lambda x: x[1], reverse=True)[0][0]
                results_by_alpha[a] = chunks[top_idx][:50] + "..."

            import pandas as pd
            df = pd.DataFrame([
                {"α": a, "최상위 결과": results_by_alpha[a]}
                for a in test_alphas
            ])
            st.dataframe(df, use_container_width=True)
    else:
        st.info("먼저 검색을 실행하세요.")
