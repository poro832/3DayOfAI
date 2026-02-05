# Day 1 - Step 1: Snowflake 연결 및 LLM 호출

---

## 🎯 학습 목표

Snowflake Cortex AI에 연결하고 첫 AI 응답 받기

---

## 📚 실습 목록 (2개)

### app_1_1.py: Snowflake 연결 설정

### app_1_2.py: 첫 LLM 호출

---

## 💡 핵심 개념

### Snowflake Session

Snowflake와 통신하기 위한 연결 객체입니다.

```python
from snowflake.snowpark import Session

def get_snowflake_session():
    connection_parameters = st.secrets["connections"]["snowflake"]
    return Session.builder.configs(connection_parameters).create()
```

### secrets.toml

`.streamlit/secrets.toml` 파일에 연결 정보를 저장합니다:

```toml
[connections.snowflake]
account = "your-account"
user = "your-user"
password = "your-password"
warehouse = "your-warehouse"
database = "your-database"
schema = "your-schema"
```

### complete_llm() 함수

SQL 방식으로 Cortex AI를 호출하는 헬퍼 함수:

```python
def complete_llm(session, model, prompt):
    """SQL 방식으로 Cortex LLM 호출"""
    escaped_prompt = prompt.replace("'", "''")
    sql = f"SELECT SNOWFLAKE.CORTEX.COMPLETE('{model}', '{escaped_prompt}')"
    result = session.sql(sql).collect()
    return result[0][0]
```

---

## 📖 실습 가이드

### 진행 방법

```bash
cd problems/Day1
streamlit run app_1_1.py
```

---

## 🎓 상세 실습 내용

### 실습 1: Snowflake 연결 설정

**파일**: `app_1_1.py`

**목표**: Snowflake에 연결하고 현재 사용자 정보 확인

**핵심 코드**:
```python
import streamlit as st
from snowflake.snowpark import Session

def get_snowflake_session():
    connection_parameters = st.secrets["connections"]["snowflake"]
    return Session.builder.configs(connection_parameters).create()

st.title("🎈 Snowflake 연결 테스트")

# 세션 생성
session = get_snowflake_session()

# 연결 성공 메시지
st.success("✅ Snowflake 연결 성공!")

# 현재 사용자 확인
current_user = session.sql("SELECT CURRENT_USER()").collect()
st.write("현재 사용자:", current_user[0][0])
```

**체크포인트**:
- [ ] secrets.toml 파일 설정 완료
- [ ] Snowflake 연결 성공
- [ ] 현재 사용자 확인

---

### 실습 2: 첫 LLM 호출

**파일**: `app_1_2.py`

**목표**: 사용자 입력을 받아 AI 응답 출력

**핵심 코드**:
```python
import streamlit as st
from snowflake.snowpark import Session

def get_snowflake_session():
    connection_parameters = st.secrets["connections"]["snowflake"]
    return Session.builder.configs(connection_parameters).create()

def complete_llm(session, model, prompt):
    """SQL 방식으로 Cortex LLM 호출"""
    escaped_prompt = prompt.replace("'", "''")
    sql = f"SELECT SNOWFLAKE.CORTEX.COMPLETE('{model}', '{escaped_prompt}')"
    result = session.sql(sql).collect()
    return result[0][0]

session = get_snowflake_session()

st.title("🤖 나의 첫 AI 대화")

# 사용자 입력
user_question = st.text_input("질문을 입력하세요")

# AI 응답
if user_question:
    with st.spinner("생각하는 중..."):
        response = complete_llm(session, "llama3.1-70b", user_question)

    st.write("### AI 답변")
    st.write(response)
```

**체크포인트**:
- [ ] complete_llm() 함수 구현 완료
- [ ] 사용자 입력 받기 완료
- [ ] AI 응답 출력 완료

---

## ✅ 완료 체크리스트

- [ ] app_1_1.py - Snowflake 연결 설정 완료
- [ ] app_1_2.py - 첫 LLM 호출 완료

---

## 🔗 관련 문서

- [Streamlit 공식 문서](https://docs.streamlit.io)
- [Snowflake Cortex AI](https://docs.snowflake.com/en/user-guide/snowflake-cortex)

---

**다음 단계**: [Day 1 - Step 2: 스트리밍 & 캐싱] →
