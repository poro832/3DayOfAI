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

**사용 가능한 도구**:
- ⏰ **시간 조회**: "지금 몇 시야?"
- 🧮 **계산기**: "123 * 456 계산해줘"
- 🌤️ **날씨 조회**: "서울 날씨 어때?"

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
