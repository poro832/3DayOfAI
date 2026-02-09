"""
Day 3 - Step 2-2: 멀티턴 Agent + 사고과정 시각화 (실습)

[학습 목표]
- 멀티턴 대화 Agent
- Agent 사고 과정 시각화
- 상태 관리

[핵심 개념]
Agent가 여러 단계를 거쳐 문제를 해결하는 과정을 시각화합니다.
"""

import streamlit as st
import json
import requests
from datetime import datetime
from snowflake.snowpark import Session


def get_snowflake_session():
    connection_parameters = st.secrets["connections"]["snowflake"]
    return Session.builder.configs(connection_parameters).create()


def complete_llm(session, model, prompt):
    escaped_prompt = prompt.replace("'", "''")
    sql = f"SELECT SNOWFLAKE.CORTEX.COMPLETE('{model}', '{escaped_prompt}')"
    result = session.sql(sql).collect()
    return result[0][0]


try:
    session = get_snowflake_session()
except Exception as e:
    st.error(f"Snowflake 연결 실패: {e}")
    st.stop()

st.title("🧠 멀티턴 Agent + 사고과정")

with st.expander("💡 Agent 사고과정이란?", expanded=False):
    st.markdown("""
    ### Agent의 추론 단계

    1. **입력 분석**: 사용자가 무엇을 원하는지 파악
    2. **계획 수립**: 어떤 도구를 어떤 순서로 사용할지 결정
    3. **도구 실행**: 선택한 도구를 파라미터와 함께 호출
    4. **결과 해석**: 도구 결과를 사용자에게 설명
    5. **다음 단계**: 추가 작업이 필요한지 판단
    """)

CITY_COORDS = {
    "서울": (37.57, 126.98), "부산": (35.18, 129.08),
    "인천": (37.46, 126.71), "대구": (35.87, 128.60),
    "대전": (36.35, 127.38), "광주": (35.16, 126.85),
    "제주": (33.50, 126.53), "수원": (37.26, 127.03),
    "성남": (37.42, 127.13), "울산": (35.54, 129.31)
}

WMO_WEATHER = {
    0: "맑음", 1: "대체로 맑음", 2: "부분적 흐림", 3: "흐림",
    45: "안개", 48: "안개", 51: "이슬비", 53: "이슬비", 55: "이슬비",
    61: "비", 63: "비", 65: "폭우", 71: "눈", 73: "눈", 75: "폭설",
    80: "소나기", 81: "소나기", 82: "폭우", 95: "뇌우"
}


def get_weather_api(city):
    """Open-Meteo API로 실시간 날씨 조회"""
    coords = CITY_COORDS.get(city)
    if coords:
        try:
            url = f"https://api.open-meteo.com/v1/forecast?latitude={coords[0]}&longitude={coords[1]}&current=temperature_2m,relative_humidity_2m,weather_code"
            resp = requests.get(url, timeout=5)
            resp.raise_for_status()
            data = resp.json()["current"]
            temp = data["temperature_2m"]
            humidity = data["relative_humidity_2m"]
            condition = WMO_WEATHER.get(data["weather_code"], "알 수 없음")
            return f"{city}: {temp}°C, {condition}, 습도 {humidity}%"
        except Exception:
            pass
    return f"{city}: 16°C, 정보 없음 (폴백 데이터)"


def search_info_api(query):
    """Wikipedia API로 정보 검색"""
    try:
        url = f"https://ko.wikipedia.org/api/rest_v1/page/summary/{requests.utils.quote(query)}"
        headers = {"User-Agent": "3DaysOfAI/1.0 (Streamlit education app)"}
        resp = requests.get(url, headers=headers, timeout=5)
        resp.raise_for_status()
        data = resp.json()
        extract = data.get("extract", "")
        if extract:
            return extract[:300]
    except Exception:
        pass
    return f"'{query}'에 대한 검색 결과를 가져올 수 없습니다 (폴백 데이터)"


