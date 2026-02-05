# Day 3 - Step 3: 다중 도구 Agent

---

## 🎯 학습 목표

여러 도구를 가진 Agent를 구현하고 사용자 의도에 따라 적절한 도구 선택

---

## 📚 실습 목록 (1개)

### app_3_1.py: 다중 도구 Agent

---

## 💡 핵심 개념

### 다중 도구 정의

```python
tools = [
    {
        "function": {
            "name": "get_time",
            "description": "현재 시간을 반환합니다"
        }
    },
    {
        "function": {
            "name": "calculate",
            "description": "수학 계산을 수행합니다",
            "parameters": {
                "properties": {
                    "expression": {"type": "string"}
                }
            }
        }
    },
    {
        "function": {
            "name": "get_weather",
            "description": "날씨를 조회합니다"
        }
    }
]
```

### 도구 라우팅

사용자 의도에 따라 적절한 도구로 분기:
```python
if "시간" in user_input:
    result = execute_tool("get_time")
elif "계산" in user_input:
    result = execute_tool("calculate", {"expression": expr})
elif "날씨" in user_input:
    result = execute_tool("get_weather", {"city": city})
else:
    result = complete_llm(...)  # LLM 직접 응답
```

---

## ⚠️ 참고 사항

| 이 실습 | 실제 Agent 시스템 |
|---------|------------------|
| if-elif 분기로 도구 선택 | LLM이 tools 배열의 description을 분석하여 자율 선택 |
| 키워드 매칭 | 의미 기반 이해 |

---

## 📖 실습 가이드

### 진행 방법

```bash
cd problems/Day3
streamlit run app_3_1.py
```

---

## 🎓 상세 실습 내용

### 실습: 다중 도구 Agent

**파일**: `app_3_1.py`

**목표**: 시간, 계산, 날씨 3가지 도구를 가진 Agent 구현

**핵심 코드**:
```python
import streamlit as st
from snowflake.snowpark import Session
from datetime import datetime

def get_snowflake_session():
    connection_parameters = st.secrets["connections"]["snowflake"]
    return Session.builder.configs(connection_parameters).create()

def complete_llm(session, model, prompt):
    escaped_prompt = prompt.replace("'", "''")
    sql = f"SELECT SNOWFLAKE.CORTEX.COMPLETE('{model}', '{escaped_prompt}')"
    result = session.sql(sql).collect()
    return result[0][0]

session = get_snowflake_session()

st.title("🛠️ 다중 도구 Agent")

# 여러 도구 정의
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_time",
            "description": "현재 시간을 반환합니다",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "수학 계산을 수행합니다",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {"type": "string", "description": "계산식"}
                },
                "required": ["expression"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "날씨를 조회합니다",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "도시명"}
                },
                "required": ["city"]
            }
        }
    }
]

def get_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def calculate(expression):
    try:
        allowed = set("0123456789+-*/(). ")
        if all(c in allowed for c in expression):
            return str(eval(expression))
        return "허용되지 않은 문자가 포함되어 있습니다"
    except:
        return "계산 오류"

def get_weather(city):
    weather_data = {
        "서울": "15°C, 맑음",
        "부산": "18°C, 구름 조금",
        "제주": "20°C, 흐림"
    }
    return weather_data.get(city, "16°C, 정보 없음")

def execute_tool(tool_name, args=None):
    if tool_name == "get_time":
        return f"⏰ 현재 시간: {get_time()}"
    elif tool_name == "calculate":
        result = calculate(args.get("expression", "0"))
        return f"🧮 계산 결과: {result}"
    elif tool_name == "get_weather":
        city = args.get("city", "서울")
        return f"🌤️ {city} 날씨: {get_weather(city)}"
    return "알 수 없는 도구"

st.write("### 사용 가능한 도구")
st.write("- ⏰ 시간 조회: \"지금 몇 시야?\"")
st.write("- 🧮 계산기: \"123 * 456 계산해줘\"")
st.write("- 🌤️ 날씨 조회: \"서울 날씨 어때?\"")

user_input = st.text_input("질문", "지금 몇 시야?")

if user_input and st.button("실행"):
    with st.spinner("Agent 실행 중..."):
        # 키워드 기반 도구 선택
        if any(word in user_input for word in ["시간", "몇 시"]):
            result = execute_tool("get_time")
        elif any(word in user_input for word in ["계산", "+", "-", "*", "/"]):
            import re
            nums = re.findall(r'[\d\+\-\*\/\(\)\.\s]+', user_input)
            expression = ''.join(nums).strip() if nums else "0"
            result = execute_tool("calculate", {"expression": expression})
        elif any(word in user_input for word in ["날씨", "기온", "온도"]):
            cities = ["서울", "부산", "제주", "대구", "인천"]
            city = next((c for c in cities if c in user_input), "서울")
            result = execute_tool("get_weather", {"city": city})
        else:
            result = complete_llm(session, "llama3.1-70b", user_input)

    st.write("### 결과")
    st.write(result)
```

**테스트 시나리오**:

| 입력 | 선택되는 도구 | 결과 |
|------|--------------|------|
| "지금 몇 시야?" | get_time | 2024-01-15 14:30:00 |
| "100 + 200 계산해줘" | calculate | 300 |
| "서울 날씨" | get_weather | 15°C, 맑음 |
| "파이썬이 뭐야?" | (없음) | LLM 직접 응답 |

**체크포인트**:
- [ ] 3개 도구 정의 완료
- [ ] 도구 라우팅 로직 완료
- [ ] 각 도구 실행 테스트 완료

---

## ✅ 완료 체크리스트

- [ ] app_3_1.py - 다중 도구 Agent 완료

---

**다음 단계**: [Day 3 - Step 4: 데이터 분석 Agent] →
