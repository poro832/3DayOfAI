"""
Day 3 - Step 1-2: 도구 스키마 파싱 + 실행 (실습)

[학습 목표]
- JSON Schema 기반 도구 정의
- 파라미터 검증
- 안전한 도구 실행

[핵심 개념]
도구를 체계적으로 정의하고, LLM 응답을 파싱하여
안전하게 실행하는 패턴을 학습합니다.
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

st.title("🔧 도구 스키마 & 실행")

with st.expander("💡 도구 스키마(Schema)란?", expanded=True):
    st.markdown("""
    ### JSON Schema로 도구 정의

    ```json
    {
        "name": "get_weather",
        "description": "날씨 정보를 반환합니다",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "도시명"
                }
            },
            "required": ["city"]
        }
    }
    ```

    ### 왜 스키마가 필요한가?
    - **명확한 인터페이스**: 도구가 어떤 입력을 받는지 정의
    - **파라미터 검증**: 잘못된 입력 방지
    - **LLM 가이드**: LLM이 올바른 형식으로 도구 호출
    """)


class ToolRegistry:
    def __init__(self):
        self.tools = {}

    def register(self, name, description, parameters, handler):
        """도구 등록"""
        self.tools[name] = {
            "name": name,
            "description": description,
            "parameters": parameters,
            "handler": handler
        }

    def get_schema(self):
        """LLM에게 보여줄 스키마"""
        # TODO: 각 도구의 name, description, parameters만 추출하여 리스트로 반환
        # 힌트: self.tools.values()를 순회하며 handler를 제외한 정보만 추출
        return []

    def execute(self, tool_name, params):
        """도구 실행"""
        if tool_name not in self.tools:
            return {"error": f"Unknown tool: {tool_name}"}

        tool = self.tools[tool_name]

        required = tool["parameters"].get("required", [])
        for req in required:
            if req not in params:
                return {"error": f"Missing required parameter: {req}"}

        # 실행
        try:
            result = tool["handler"](**params)
            return {"success": True, "result": result}
        except Exception as e:
            return {"error": str(e)}


# 도구 레지스트리 생성
registry = ToolRegistry()


# 도구 구현 및 등록
def get_current_time():
    return datetime.now().strftime("%Y년 %m월 %d일 %H:%M:%S")


def calculate(expression: str):
    allowed = set("0123456789+-*/(). ")
    if not all(c in allowed for c in expression):
        raise ValueError("허용되지 않은 문자")
    return eval(expression)


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


def get_weather(city: str, unit: str = "celsius"):
    coords = CITY_COORDS.get(city)
    temp = None
    condition = "정보없음"
    fallback = False
    if coords:
        try:
            url = f"https://api.open-meteo.com/v1/forecast?latitude={coords[0]}&longitude={coords[1]}&current=temperature_2m,weather_code"
            resp = requests.get(url, timeout=5)
            resp.raise_for_status()
            data = resp.json()["current"]
            temp = data["temperature_2m"]
            condition = WMO_WEATHER.get(data["weather_code"], "알 수 없음")
        except Exception:
            fallback = True
    else:
        fallback = True
    if temp is None:
        temp = 16
        condition = "정보없음"
        fallback = True
    if unit == "fahrenheit":
        temp = temp * 9/5 + 32
    result = f"{city}: {temp}{'°F' if unit == 'fahrenheit' else '°C'}, {condition}"
    if fallback:
        result += " (폴백 데이터)"
    return result


def convert_currency(amount, from_currency: str, to_currency: str):
    amount = float(amount)
    try:
        url = f"https://api.exchangerate-api.com/v4/latest/{from_currency}"
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        rates = resp.json()["rates"]
        if to_currency not in rates:
            raise ValueError("지원하지 않는 통화")
        result = amount * rates[to_currency]
        return f"{amount} {from_currency} = {result:.2f} {to_currency}"
    except Exception:
        # 폴백 환율
        fallback_rates = {"USD": 1, "KRW": 1350, "JPY": 150, "EUR": 0.92}
        if from_currency not in fallback_rates or to_currency not in fallback_rates:
            raise ValueError("지원하지 않는 통화")
        in_usd = amount / fallback_rates[from_currency]
        result = in_usd * fallback_rates[to_currency]
        return f"{amount} {from_currency} = {result:.2f} {to_currency} (폴백 데이터)"


# 도구 등록
registry.register(
    "get_current_time",
    "현재 날짜와 시간을 반환합니다",
    {"type": "object", "properties": {}, "required": []},
    get_current_time
)

registry.register(
    "calculate",
    "수학 계산을 수행합니다",
    {
        "type": "object",
        "properties": {
            "expression": {"type": "string", "description": "계산식 (예: 2+3*4)"}
        },
        "required": ["expression"]
    },
    calculate
)

registry.register(
    "get_weather",
    "도시의 날씨 정보를 반환합니다",
    {
        "type": "object",
        "properties": {
            "city": {"type": "string", "description": "도시명"},
            "unit": {"type": "string", "description": "온도 단위 (celsius/fahrenheit)", "default": "celsius"}
        },
        "required": ["city"]
    },
    get_weather
)

registry.register(
    "convert_currency",
    "환율을 변환합니다",
    {
        "type": "object",
        "properties": {
            "amount": {"type": "number", "description": "금액"},
            "from_currency": {"type": "string", "description": "원래 통화 (USD, KRW, JPY, EUR)"},
            "to_currency": {"type": "string", "description": "변환할 통화"}
        },
        "required": ["amount", "from_currency", "to_currency"]
    },
    convert_currency
)


def call_with_tools(user_input):
    """LLM으로 도구 호출 결정 및 실행"""
    schema = registry.get_schema()
    schema_str = json.dumps(schema, ensure_ascii=False, indent=2)

    prompt = f"""당신은 사용자 요청을 분석하여 도구를 호출하는 AI입니다.