# 도구 정의
TOOLS = {
    "get_time": {"desc": "현재 시간", "handler": lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S")},
    "calculate": {"desc": "수학 계산", "handler": lambda expr: str(eval(expr)) if all(c in "0123456789+-*/(). " for c in expr) else "오류"},
    "get_weather": {"desc": "날씨 조회", "handler": get_weather_api},
    "search_info": {"desc": "정보 검색 (Wikipedia)", "handler": search_info_api}
}

# TODO 1: 세션 상태 초기화
# agent_messages: 대화 히스토리
# thinking_steps: 사고 과정 기록
if "agent_messages" not in st.session_state:
    st.session_state.agent_messages = []
if "thinking_steps" not in st.session_state:
    st.session_state.thinking_steps = []


def think_and_act(user_input, history):
    """Agent 사고 및 행동"""
    thinking = []

    # TODO 2: Step 1 - 입력 분석 기록 (1줄)
    # 힌트: thinking.append({"step": "입력 분석", "content": f"사용자 요청: '{user_input}'"})
    pass  # TODO를 완성하세요

    # Step 2: 도구 선택
    tools_desc = ", ".join([f"{k}({v['desc']})" for k, v in TOOLS.items()])
    decide_prompt = f"""이전 대화:
{history}

사용자: "{user_input}"

도구: {tools_desc}

JSON 응답: {{"thought": "생각", "tool": "도구명 또는 null", "params": {{}}, "answer": "직접답변(도구 없을 때)"}}"""

    response = complete_llm(session, "llama3.1-70b", decide_prompt)

    try:
        json_start = response.find('{')
        json_end = response.rfind('}') + 1
        decision = json.loads(response[json_start:json_end])
    except:
        decision = {"thought": "파싱 실패", "tool": None, "answer": response}

    # TODO 3: 추론과 결정을 thinking에 기록 (2줄)
    # 힌트: thinking.append({"step": "추론", "content": decision.get("thought", "")})
    #       thinking.append({"step": "결정", "content": f"도구: {decision.get('tool', 'None')}"})
    pass  # TODO를 완성하세요

    # Step 3: 도구 실행
    if decision.get("tool") and decision["tool"] in TOOLS:
        tool_name = decision["tool"]
        params = decision.get("params", {})

        # TODO 4: 도구 호출 기록 (1줄)
        # 힌트: thinking.append({"step": "도구 호출", "content": f"{tool_name}({params})"})
        pass  # TODO를 완성하세요

        try:
            handler = TOOLS[tool_name]["handler"]
            if params:
                result = handler(list(params.values())[0])
            else:
                result = handler()
            thinking.append({"step": "결과", "content": result})

            # 결과를 자연어로 변환
            final_prompt = f"도구 {tool_name} 결과: {result}\n\n이 결과를 사용자 질문 '{user_input}'에 맞게 자연어로 답변하세요."
            answer = complete_llm(session, "llama3.1-70b", final_prompt)
        except Exception as e:
            answer = f"도구 실행 오류: {e}"
    else:
        answer = decision.get("answer", response)

    thinking.append({"step": "최종 답변", "content": answer})

    return answer, thinking


# 대화 히스토리 표시
for msg in st.session_state.agent_messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        if "thinking" in msg:
            with st.expander("🧠 사고 과정"):
                for step in msg["thinking"]:
                    st.markdown(f"**{step['step']}**: {step['content']}")

# 입력
user_input = st.chat_input("질문하세요...")

if user_input:
    # 사용자 메시지
    st.session_state.agent_messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    # 히스토리
    history = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.agent_messages[-5:]])

    # Agent 실행
    with st.chat_message("assistant"):
        with st.spinner("🤔 생각 중..."):
            answer, thinking = think_and_act(user_input, history)

        st.write(answer)

        # TODO 5: 단계별 색상 적용 (4줄)
        # 힌트: 추론 → st.info(), 도구 호출 → st.warning(), 결과 → st.success(), 기타 → st.write()
        with st.expander("🧠 사고 과정", expanded=True):
            for step in thinking:
                if step["step"] == "추론":
                    st.info(f"💭 **{step['step']}**: {step['content']}")
                elif step["step"] == "도구 호출":
                    st.warning(f"🔧 **{step['step']}**: {step['content']}")
                elif step["step"] == "결과":
                    pass  # TODO: st.success()로 표시
                else:
                    pass  # TODO: st.write()로 표시

    st.session_state.agent_messages.append({
        "role": "assistant",
        "content": answer,
        "thinking": thinking
    })

# 사이드바
with st.sidebar:
    st.write("### 💡 예시 질문")
    st.write("- 지금 몇 시야?")
    st.write("- 123 * 456 계산해줘")
    st.write("- 서울 날씨 어때?")
    st.write("- 그리고 부산 날씨도 알려줘 (멀티턴)")

    if st.button("🗑️ 대화 초기화"):
        st.session_state.agent_messages = []
        st.rerun()
