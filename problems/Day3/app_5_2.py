"""
Day 3 - Step 5-2: 최종 프로젝트 - AI 만능 어시스턴트 (실습)

3일간 학습한 모든 기술을 통합한 올인원 AI 어시스턴트입니다.

[활용 기술]
- Day 1: Streamlit UI, LLM 호출, 스트리밍, 캐싱, 세션 상태, 채팅 UI, 시스템 프롬프트
- Day 2: RAG (임베딩, 코사인 유사도, 출처 표시)
- Day 3: Agent (LLM 기반 도구 선택, 멀티턴, 사고과정 시각화)
"""

import streamlit as st
import json
import time
import numpy as np
import pandas as pd
from datetime import datetime
from snowflake.snowpark import Session


# ==============================================
# Day 1: Snowflake 연결 + LLM 호출 + 스트리밍
# ==============================================

@st.cache_resource
def get_snowflake_session():
    connection_parameters = st.secrets["connections"]["snowflake"]
    return Session.builder.configs(connection_parameters).create()


def complete_llm(session, model, prompt):
    escaped_prompt = prompt.replace("'", "''")
    sql = f"SELECT SNOWFLAKE.CORTEX.COMPLETE('{model}', '{escaped_prompt}')"
    result = session.sql(sql).collect()
    return result[0][0]


def get_embedding(session, text):
    """Day 2: 벡터 임베딩 생성"""
    safe_text = text.replace("'", "''").replace("\\", "\\\\")[:2000]
    sql = f"SELECT SNOWFLAKE.CORTEX.EMBED_TEXT_768('snowflake-arctic-embed-m', '{safe_text}')"
    result = session.sql(sql).collect()
    raw = result[0][0]
    if isinstance(raw, str):
        return json.loads(raw)
    return list(raw)


def stream_text(text):
    """Day 1: 스트리밍 출력"""
    for char in text:
        yield char
        time.sleep(0.015)


try:
    session = get_snowflake_session()
except Exception as e:
    st.error(f"Snowflake 연결 실패: {e}")
    st.stop()


# ==============================================
# Day 2: RAG - 지식 베이스
# ==============================================

KNOWLEDGE_BASE = [
    {
        "title": "Streamlit 기초",
        "content": "Streamlit은 Python으로 데이터 웹 앱을 빠르게 만드는 프레임워크입니다. st.title()로 제목, st.write()로 텍스트, st.button()으로 버튼, st.text_input()은 텍스트 입력, st.selectbox()는 드롭다운, st.slider()는 슬라이더를 제공합니다. st.sidebar로 사이드바에 위젯을 배치할 수 있습니다."
    },
    {
        "title": "스트리밍과 캐싱",
        "content": "스트리밍은 응답을 글자별로 출력하여 체감 속도를 높이는 기법입니다. Python yield를 사용한 제너레이터 함수로 구현하며 st.write_stream()으로 출력합니다. 캐싱은 @st.cache_data로 함수 결과를 저장하여 동일 입력 재계산을 방지합니다. @st.cache_resource는 DB 연결 같은 리소스를 캐싱합니다."
    },
    {
        "title": "세션 상태와 채팅 UI",
        "content": "st.session_state는 사용자별 데이터를 저장하는 딕셔너리입니다. 채팅 히스토리를 st.session_state.messages에 저장하면 대화가 유지됩니다. st.chat_message()로 말풍선을, st.chat_input()으로 입력창을 만들어 ChatGPT 같은 채팅 인터페이스를 구현합니다."
    },
    {
        "title": "RAG 파이프라인",
        "content": "RAG(Retrieval Augmented Generation)는 외부 문서를 검색하여 LLM에 맥락으로 제공하는 기법입니다. 과정: 1) 문서를 청크로 나누기(청킹), 2) 각 청크를 벡터로 변환(임베딩), 3) 사용자 질문과 유사한 청크 검색(유사도 검색), 4) 검색된 청크를 프롬프트에 포함하여 답변 생성. Snowflake EMBED_TEXT_768 함수로 벡터 임베딩을 생성합니다."
    },
    {
        "title": "청킹과 유사도 함수",
        "content": "청킹 전략: 고정 크기(일정 글자 수), 문장 기반(문장 단위), 단락 기반(빈 줄 기준). 오버랩으로 문맥을 연결합니다. 유사도 함수: 코사인 유사도(방향 유사성, 0~1), 유클리드 거리(절대 거리), 맨해튼 거리(차원별 차이 합). RAG에서는 코사인 유사도가 가장 널리 사용됩니다."
    },
    {
        "title": "쿼리 리라이팅과 RAG 품질 평가",
        "content": "쿼리 리라이팅은 검색 성능을 높이기 위해 질문을 변환하는 기법입니다. 키워드 추출, 쿼리 확장, HyDE(가상 답변 생성 후 검색) 전략이 있습니다. RAG Triad로 품질 평가: Context Relevance(문맥 관련성), Groundedness(근거 기반), Answer Relevance(답변 적절성)."
    },
    {
        "title": "AI Agent와 Function Calling",
        "content": "AI Agent는 LLM이 사용자 의도를 파악하여 적절한 도구를 선택하고 실행하는 시스템입니다. Function Calling은 LLM에게 도구 설명을 제공하면 JSON으로 어떤 도구를 호출할지 결정하는 방식입니다. 도구 스키마에는 이름, 설명, 파라미터가 포함됩니다."
    },
    {
        "title": "멀티턴 Agent와 도구 오케스트레이션",
        "content": "멀티턴 Agent는 이전 대화 맥락을 기억하며 여러 번의 도구 호출을 수행합니다. Think-Act-Observe 루프로 사고과정을 시각화합니다. 다중 도구 오케스트레이션은 여러 도구를 순차적 또는 병렬적으로 실행하여 복잡한 요청을 처리합니다."
    }
]


