# Day 1: Streamlit & LLM 기초

**기간**: Day 1-12  
**목표**: Snowflake Cortex AI를 연결하고 첫 LLM 호출부터 완성형 챗봇까지 구축

---

## 🎯 학습 목표

1. **Snowflake 연결** - secrets.toml로 안전한 연결 설정
2. **LLM 호출** - Cortex AI로 첫 AI 응답 받기
3. **스트리밍 & 캐싱** - 사용자 경험과 성능 최적화
4. **위젯 활용** - 인터랙티브한 UI 구성
5. **세션 상태** - 대화 히스토리 관리
6. **채팅 UI** - 실제 챗봇 인터페이스 완성

---

## 📚 실습 구성 (총 11개)

### Step 1: Snowflake 연결 및 LLM 호출 (2개)
- **app_1_1.py** - Snowflake 연결 설정
- **app_1_2.py** - 첫 LLM 호출

### Step 2: 성능 최적화 (2개)
- **app_2_1.py** - 스트리밍 응답 구현
- **app_2_2.py** - 캐싱으로 성능 개선

### Step 3: 인터랙티브 위젯 (3개)
- **app_3_1.py** - 온도 조절 챗봇
- **app_3_2.py** - 모델 선택 챗봇
- **app_3_3.py** - 사이드바 활용

### Step 4: 세션 상태 & 채팅 UI (2개)
- **app_4_1.py** - 세션 상태 기초
- **app_4_2.py** - 채팅 UI 만들기

### Step 5: 완성형 챗봇 (2개)
- **app_5_1.py** - 컨텍스트 챗봇 구현
- **app_5_2.py** - 시스템 프롬프트 추가

---

## 🗺️ 학습 로드맵

```
Step 1: 연결 설정 → Step 2: 최적화 → Step 3: 위젯 
    ↓                                        ↓
Step 5: 완성 ← Step 4: 채팅 UI ←──────────┘
```

---

## 💡 핵심 개념

### Snowflake Cortex AI
```python
# SQL 방식으로 LLM 호출 (권장)
def complete_llm(session, model, prompt):
    escaped_prompt = prompt.replace("'", "''")
    sql = f"SELECT SNOWFLAKE.CORTEX.COMPLETE('{model}', '{escaped_prompt}')"
    return session.sql(sql).collect()[0][0]

response = complete_llm(session, "mistral-7b", "질문")
```

### Streamlit 기본 위젯
```python
st.title("제목")
st.text_input("입력")
st.button("버튼")
st.slider("슬라이더")
st.selectbox("선택")
```

### 세션 상태
```python
if "messages" not in st.session_state:
    st.session_state.messages = []

st.session_state.messages.append(new_message)
```

### 채팅 UI
```python
with st.chat_message("user"):
    st.write(message)

user_input = st.chat_input("입력...")
```

---

## ✅ 완료 체크리스트

- [ ] Step 1: Snowflake 연결 및 LLM 호출
- [ ] Step 2: 스트리밍 & 캐싱
- [ ] Step 3: 위젯 활용
- [ ] Step 4: 세션 상태 & 채팅 UI
- [ ] Step 5: 완성형 챗봇

---

## 🚀 시작하기

**다음**: [Step 1 - Snowflake 연결 및 LLM 호출] →
