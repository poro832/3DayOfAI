"""
Day 3 - Step 5-2: 최종 프로젝트 - AI 만능 어시스턴트 (실습)

3일간 학습한 모든 기술을 통합한 올인원 AI 어시스턴트입니다.
Google Gemini API로 고품질 응답 + 실시간 스트리밍을 제공합니다.

[활용 기술]
- Day 1: Streamlit UI, 스트리밍, 캐싱, 세션 상태, 채팅 UI, 시스템 프롬프트
- Day 2: RAG (임베딩, 코사인 유사도, 출처 표시)
- Day 3: Agent (LLM 기반 도구 선택, 도구 배지 표시)

[필요 설정] .streamlit/secrets.toml
[api_keys]
google = "AIza..."
"""

import streamlit as st
from google import genai
from google.genai import types
import json
import time
import numpy as np
import pandas as pd
from datetime import datetime
from snowflake.snowpark import Session


# ==============================================
# Gemini API
# ==============================================

GEMINI_MODELS = {
    "Gemini 2.5 Flash": "gemini-2.5-flash",
    "Gemini 2.5 Pro": "gemini-2.5-pro",
}


@st.cache_resource
def get_genai_client():
    return genai.Client(api_key=st.secrets["api_keys"]["google"])


def to_gemini_history(messages):
    """내부 메시지 형식 → Gemini 형식으로 변환"""
    history = []
    for msg in messages:
        role = "model" if msg["role"] == "assistant" else "user"
        entry = types.Content(role=role, parts=[types.Part(text=msg["content"])])
        if history and history[-1].role == role:
            history[-1].parts[0].text += "\n" + msg["content"]
        else:
            history.append(entry)
    # Gemini 히스토리는 user로 시작해야 함
    while history and history[0].role == "model":
        history.pop(0)
    return history


def complete_llm(messages, model_name):
    """비스트리밍 LLM 호출 (도구 선택용) - 429 에러 시 자동 재시도"""
    for attempt in range(3):
        try:
            if len(messages) == 1:
                response = client.models.generate_content(
                    model=model_name, contents=messages[0]["content"]
                )
            else:
                gemini_history = to_gemini_history(messages[:-1])
                chat = client.chats.create(model=model_name, history=gemini_history)
                response = chat.send_message(messages[-1]["content"])
            return response.text
        except Exception as e:
            if ("429" in str(e) or "RESOURCE_EXHAUSTED" in str(e)) and attempt < 2:
                time.sleep(10)
                continue
            raise


def stream_response(messages, system_prompt, model_name):
    """실시간 스트리밍 LLM 호출 (응답 생성용) - 429 에러 시 자동 재시도"""
    config = types.GenerateContentConfig(system_instruction=system_prompt)

    for attempt in range(3):
        try:
            if len(messages) == 1:
                response = client.models.generate_content_stream(
                    model=model_name, contents=messages[0]["content"], config=config
                )
            else:
                gemini_history = to_gemini_history(messages[:-1])
                chat = client.chats.create(model=model_name, history=gemini_history, config=config)
                response = chat.send_message_stream(messages[-1]["content"])

            for chunk in response:
                if chunk.text:
                    yield chunk.text
            return
        except Exception as e:
            if ("429" in str(e) or "RESOURCE_EXHAUSTED" in str(e)) and attempt < 2:
                time.sleep(10)
                continue
            raise


def stream_text(text):
    """간단한 텍스트 스트리밍 (비LLM 결과용)"""
    for char in text:
        yield char
        time.sleep(0.015)


# ==============================================
# Snowflake 연결 (RAG 임베딩 전용)
# ==============================================

@st.cache_resource
def get_snowflake_session():
    return Session.builder.configs(st.secrets["connections"]["snowflake"]).create()


