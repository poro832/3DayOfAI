# Day 3: Agent & 배포

**기간**: Day 23-30  
**목표**: Function Calling으로 지능형 에이전트를 구축하고 실제 배포

---

## 🎯 학습 목표

1. **Function Calling 기초** - LLM이 도구를 사용하게 만들기
2. **날씨 Agent** - 외부 API 연동
3. **다중 도구 Agent** - 복잡한 작업 수행
4. **데이터 분석 Agent** - CSV 데이터 분석
5. **배포** - Streamlit Cloud에 앱 배포

---

## 📚 실습 구성 (총 5개)

- **app_1_1.py** - Function Calling 기초
- **app_2_1.py** - 날씨 조회 Agent
- **app_3_1.py** - 다중 도구 Agent
- **app_4_1.py** - 데이터 분석 Agent
- **app_5_1.py** - 배포 준비

---

## 💡 핵심 개념

### Function Calling

LLM이 직접 할 수 없는 작업(날씨 조회, 계산, DB 쿼리 등)을 함수로 정의하고 호출하게 하는 기술

### 도구 정의

```python
tools = [{
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "날씨 정보를 반환합니다",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {"type": "string"}
            }
        }
    }
}]
```

---

## ✅ 완료 체크리스트

- [ ] Function Calling 기초
- [ ] 날씨 Agent 구현
- [ ] 다중 도구 Agent 구현
- [ ] 데이터 분석 Agent 구현
- [ ] Streamlit Cloud 배포

---

## 🚀 시작하기

**다음**: [Day 3 실습 시작] →
