# Day 3 - Step 1: Function Calling 기초

---

## 🎯 학습 목표

Agent의 기본 개념인 도구 정의와 도구 선택 패턴 이해

---

## 📚 실습 목록 (1개)

### app_1_1.py: 시간 조회 Agent

---

## 💡 핵심 개념

### Agent란?

LLM이 단순 텍스트 생성을 넘어 **도구(함수)를 선택하고 실행**하여 작업을 수행하는 시스템

### Agent의 구성 요소

1. **도구 정의** - 사용 가능한 함수 목록
2. **도구 선택** - 사용자 요청에 맞는 도구 결정
3. **도구 실행** - 선택된 도구 호출 및 결과 반환

### 도구 정의 형식

```python
tools = [{
    "type": "function",
    "function": {
        "name": "get_current_time",
        "description": "현재 시간을 반환합니다",
        "parameters": {"type": "object", "properties": {}}
    }
}]
```

---

## ⚠️ 참고 사항

이 실습은 **Agent 개념 학습을 위한 시뮬레이션**입니다.

| 구분 | 이 실습 | 실제 Cortex Agents |
|------|---------|-------------------|
| 도구 선택 | 키워드 매칭 (if-elif) | LLM이 자율적으로 선택 |
| 실행 방식 | 직접 함수 호출 | API가 자동 처리 |

> **비전공자를 위한 설명**
> - 실제 Agent는 AI가 "이 질문에는 날씨 도구가 필요하겠군"이라고 스스로 판단합니다
> - 이 실습에서는 "날씨"라는 단어가 있으면 날씨 도구를 사용하는 간단한 방식으로 학습합니다
> - 핵심 개념(도구 정의 → 선택 → 실행)은 동일합니다!

실제 Cortex Agents: [공식 문서](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-agents)

---

## 📖 실습 가이드

### 진행 방법

```bash
cd problems/Day3
streamlit run app_1_1.py
```

---

## 🎓 상세 실습 내용

### 실습: 시간 조회 Agent

**파일**: `app_1_1.py`

**목표**: 사용자가 "지금 몇 시야?"라고 물으면 현재 시간을 반환

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

st.title("🕐 시간 조회 Agent")

# 도구 정의
tools = [{
    "type": "function",
    "function": {
        "name": "get_current_time",
        "description": "현재 시간을 반환합니다",
        "parameters": {"type": "object", "properties": {}}
    }
}]

def get_current_time():
    """현재 시간 반환"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

user_input = st.text_input("질문", "지금 몇 시야?")

if user_input and st.button("실행"):
    # 시간 관련 키워드 확인
    time_keywords = ["시간", "몇 시", "몇시", "time", "시계"]
    is_time_query = any(kw in user_input.lower() for kw in time_keywords)

    if is_time_query:
        result = get_current_time()
        st.write(f"⏰ 현재 시간: {result}")
    else:
        response = complete_llm(session, "llama3.1-70b", user_input)
        st.write(response)
```

**테스트 입력**:
- "지금 몇 시야?" → 시간 도구 실행
- "안녕하세요" → LLM 직접 응답

**체크포인트**:
- [ ] 도구 정의 완료
- [ ] 키워드 매칭 구현 완료
- [ ] 도구 실행 완료

---

## ✅ 완료 체크리스트

- [ ] app_1_1.py - 시간 조회 Agent 완료

---

**다음 단계**: [Day 3 - Step 2: 날씨 조회 Agent] →