def cosine_similarity(vec1, vec2):
    """Day 2: 코사인 유사도"""
    vec1, vec2 = np.array(vec1), np.array(vec2)
    return float(np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2)))


@st.cache_data
def build_knowledge_embeddings(_session):
    """지식 베이스 벡터 임베딩 (Day 2: 벡터 임베딩 + Day 1: 캐싱)"""
    embeddings = []
    for doc in KNOWLEDGE_BASE:
        emb = get_embedding(_session, doc["content"])
        embeddings.append(emb)
    return embeddings


def search_knowledge(query, top_k=2):
    """RAG 검색 (Day 2: 유사도 검색 + 출처 표시)"""
    embeddings = build_knowledge_embeddings(session)
    query_emb = get_embedding(session, query)

    scores = []
    for i, emb in enumerate(embeddings):
        score = cosine_similarity(query_emb, emb)
        scores.append((i, score))

    scores.sort(key=lambda x: x[1], reverse=True)

    return [
        {
            "title": KNOWLEDGE_BASE[idx]["title"],
            "content": KNOWLEDGE_BASE[idx]["content"],
            "score": score
        }
        for idx, score in scores[:top_k]
    ]


# ==============================================
# Day 3: 제품 데이터 (데이터 분석 도구용)
# ==============================================

@st.cache_data
def get_product_data():
    return pd.DataFrame({
        "제품": [
            "맥북 프로 14", "맥북 에어 M3", "갤럭시북4 프로", "LG 그램 17",
            "아이폰 15 Pro", "갤럭시 S24 Ultra", "갤럭시 Z 플립5", "아이폰 15",
            "에어팟 프로 2", "갤럭시 버즈3 프로", "소니 WH-1000XM5",
            "애플워치 시리즈 9", "갤럭시 워치6",
            "로지텍 MX Master 3S", "LG 울트라파인 27"
        ],
        "브랜드": [
            "Apple", "Apple", "Samsung", "LG",
            "Apple", "Samsung", "Samsung", "Apple",
            "Apple", "Samsung", "Sony",
            "Apple", "Samsung",
            "Logitech", "LG"
        ],
        "카테고리": [
            "노트북", "노트북", "노트북", "노트북",
            "스마트폰", "스마트폰", "스마트폰", "스마트폰",
            "이어폰", "이어폰", "헤드폰",
            "웨어러블", "웨어러블",
            "마우스", "모니터"
        ],
        "가격": [
            2890000, 1890000, 1790000, 1990000,
            1550000, 1450000, 1350000, 1250000,
            359000, 329000, 549000,
            599000, 369000,
            159000, 650000
        ],
        "판매량": [
            120, 250, 180, 95,
            400, 350, 200, 380,
            600, 450, 200,
            280, 320,
            500, 130
        ],
        "평점": [
            4.8, 4.6, 4.3, 4.4,
            4.7, 4.8, 4.2, 4.5,
            4.7, 4.4, 4.8,
            4.5, 4.2,
            4.7, 4.5
        ]
    })


# ==============================================
# Day 3: Agent - 도구 정의 + LLM 기반 선택
# ==============================================

