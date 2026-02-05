# Day 3 - Step 2: 날씨 조회 Agent

---

## 🎯 학습 목표

파라미터가 있는 도구 정의 및 사용자 입력에서 파라미터 추출

---

## 📚 실습 목록 (1개)

### app_2_1.py: 날씨 조회 Agent

---

## 💡 핵심 개념

### 파라미터가 있는 도구

```python
tools = [{
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "도시의 현재 날씨를 반환합니다",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "도시 이름 (예: 서울, 부산)"
                }
            },
            "required": ["city"]  # 필수 파라미터
        }
    }
}]
```

### 파라미터 추출

사용자 입력에서 도시명을 추출하여 함수에 전달:
```python
cities = ["서울", "부산", "제주", "대구", "인천"]
found_city = None
for city in cities:
    if city in user_input:
        found_city = city
        break
```

---

## ⚠️ 참고 사항

- 날씨 데이터: **하드코딩된 샘플** (실제 API 아님)
- 도구 선택: **키워드 매칭** (LLM 자율 선택 아님)

실제 프로덕션에서는 OpenWeatherMap 등 외부 API 연동 필요

---

## 📖 실습 가이드

### 진행 방법

```bash
cd problems/Day3
streamlit run app_2_1.py
```

---

## 🎓 상세 실습 내용

### 실습: 날씨 조회 Agent

**파일**: `app_2_1.py`

**목표**: "서울 날씨 어때?"라고 물으면 서울 날씨 정보 반환

**핵심 코드**:
```python
import streamlit as st
from snowflake.snowpark import Session

def get_snowflake_session():
    connection_parameters = st.secrets["connections"]["snowflake"]
    return Session.builder.configs(connection_parameters).create()

def complete_llm(session, model, prompt):
    escaped_prompt = prompt.replace("'", "''")
    sql = f"SELECT SNOWFLAKE.CORTEX.COMPLETE('{model}', '{escaped_prompt}')"
    result = session.sql(sql).collect()
    return result[0][0]

session = get_snowflake_session()

st.title("🌤️ 날씨 조회 Agent")

# 도구 정의
tools = [{
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "도시의 현재 날씨를 반환합니다",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "도시 이름 (예: 서울, 부산)"
                }
            },
            "required": ["city"]
        }
    }
}]

def get_weather(city):
    """도시별 날씨 반환 (시뮬레이션)"""
    weather_data = {
        "서울": {"temp": 15, "condition": "맑음"},
        "부산": {"temp": 18, "condition": "구름 조금"},
        "제주": {"temp": 20, "condition": "흐림"},
        "대구": {"temp": 17, "condition": "맑음"},
        "인천": {"temp": 14, "condition": "안개"}
    }
    return weather_data.get(city, {"temp": 16, "condition": "정보 없음"})

user_input = st.text_input("질문", "서울 날씨 어때?")

if user_input and st.button("실행"):
    with st.spinner("Agent 실행 중..."):
        # 도시명 추출 (간단한 방식)
        cities = ["서울", "부산", "제주", "대구", "인천"]
        found_city = None
        for city in cities:
            if city in user_input:
                found_city = city
                break

        if found_city:
            weather = get_weather(found_city)
            st.write(f"### 🌤️ {found_city} 날씨")
            st.write(f"🌡️ 온도: {weather['temp']}°C")
            st.write(f"☁️ 상태: {weather['condition']}")
        else:
            response = complete_llm(session, "llama3.1-70b", user_input)
            st.write(response)
```

**샘플 데이터**:
```python
weather_data = {
    "서울": {"temp": 15, "condition": "맑음"},
    "부산": {"temp": 18, "condition": "구름 조금"},
    "제주": {"temp": 20, "condition": "흐림"},
    "대구": {"temp": 17, "condition": "맑음"},
    "인천": {"temp": 14, "condition": "안개"}
}
```

**테스트 입력**:
- "서울 날씨 어때?" → 서울: 15°C, 맑음
- "부산 날씨 알려줘" → 부산: 18°C, 구름 조금
- "파이썬이 뭐야?" → LLM 직접 응답

**체크포인트**:
- [ ] 도구 정의 (파라미터 포함) 완료
- [ ] 도시명 추출 완료
- [ ] 날씨 정보 반환 완료

---

## ✅ 완료 체크리스트

- [ ] app_2_1.py - 날씨 조회 Agent 완료

---

**다음 단계**: [Day 3 - Step 3: 다중 도구 Agent] →