def get_embedding(session, text):
    """벡터 임베딩 생성 (Snowflake EMBED_TEXT_768)"""
    safe_text = text.replace("'", "''").replace("\\", "\\\\")[:2000]
    sql = f"SELECT SNOWFLAKE.CORTEX.EMBED_TEXT_768('snowflake-arctic-embed-m', '{safe_text}')"
    result = session.sql(sql).collect()
    raw = result[0][0]
    return json.loads(raw) if isinstance(raw, str) else list(raw)


# Snowflake 연결 시도 (실패해도 RAG 외 기능은 동작)
try:
    session = get_snowflake_session()
    snowflake_available = True
except Exception:
    snowflake_available = False
    session = None


# ==============================================
# RAG 지식 베이스 (Day 2)
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
    """코사인 유사도 (Day 2)"""
    vec1, vec2 = np.array(vec1), np.array(vec2)
    return float(np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2)))


@st.cache_data
def build_knowledge_embeddings(_session):
    """지식 베이스 벡터 임베딩 (Day 2 + Day 1 캐싱)"""
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
# 제품 데이터 (데이터 분석 도구용)
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
# Agent: 도구 정의 + 선택 + 실행 (Day 3)
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
    },
    {
        "name": "web_search",
        "description": "웹 검색으로 최신 정보 조회. 최신 뉴스, 실시간 정보, 인물/기업 정보, 기술 트렌드, 스포츠 결과 등."
    }
]


def format_history(messages, max_turns=5):
    """최근 대화를 메시지 형식으로 변환 (user/assistant 교대 보장)"""
    recent = messages[-(max_turns * 2):]
    result = []
    for m in recent:
        entry = {"role": m["role"], "content": m["content"]}
        if result and result[-1]["role"] == m["role"]:
            result[-1]["content"] += "\n" + m["content"]
        else:
            result.append(entry)
    return result


def select_tool(user_message, model_name, chat_history=None):
    """Gemini로 도구 선택 (Day 3: Function Calling)"""
    tools_list = TOOLS if snowflake_available else [t for t in TOOLS if t["name"] != "search_knowledge"]
    tools_desc = "\n".join([f"- {t['name']}: {t['description']}" for t in tools_list])

    prompt = f"""사용자 메시지를 분석하고 가장 적합한 도구 하나를 선택하세요.

도구 목록:
{tools_desc}

사용자: "{user_message}"

반드시 아래 JSON 형식으로만 응답:
{{"tool": "도구이름", "param": "핵심 파라미터"}}

JSON:"""

    messages = []
    if chat_history:
        messages.extend(format_history(chat_history, max_turns=2))
    messages.append({"role": "user", "content": prompt})

    result = complete_llm(messages, model_name)

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