사용 가능한 도구:
{schema_str}

사용자: "{user_input}"

응답 형식 (JSON만):
- 도구 호출: {{"tool": "도구명", "params": {{...}}}}
- 직접 답변: {{"tool": null, "answer": "답변"}}

JSON:"""

    response = complete_llm(session, "llama3.1-70b", prompt)

    # JSON 파싱
    try:
        json_start = response.find('{')
        json_end = response.rfind('}') + 1
        if json_start >= 0 and json_end > json_start:
            return json.loads(response[json_start:json_end])
    except json.JSONDecodeError:
        pass

    return {"tool": None, "answer": response}


# UI
st.write("### 📋 등록된 도구")
for tool in registry.get_schema():
    with st.expander(f"**{tool['name']}**: {tool['description']}"):
        st.json(tool["parameters"])

st.divider()

# 예시
st.write("### 💡 예시 질문")
examples = [
    "지금 몇 시야?",
    "123 * 456 계산해줘",
    "서울 날씨 화씨로 알려줘",
    "100 달러를 원화로 바꾸면?",
    "1000 엔은 몇 유로야?"
]
selected_example = st.selectbox("예시 선택", ["직접 입력"] + examples)

if selected_example == "직접 입력":
    user_input = st.text_input("질문", placeholder="질문을 입력하세요")
else:
    user_input = st.text_input("질문", value=selected_example)

if user_input and st.button("🚀 실행"):
    # 1. LLM 결정
    with st.spinner("분석 중..."):
        decision = call_with_tools(user_input)

    # 2. 사고 과정
    with st.expander("🧠 Agent 사고 과정", expanded=True):
        st.write("**입력:**", user_input)
        st.write("**LLM 결정:**")
        st.json(decision)

    # 3. 도구 실행
    if decision.get("tool"):
        tool_name = decision["tool"]
        params = decision.get("params", {})

        st.write(f"**도구 호출:** `{tool_name}({params})`")

        result = registry.execute(tool_name, params)

        if result.get("success"):
            st.success(f"✅ 결과: {result['result']}")
        else:
            st.error(f"❌ 오류: {result['error']}")
    else:
        st.write("### 💬 답변")
        st.write(decision.get("answer", "응답 없음"))