TOOLS = [
    {
        "name": "general_chat",
        "description": "일반 대화, 인사, 질문 답변. 다른 도구에 해당하지 않는 모든 요청."
    },
    {
        "name": "search_knowledge",
        "description": "이 과정에서 배운 기술 지식 검색. Streamlit, Snowflake, RAG, Agent, 청킹, 임베딩, 유사도, 캐싱, 스트리밍 관련 질문."
    },
    {
        "name": "analyze_data",
        "description": "전자 제품 데이터 분석. 제품명, 브랜드(Apple/Samsung/LG/Sony/Logitech), 카테고리, 가격, 판매량, 평점 조회 및 분석."
    },
    {
        "name": "calculator",
        "description": "수학 계산. 사칙연산, 거듭제곱, 제곱근 등."
    },
    {
        "name": "get_time",
        "description": "현재 날짜와 시간 조회."
    }
]


def select_tool(user_message, model):
    """LLM 기반 도구 선택 (Day 3: Function Calling)"""
    tools_desc = "\n".join([f"- {t['name']}: {t['description']}" for t in TOOLS])

    prompt = f"""사용자 메시지를 분석하고 가장 적합한 도구 하나를 선택하세요.

도구 목록:
{tools_desc}

사용자: "{user_message}"

반드시 아래 JSON 형식으로만 응답:
{{"tool": "도구이름", "param": "핵심 파라미터"}}

JSON:"""

    result = complete_llm(session, model, prompt)

    try:
        result = result.strip()
        if "```" in result:
            result = result.split("```")[1]
            if result.startswith("json"):
                result = result[4:]
        start = result.find("{")
        end = result.rfind("}") + 1
        if start >= 0 and end > start:
            return json.loads(result[start:end])
    except Exception:
        pass

    return {"tool": "general_chat", "param": user_message}


def execute_tool(tool_name, param, model, system_prompt):
    """도구 실행 및 결과 반환 (Day 3: Agent 실행)"""

    if tool_name == "search_knowledge":
        # Day 2: RAG 검색 + 출처 표시
        results = search_knowledge(param, top_k=2)
        context = "\n\n".join([
            f"[{r['title']}] (유사도: {r['score']:.3f})\n{r['content']}"
            for r in results
        ])
        prompt = f"""다음 참고 자료를 바탕으로 질문에 답변하세요.

참고 자료:
{context}

질문: {param}

참고 자료 기반으로 답변:"""
        answer = complete_llm(session, model, prompt)
        sources = " | ".join([f"{r['title']}({r['score']:.2f})" for r in results])
        return answer, "🔍 지식 검색 (RAG)", sources

    elif tool_name == "analyze_data":
        # Day 3: 데이터 분석
        df = get_product_data()
        prompt = f"""다음 전자제품 데이터를 분석하여 질문에 답하세요.

{df.to_string()}

질문: {param}

데이터 기반으로 정확하게 답변:"""
        answer = complete_llm(session, model, prompt)
        return answer, "📊 데이터 분석", None

    elif tool_name == "calculator":
        # Day 3: 계산기 도구
        try:
            allowed = set("0123456789+-*/.() ")
            expr = param.replace("^", "**").replace("x", "*").replace("×", "*").replace("÷", "/")
            if all(c in allowed for c in expr):
                result = eval(expr)
                return f"계산 결과: **{param} = {result:,}**", "🔢 계산기", None
            else:
                return f"계산할 수 없는 표현식: {param}", "🔢 계산기", None
        except Exception as e:
            return f"계산 오류: {e}", "🔢 계산기", None

    elif tool_name == "get_time":
        # Day 3: 시간 조회 도구
        now = datetime.now()
        weekdays = {
            "Monday": "월요일", "Tuesday": "화요일", "Wednesday": "수요일",
            "Thursday": "목요일", "Friday": "금요일", "Saturday": "토요일", "Sunday": "일요일"
        }
        day_kr = weekdays.get(now.strftime("%A"), now.strftime("%A"))
        return f"현재: **{now.strftime('%Y년 %m월 %d일 %H시 %M분')}** ({day_kr})", "🕐 현재 시간", None

    else:
        # Day 1: 일반 대화
        prompt = f"""{system_prompt}

사용자: {param}

답변:"""
        answer = complete_llm(session, model, prompt)
        return answer, "💬 일반 대화", None


# ==============================================
# Streamlit UI (Day 1: 전체 UI 구성)
# ==============================================

st.title("🤖 AI 만능 어시스턴트")
st.caption("Day 1~3의 모든 기술을 통합한 올인원 AI")