def execute_tool(tool_name, param, model_name, system_prompt, chat_history):
    """도구 실행 - LLM 응답은 스트리밍 generator, 비LLM은 문자열 반환"""

    if tool_name == "search_knowledge":
        results = search_knowledge(param, top_k=2)
        context = "\n\n".join([
            f"[{r['title']}] (유사도: {r['score']:.3f})\n{r['content']}"
            for r in results
        ])
        messages = format_history(chat_history)
        messages.append({
            "role": "user",
            "content": f"다음 참고 자료를 바탕으로 질문에 답변하세요.\n\n참고 자료:\n{context}\n\n질문: {param}"
        })
        sources = [f"{r['title']} (유사도: {r['score']:.2f})" for r in results]
        return stream_response(messages, system_prompt, model_name), "search_knowledge", sources

    elif tool_name == "analyze_data":
        df = get_product_data()
        messages = format_history(chat_history)
        messages.append({
            "role": "user",
            "content": f"다음 전자제품 데이터를 분석하여 질문에 답하세요.\n\n{df.to_string()}\n\n질문: {param}"
        })
        return stream_response(messages, system_prompt, model_name), "analyze_data", None

    elif tool_name == "calculator":
        try:
            allowed = set("0123456789+-*/.() ")
            expr = param.replace("^", "**").replace("x", "*").replace("×", "*").replace("÷", "/")
            if all(c in allowed for c in expr):
                result = eval(expr)
                return f"**{param} = {result:,}**", "calculator", None
            else:
                return f"계산할 수 없는 표현식입니다: {param}", "calculator", None
        except Exception as e:
            return f"계산 오류: {e}", "calculator", None

    elif tool_name == "get_time":
        now = datetime.now()
        weekdays = {
            "Monday": "월요일", "Tuesday": "화요일", "Wednesday": "수요일",
            "Thursday": "목요일", "Friday": "금요일", "Saturday": "토요일", "Sunday": "일요일"
        }
        day_kr = weekdays.get(now.strftime("%A"), now.strftime("%A"))
        return f"현재 시간은 **{now.strftime('%Y년 %m월 %d일 %H시 %M분')}** ({day_kr}) 입니다.", "get_time", None

    elif tool_name == "web_search":
        search_tool = types.Tool(google_search=types.GoogleSearch())
        config = types.GenerateContentConfig(
            tools=[search_tool],
            system_instruction=system_prompt
        )
        response = None
        for attempt in range(3):
            try:
                response = client.models.generate_content(
                    model=model_name, contents=param, config=config
                )
                break
            except Exception as e:
                if ("429" in str(e) or "RESOURCE_EXHAUSTED" in str(e)) and attempt < 2:
                    time.sleep(10)
                    continue
                raise
        text = response.text or "검색 결과를 가져올 수 없습니다."
        sources = []
        if response.candidates:
            metadata = response.candidates[0].grounding_metadata
            if metadata and metadata.grounding_chunks:
                for chunk in metadata.grounding_chunks:
                    if chunk.web and chunk.web.uri:
                        title = chunk.web.title or chunk.web.uri
                        sources.append(f"[{title}]({chunk.web.uri})")
        return text, "web_search", sources if sources else None

    else:
        messages = format_history(chat_history)
        messages.append({"role": "user", "content": param})
        return stream_response(messages, system_prompt, model_name), "general_chat", None


# ==============================================
# UI: ChatGPT / Gemini 스타일 채팅 인터페이스
# ==============================================

TOOL_ICONS = {
    "general_chat": "💬",
    "search_knowledge": "🔍",
    "analyze_data": "📊",
    "calculator": "🔢",
    "get_time": "🕐",
    "web_search": "🌐",
}

TOOL_LABELS = {
    "general_chat": "일반 대화",
    "search_knowledge": "지식 검색",
    "analyze_data": "데이터 분석",
    "calculator": "계산기",
    "get_time": "시간 조회",
    "web_search": "웹 검색",
}

# 페이지 설정
st.set_page_config(page_title="AI 어시스턴트", page_icon="🤖", layout="centered")

# Gemini API 클라이언트 생성
try:
    client = get_genai_client()
except Exception:
    st.error("⚠️ Gemini API 키를 설정하세요\n\n`.streamlit/secrets.toml`에 추가:\n```\n[api_keys]\ngoogle = \"AIza...\"\n```\n\n[Google AI Studio](https://aistudio.google.com/apikey)에서 무료 발급")
    st.stop()

# --- 사이드바 ---
with st.sidebar:
    st.markdown("### 설정")

    model_name_display = st.selectbox("모델", list(GEMINI_MODELS.keys()), label_visibility="collapsed")
    model_name = GEMINI_MODELS[model_name_display]

    system_prompt = st.text_area(
        "시스템 프롬프트",
        value="당신은 친절하고 도움이 되는 AI 어시스턴트입니다. 한국어로 간결하게 답변합니다.",
        height=80,
        label_visibility="collapsed"
    )

    st.divider()

    if st.button("새 대화", use_container_width=True, type="primary"):
        st.session_state.messages = []
        st.rerun()

    st.divider()

    st.markdown("**도구**")
    for tool in TOOLS:
        icon = TOOL_ICONS.get(tool["name"], "🔧")
        label = TOOL_LABELS.get(tool["name"], tool["name"])
        if tool["name"] == "search_knowledge" and not snowflake_available:
            st.caption(f"~~{icon} {label}~~ (Snowflake 필요)")
        else:
            st.caption(f"{icon} {label}")

    with st.expander("제품 데이터"):
        st.dataframe(get_product_data(), use_container_width=True, height=200)


