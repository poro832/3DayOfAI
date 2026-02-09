"""
Day 3 - Step 3-2: RAG + Agent 통합 (실습)

[학습 목표]
- RAG와 Agent를 결합
- 문서 기반 + 도구 기반 하이브리드
- 동적 컨텍스트 활용

[핵심 개념]
RAG로 관련 문서를 검색하고, Agent가 추가 도구를 활용하여
더 풍부한 답변을 생성합니다.
"""

import streamlit as st
import json
import numpy as np
import pickle
import os
from datetime import datetime
from snowflake.snowpark import Session

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


try:
    session = get_snowflake_session()
except Exception as e:
    st.error(f"Snowflake 연결 실패: {e}")
    st.stop()

st.title("📚🤖 RAG + Agent 통합")

with st.expander("💡 RAG + Agent란?", expanded=True):
    st.markdown("""
    ### RAG만 사용 vs RAG + Agent

    **RAG만:**
    ```
    질문: "사자의 속도는?"
    → 문서 검색 → "사자는 시속 80km로 달립니다"
    ```

    **RAG + Agent:**
    ```
    질문: "사자 속도를 mph로 변환하면?"
    → 문서 검색 → 80 km/h 발견
    → calculate 도구 → 80 * 0.621 = 49.7 mph
    → 조합 → "사자는 시속 약 50 mph로 달립니다"
    ```

    ### 언제 유용한가?
    - 문서 정보 + 계산 필요
    - 문서 정보 + 현재 시간/날씨 조합
    - 여러 문서 비교 + 요약
    """)

# 도구 정의
TOOLS = {
    "calculate": {
        "desc": "수학 계산",
        "handler": lambda expr: str(eval(expr)) if all(c in "0123456789+-*/(). " for c in expr) else "오류"
    },
    "get_current_date": {
        "desc": "현재 날짜",
        "handler": lambda: datetime.now().strftime("%Y년 %m월 %d일")
    },
    "convert_unit": {
        "desc": "단위 변환 (km/mph, kg/lb 등)",
        "handler": lambda val, from_u, to_u: f"{float(val) * 0.621:.1f}" if from_u == "km" and to_u == "mph" else str(val)
    }
}

# Day2의 데이터 로드 시도
chunks_path = os.path.join(DATA_DIR, "..", "Day2", "chunks.pkl")
embeddings_path = os.path.join(DATA_DIR, "..", "Day2", "embeddings.pkl")

has_rag_data = False
if os.path.exists(chunks_path) and os.path.exists(embeddings_path):
    try:
        with open(chunks_path, "rb") as f:
            chunks = pickle.load(f)
        with open(embeddings_path, "rb") as f:
            embeddings = pickle.load(f)
        has_rag_data = True
        st.success(f"✅ RAG 데이터 로드: {len(chunks)} 청크")
    except:
        pass

if not has_rag_data:
    st.warning("⚠️ Day2의 RAG 데이터가 없습니다. 샘플 데이터를 사용합니다.")
    # 샘플 데이터
    chunks = [
        "사자는 고양이과 동물로, 시속 80km로 달릴 수 있습니다. 아프리카 초원에 서식합니다.",
        "코끼리는 하루에 약 200리터의 물을 마시고 150kg의 음식을 먹습니다.",
        "치타는 육상에서 가장 빠른 동물로 시속 120km로 달립니다."
    ]
    embeddings = None


def search_documents(query, top_k=3):
    """RAG 검색"""
    if embeddings is None:
        # 키워드 기반 폴백
        results = []
        for i, chunk in enumerate(chunks):
            score = sum(1 for word in query.split() if word in chunk)
            results.append((i, score, chunk))
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]

    # TODO: 벡터 검색 - 쿼리를 임베딩한 후 유사도 계산
    # 힌트: safe_query = escape_sql_string(query)
    #       query_sql = f"""SELECT SNOWFLAKE.CORTEX.EMBED_TEXT_768('snowflake-arctic-embed-m', '{safe_query}') as embedding"""
    #       query_emb = session.sql(query_sql).collect()[0]['EMBEDDING']
    safe_query = escape_sql_string(query)
    query_emb = None  # TODO: 위 힌트를 참고하여 query_emb를 구하세요

    if query_emb is None:
        return [(0, 0.5, chunks[0])] if chunks else []

    results = []
    for i, emb in enumerate(embeddings):
        sim = cosine_similarity(query_emb, emb)
        results.append((i, sim, chunks[i]))

    results.sort(key=lambda x: x[1], reverse=True)
    return results[:top_k]


