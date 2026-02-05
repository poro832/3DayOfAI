# Day 1 - Step 3: 인터랙티브 위젯

---

## 🎯 학습 목표

다양한 Streamlit 위젯으로 인터랙티브한 UI 구성

---

## 📚 실습 목록 (3개)

### app_3_1.py: 온도 조절 챗봇

### app_3_2.py: 모델 선택 챗봇

### app_3_3.py: 사이드바 활용

---

## 💡 핵심 개념

### Streamlit 위젯

```python
# 슬라이더
temperature = st.slider("Temperature", 0.0, 1.0, 0.7)

# 셀렉트박스
model = st.selectbox("모델", ["llama3.1-70b", "mixtral-8x7b"])

# 체크박스
detailed = st.checkbox("상세한 설명 포함")

# 사이드바
with st.sidebar:
    st.write("### 설정")
```

### Temperature 시뮬레이션

Snowflake Cortex SQL 방식은 temperature를 직접 지원하지 않아 프롬프트로 창의성을 조절:

```python
if temperature < 0.3:
    style = "정확하고 간결하게 답변하세요."
elif temperature >= 0.7:
    style = "창의적이고 다양한 관점에서 답변하세요."
```

---

## 📖 실습 가이드

### 진행 방법

```bash
cd problems/Day1
streamlit run app_3_1.py
```

---

## 🎓 상세 실습 내용

### 실습 1: 온도 조절 챗봇

**파일**: `app_3_1.py`

**목표**: 슬라이더로 응답 스타일 조절

**핵심 코드**:
```python
import streamlit as st
from snowflake.snowpark import Session

@st.cache_resource
def get_snowflake_session():
    connection_parameters = st.secrets["connections"]["snowflake"]
    return Session.builder.configs(connection_parameters).create()

def complete_llm(session, model, prompt):
    escaped_prompt = prompt.replace("'", "''")
    sql = f"SELECT SNOWFLAKE.CORTEX.COMPLETE('{model}', '{escaped_prompt}')"
    result = session.sql(sql).collect()
    return result[0][0]

session = get_snowflake_session()

st.title("🎚️ 온도 조절 챗봇")

temperature = st.slider("Temperature (창의성)", 0.0, 1.0, 0.7)
st.write(f"현재 Temperature: {temperature}")

user_question = st.text_input("질문을 입력하세요")

if user_question:
    # temperature에 따라 프롬프트 스타일 조정
    if temperature < 0.3:
        style = "정확하고 간결하게 답변하세요."
    elif temperature < 0.7:
        style = "명확하게 답변하세요."
    else:
        style = "창의적이고 다양한 관점에서 답변하세요."

    prompt = f"{user_question}\n\n({style})"

    with st.spinner("생각하는 중..."):
        response = complete_llm(session, "llama3.1-70b", prompt)

    st.write("### AI 답변")
    st.write(response)
```

**체크포인트**:
- [ ] st.slider() 구현 완료
- [ ] temperature에 따른 프롬프트 분기 완료

---

### 실습 2: 모델 선택 챗봇

**파일**: `app_3_2.py`

**목표**: 셀렉트박스와 체크박스로 옵션 선택

**핵심 코드**:
```python
import streamlit as st
from snowflake.snowpark import Session

@st.cache_resource
def get_snowflake_session():
    connection_parameters = st.secrets["connections"]["snowflake"]
    return Session.builder.configs(connection_parameters).create()

def complete_llm(session, model, prompt):
    escaped_prompt = prompt.replace("'", "''")
    sql = f"SELECT SNOWFLAKE.CORTEX.COMPLETE('{model}', '{escaped_prompt}')"
    result = session.sql(sql).collect()
    return result[0][0]

session = get_snowflake_session()

st.title("🤖 모델 선택 챗봇")

selected_model = st.selectbox(
    "모델 선택",
    ["llama3.1-70b", "llama3.1-405b", "mixtral-8x7b"]
)

detailed = st.checkbox("상세한 설명 포함")

user_question = st.text_input("질문을 입력하세요")

if user_question:
    prompt = user_question
    if detailed:
        prompt = f"{user_question}\n\n상세하고 구체적으로 설명해주세요."

    with st.spinner("생각하는 중..."):
        response = complete_llm(session, selected_model, prompt)

    st.write("### AI 답변")
    st.write(response)
```

**체크포인트**:
- [ ] st.selectbox() 구현 완료
- [ ] st.checkbox() 구현 완료

---

### 실습 3: 사이드바 활용

**파일**: `app_3_3.py`

**목표**: 사이드바에 설정 옵션 배치

**핵심 코드**:
```python
import streamlit as st
from snowflake.snowpark import Session

@st.cache_resource
def get_snowflake_session():
    connection_parameters = st.secrets["connections"]["snowflake"]
    return Session.builder.configs(connection_parameters).create()

def complete_llm(session, model, prompt):
    escaped_prompt = prompt.replace("'", "''")
    sql = f"SELECT SNOWFLAKE.CORTEX.COMPLETE('{model}', '{escaped_prompt}')"
    result = session.sql(sql).collect()
    return result[0][0]

session = get_snowflake_session()

st.title("⚙️ 설정 가능한 챗봇")

with st.sidebar:
    st.write("### ⚙️ 설정")
    model = st.selectbox("모델 선택", ["llama3.1-70b", "mixtral-8x7b"])
    temperature = st.slider("Temperature", 0.0, 1.0, 0.7)
    detailed = st.checkbox("상세한 설명 포함")

user_question = st.text_input("질문을 입력하세요")

if user_question:
    prompt = user_question
    if detailed:
        prompt += "\n\n상세하고 구체적으로 설명해주세요."
    if temperature < 0.3:
        prompt += "\n(정확하고 간결하게 답변하세요.)"
    elif temperature >= 0.7:
        prompt += "\n(창의적이고 다양한 관점에서 답변하세요.)"

    with st.spinner("생각하는 중..."):
        response = complete_llm(session, model, prompt)

    st.write("### AI 답변")
    st.write(response)
```

**체크포인트**:
- [ ] st.sidebar 사용 완료
- [ ] 모든 설정 옵션 사이드바로 이동 완료

---

## ✅ 완료 체크리스트

- [ ] app_3_1.py - 온도 조절 챗봇 완료
- [ ] app_3_2.py - 모델 선택 챗봇 완료
- [ ] app_3_3.py - 사이드바 활용 완료

---

## 🔗 관련 문서

- [Streamlit Widgets](https://docs.streamlit.io/library/api-reference/widgets)
- [Snowflake Cortex AI](https://docs.snowflake.com/en/user-guide/snowflake-cortex)

---

**다음 단계**: [Day 1 - Step 4: 세션 상태 & 채팅 UI] →