# --- 세션 상태 초기화 ---
if "messages" not in st.session_state:
    st.session_state.messages = []


# --- 메인 영역 ---
if not st.session_state.messages:
    st.markdown("")
    st.markdown("")
    st.markdown("<h1 style='text-align: center; color: #666;'>무엇을 도와드릴까요?</h1>", unsafe_allow_html=True)
    st.markdown("")

    # 추천 질문 칩 (2x2 그리드)
    suggestions = [
        ("🔍 RAG가 뭐야?", "RAG가 뭐야?"),
        ("📊 가장 비싼 제품 TOP 3", "가장 비싼 제품 TOP 3 알려줘"),
        ("🔢 1234 * 5678 계산", "1234 * 5678"),
        ("🌐 오늘 주요 뉴스", "오늘 주요 뉴스 알려줘"),
    ]

    cols = st.columns(2)
    for i, (label, query) in enumerate(suggestions):
        with cols[i % 2]:
            if st.button(label, key=f"sug_{i}", use_container_width=True):
                st.session_state.pending_input = query
                st.rerun()

else:
    # 대화가 있을 때: 채팅 히스토리 표시
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

            if msg["role"] == "assistant" and msg.get("tool_name"):
                tn = msg["tool_name"]
                st.caption(f"{TOOL_ICONS.get(tn, '🔧')} {TOOL_LABELS.get(tn, tn)} 사용")

            if msg.get("sources"):
                with st.expander("📚 출처 보기"):
                    for src in msg["sources"]:
                        st.markdown(f"- {src}")


# --- 채팅 입력 ---
pending = st.session_state.pop("pending_input", None)
user_input = st.chat_input("메시지를 입력하세요")

if pending and not user_input:
    user_input = pending

if user_input:
    # 사용자 메시지 저장 + 표시
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # AI 응답
    with st.chat_message("assistant"):
        try:
            # 1. 도구 선택 (대화 맥락 포함)
            with st.spinner("생각하는 중..."):
                history = st.session_state.messages[:-1]
                tool_choice = select_tool(user_input, model_name, history)

            tool_name = tool_choice.get("tool", "general_chat")
            tool_param = tool_choice.get("param", user_input)

            # 2. 도구 실행
            result, used_tool, sources = execute_tool(
                tool_name, tool_param, model_name, system_prompt, history
            )

            # 3. 스트리밍 출력 (LLM: 실시간, 비LLM: 텍스트)
            if isinstance(result, str):
                st.write_stream(stream_text(result))
                full_text = result
            else:
                full_text = st.write_stream(result)

            # 4. 도구 배지
            icon = TOOL_ICONS.get(used_tool, "🔧")
            label = TOOL_LABELS.get(used_tool, used_tool)
            st.caption(f"{icon} {label} 사용")

            # 5. 출처 표시
            if sources:
                with st.expander("📚 출처 보기"):
                    for src in sources:
                        st.markdown(f"- {src}")

        except Exception as e:
            if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                full_text = "API 요청 한도를 초과했습니다. 잠시 후 다시 시도해주세요."
                st.warning(full_text)
            else:
                full_text = f"오류가 발생했습니다: {e}"
                st.error(full_text)
            used_tool = "general_chat"
            sources = None

        # 6. 메시지 저장
        st.session_state.messages.append({
            "role": "assistant",
            "content": full_text,
            "tool_name": used_tool,
            "sources": sources
        })