def rag_agent(user_input):
    """RAG + Agent 하이브리드"""
    thinking_log = []

    # 1. RAG 검색
    thinking_log.append({"step": "RAG 검색", "action": "문서에서 관련 정보 검색"})
    search_results = search_documents(user_input)
    context = "\n".join([r[2] for r in search_results])
    thinking_log.append({"step": "검색 결과", "action": f"{len(search_results)}개 문서 발견"})

    # Agent 도구 필요 여부 판단
    tools_desc = ", ".join([f"{k}({v['desc']})" for k, v in TOOLS.items()])

    plan_prompt = f"""사용자 질문과 검색된 문서를 분석하세요.

검색된 문서:
{context}

사용자: "{user_input}"

사용 가능한 도구: {tools_desc}

문서 정보만으로 충분하면: {{"need_tool": false}}
추가 도구가 필요하면: {{"need_tool": true, "tool": "도구명", "params": {{}}, "reason": "이유"}}

JSON:"""

    response = complete_llm(session, "llama3.1-70b", plan_prompt)

    try:
        json_start = response.find('{')
        json_end = response.rfind('}') + 1
        decision = json.loads(response[json_start:json_end])
    except:
        decision = {"need_tool": False}

    thinking_log.append({"step": "도구 판단", "action": str(decision)})

    # 도구 실행 (필요한 경우)
    tool_result = None
    if decision.get("need_tool") and decision.get("tool"):
        tool_name = decision["tool"]
        params = decision.get("params", {})

        thinking_log.append({"step": "도구 실행", "action": f"{tool_name}({params})"})

        if tool_name in TOOLS:
            try:
                handler = TOOLS[tool_name]["handler"]
                if params:
                    tool_result = handler(*params.values())
                else:
                    tool_result = handler()
                thinking_log.append({"step": "도구 결과", "action": tool_result})
            except Exception as e:
                tool_result = f"오류: {e}"

    # 최종 답변 생성
    final_prompt = f"""검색된 문서와 도구 결과를 조합하여 답변하세요.

검색된 문서:
{context}

{"도구 결과: " + str(tool_result) if tool_result else ""}

질문: {user_input}

답변:"""

    answer = complete_llm(session, "llama3.1-70b", final_prompt)
    thinking_log.append({"step": "최종 답변", "action": "생성 완료"})

    return answer, thinking_log, search_results


# UI
st.write("### 💡 예시")
examples = [
    "사자는 얼마나 빨라? mph로 알려줘",
    "코끼리가 하루에 마시는 물의 양은? 리터로",
    "가장 빠른 동물의 속도를 계산해줘"
]

for ex in examples:
    if st.button(ex, key=f"ex_{ex}"):
        st.session_state.rag_query = ex

user_input = st.text_input("질문", value=st.session_state.get("rag_query", ""))

if user_input and st.button("🚀 RAG + Agent 실행"):
    with st.spinner("🔍 RAG 검색 + 🤖 Agent 실행 중..."):
        answer, log, sources = rag_agent(user_input)

    # 사고 과정
    with st.expander("🧠 처리 과정", expanded=True):
        for entry in log:
            if "검색" in entry["step"]:
                st.info(f"🔍 **{entry['step']}**: {entry['action']}")
            elif "도구" in entry["step"]:
                st.warning(f"🔧 **{entry['step']}**: {entry['action']}")
            else:
                st.write(f"**{entry['step']}**: {entry['action']}")

    # 출처
    with st.expander("📄 참고 문서"):
        for i, (idx, score, text) in enumerate(sources, 1):
            st.write(f"**[{i}]** (점수: {score:.2f})")
            st.caption(text[:200])

    # 답변
    st.write("### 💬 답변")
    st.success(answer)