# --- 사이드바 (Day 1: 위젯 + 사이드바) ---
with st.sidebar:
    st.header("⚙️ 설정")

    model = st.selectbox("LLM 모델", ["llama3.1-70b", "mistral-7b", "llama3.1-8b"])

    system_prompt = st.text_area(
        "시스템 프롬프트",
        value="당신은 친절하고 도움이 되는 AI 어시스턴트입니다. 한국어로 간결하게 답변합니다.",
        height=80
    )

    st.divider()

    st.write("**🛠️ 사용 가능한 도구**")
    for tool in TOOLS:
        icon = {"general_chat": "💬", "search_knowledge": "🔍", "analyze_data": "📊",
                "calculator": "🔢", "get_time": "🕐"}.get(tool["name"], "🔧")
        st.write(f"- {icon} {tool['description'][:20]}...")

    with st.expander("📋 제품 데이터 미리보기"):
        st.dataframe(get_product_data(), use_container_width=True, height=200)

    st.divider()

    if st.button("🗑️ 대화 초기화", use_container_width=True):
        st.session_state.final_messages = []
        st.rerun()

    st.divider()
    st.markdown("""
    **활용 기술:**
    - `Day 1` UI, 스트리밍, 캐싱, 세션
    - `Day 2` RAG, 임베딩, 유사도
    - `Day 3` Agent, Function Calling
    """)

# --- 과정 소개 ---
with st.expander("💡 AI 만능 어시스턴트란?", expanded=False):
    st.markdown("""
    ### 3일간 배운 기술의 총집합!

    이 앱은 **Day 1~3에서 학습한 모든 기술**을 하나로 통합한 AI 어시스턴트입니다.

    | 기술 | 출처 | 적용 |
    |------|------|------|
    | 채팅 UI + 세션 상태 | Day 1 | 대화 인터페이스 |
    | 스트리밍 출력 | Day 1 | 글자별 응답 표시 |
    | 시스템 프롬프트 | Day 1 | 사이드바에서 설정 |
    | 벡터 임베딩 + 유사도 | Day 2 | 지식 검색 (RAG) |
    | 출처 표시 | Day 2 | 검색 결과 출처 |
    | LLM 도구 선택 | Day 3 | Agent가 도구 자동 선택 |
    | 사고 과정 시각화 | Day 3 | Agent 판단 과정 표시 |
    """)

# --- 예시 질문 ---
st.write("### 💡 이런 질문을 해보세요")
examples = [
    ("RAG가 뭐야?", "🔍"),
    ("가장 비싼 제품은?", "📊"),
    ("1234 * 5678", "🔢"),
    ("지금 몇 시야?", "🕐"),
    ("안녕하세요!", "💬"),
    ("캐싱이 뭐야?", "🔍"),
]

example_cols = st.columns(3)
for i, (ex, icon) in enumerate(examples):
    with example_cols[i % 3]:
        if st.button(f"{icon} {ex}", key=f"final_ex_{i}", use_container_width=True):
            st.session_state.final_pending = ex
            st.rerun()

st.divider()


# --- 세션 상태 초기화 (Day 1: 세션 상태) ---
if "final_messages" not in st.session_state:
    st.session_state.final_messages = []


# --- 채팅 히스토리 표시 (Day 1: 채팅 UI) ---
for msg in st.session_state.final_messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("tool_label"):
            st.caption(f"🛠️ {msg['tool_label']}")
        if msg.get("sources"):
            st.caption(f"📚 출처: {msg['sources']}")


# --- 채팅 입력 (Day 1: chat_input) ---
pending = st.session_state.pop("final_pending", None)
user_input = st.chat_input("무엇이든 물어보세요! (지식 검색, 데이터 분석, 계산 등)")

if pending and not user_input:
    user_input = pending

if user_input:
    # 사용자 메시지
    st.session_state.final_messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # --- Agent 처리 (Day 3) ---
    with st.chat_message("assistant"):
        # 1. 도구 선택 (Day 3: Function Calling)
        with st.spinner("🤔 어떤 도구를 쓸지 결정 중..."):
            tool_choice = select_tool(user_input, model)

        tool_name = tool_choice.get("tool", "general_chat")
        tool_param = tool_choice.get("param", user_input)

        # 2. 사고 과정 시각화 (Day 3: Agent 사고과정)
        with st.expander("🧠 Agent 사고 과정", expanded=False):
            st.write(f"**선택된 도구**: `{tool_name}`")
            st.write(f"**파라미터**: {tool_param}")
            st.json(tool_choice)

        # 3. 도구 실행
        with st.spinner("⚙️ 도구 실행 중..."):
            answer, tool_label, sources = execute_tool(
                tool_name, tool_param, model, system_prompt
            )

        # 4. 스트리밍 출력 (Day 1: 스트리밍)
        st.write_stream(stream_text(answer))
        st.caption(f"🛠️ {tool_label}")
        if sources:
            st.caption(f"📚 출처: {sources}")

        # 5. 메시지 저장 (Day 1: 세션 상태)
        st.session_state.final_messages.append({
            "role": "assistant",
            "content": answer,
            "tool_label": tool_label,
            "sources": sources
        })
