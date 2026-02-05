# Day 1 - Step 2: 스트리밍 & 캐싱

---

## 🎯 학습 목표

사용자 경험과 성능을 동시에 개선하기

---

## 📚 실습 목록 (2개)

### app_2_1.py: 스트리밍 응답 구현

### app_2_2.py: 캐싱으로 성능 개선

---

## 💡 핵심 개념

### 스트리밍 응답

응답을 한 번에 출력하지 않고 단어별로 출력하여 체감 속도 향상:

```python
def stream_text(text):
    """텍스트를 스트리밍처럼 출력"""
    import time
    words = text.split()
    for word in words:
        yield word + ' '
        time.sleep(0.02)

# 사용
st.write_stream(stream_text(response))
```

### 캐싱

같은 입력에 대해 재계산 없이 캐시된 결과 반환:

```python
@st.cache_resource  # 세션 객체 캐싱
def get_snowflake_session():
    ...

@st.cache_data  # 데이터 캐싱
def get_ai_response(question, _session):
    ...
```

---

## 📖 실습 가이드

### 진행 방법

```bash
cd problems/Day1
streamlit run app_2_1.py
```

---

## 🎓 상세 실습 내용

### 실습 1: 스트리밍 응답 구현

**파일**: `app_2_1.py`

**목표**: 응답을 단어별로 스트리밍 출력

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

def stream_text(text):
    """텍스트를 스트리밍처럼 출력"""
    import time
    words = text.split()
    for word in words:
        yield word + ' '
        time.sleep(0.02)

session = get_snowflake_session()

st.title("✨ 스트리밍 챗봇")

user_question = st.text_input("질문을 입력하세요")

if user_question:
    st.write("### AI 답변")
    response_stream = stream_text(complete_llm(session, "llama3.1-70b", user_question))
    st.write_stream(response_stream)
```

**체크포인트**:
- [ ] stream_text() 제너레이터 함수 구현 완료
- [ ] st.write_stream() 사용 완료

---

### 실습 2: 캐싱으로 성능 개선

**파일**: `app_2_2.py`

**목표**: 같은 질문에 대해 캐시된 응답 반환

**핵심 코드**:
```python
import streamlit as st
from snowflake.snowpark import Session
import time

@st.cache_resource
def get_snowflake_session():
    connection_parameters = st.secrets["connections"]["snowflake"]
    return Session.builder.configs(connection_parameters).create()

def complete_llm(session, model, prompt):
    escaped_prompt = prompt.replace("'", "''")
    sql = f"SELECT SNOWFLAKE.CORTEX.COMPLETE('{model}', '{escaped_prompt}')"
    result = session.sql(sql).collect()
    return result[0][0]

@st.cache_data
def get_ai_response(question, _session):
    response = complete_llm(_session, "llama3.1-70b", question)
    return response

session = get_snowflake_session()

st.title("⚡ 캐싱 성능 테스트")
st.write("같은 질문을 여러 번 해보세요!")

user_question = st.text_input("질문을 입력하세요")

if user_question:
    start_time = time.time()
    response = get_ai_response(user_question, session)
    elapsed = time.time() - start_time

    st.write("### AI 답변")
    st.write(response)

    st.info(f"⏱️ 응답 시간: {elapsed:.2f}초")

    if elapsed < 0.1:
        st.success("✅ 캐시에서 가져왔습니다!")
    else:
        st.warning("⏳ 첫 응답입니다. (캐시에 저장됨)")
```

**체크포인트**:
- [ ] @st.cache_resource 데코레이터 적용 완료
- [ ] @st.cache_data 데코레이터 적용 완료
- [ ] 응답 시간 측정 완료

---

## ✅ 완료 체크리스트

- [ ] app_2_1.py - 스트리밍 응답 구현 완료
- [ ] app_2_2.py - 캐싱으로 성능 개선 완료

---

## 🔗 관련 문서

- [Streamlit Caching](https://docs.streamlit.io/library/advanced-features/caching)
- [Snowflake Cortex AI](https://docs.snowflake.com/en/user-guide/snowflake-cortex)

---

**다음 단계**: [Day 1 - Step 3: 인터랙티브 위젯] →
