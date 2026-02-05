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
| 도구 선택 | 키워드 매칭 | LLM 자율 선택 |
| 실행 방식 | if-elif 분기 | API 자동 처리 |

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

**구현 흐름**:
```
사용자 입력 → 키워드 확인 → 도구 선택 → 함수 실행 → 결과 표시
```

**핵심 코드**:
```python
# 도구 함수 정의
def get_current_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# 키워드 기반 도구 선택
time_keywords = ["시간", "몇 시", "time"]
if any(kw in user_input for kw in time_keywords):
    result = get_current_time()
    st.write(f"⏰ 현재 시간: {result}")
else:
    # LLM에게 직접 답변 요청
    response = complete_llm(session, "llama3.1-70b", user_input)
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
