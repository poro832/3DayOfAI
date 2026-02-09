"""
Step 5-2: 시스템 프롬프트 추가

학습 목표:
- 시스템 프롬프트로 AI 역할 정의하기
- 사이드바로 대화 관리하기

실행:
streamlit run app_5_2.py
"""

import streamlit as st
from snowflake.snowpark import Session

@st.cache_resource
def get_snowflake_session():
    connection_parameters = st.secrets["connections"]["snowflake"]
    return Session.builder.configs(connection_parameters).create()

def complete_llm(session, model, prompt):
    """SQL 방식으로 Cortex LLM 호출"""
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

st.title("🎯 완성형 챗봇")

# TODO: 시스템 프롬프트 정의 (AI의 역할과 성격을 지정)
# 힌트: AI의 역할, 답변 언어, 스타일 등을 문자열로 정의하세요
DEFAULT_SYSTEM_PROMPT = "당신은 AI 어시스턴트입니다."  # TODO를 완성하세요

if "messages" not in st.session_state:
    st.session_state.messages = []

if "system_prompt" not in st.session_state:
    st.session_state.system_prompt = DEFAULT_SYSTEM_PROMPT

with st.sidebar:
    st.write("### ⚙️ 설정")

    # TODO: 시스템 프롬프트 편집 영역
    # 힌트: st.text_area()로 현재 프롬프트를 표시하고, 변경 시 session_state 업데이트
    # new_prompt = st.text_area("시스템 프롬프트", value=???, height=100)


    st.divider()

    st.write("### 💬 대화 관리")

    # TODO: 대화 초기화 버튼
    # 힌트: st.button()으로 버튼 생성, 클릭 시 messages를 빈 리스트로 초기화 후 st.rerun()


    msg_count = len(st.session_state.messages)
    st.write(f"메시지 수: {msg_count}개")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

user_input = st.chat_input("메시지를 입력하세요...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    # 대화 히스토리를 프롬프트로 구성
    conversation_history = "\n".join([
        f"{'사용자' if msg['role'] == 'user' else 'AI'}: {msg['content']}"
        for msg in st.session_state.messages
    ])

    # TODO: 시스템 프롬프트와 대화 히스토리를 조합한 full_prompt 생성
    # 힌트: 아래 형식으로 f-string을 완성하세요
    # full_prompt = f"""[시스템 지시사항]
    # {???}
    #
    # [대화 내용]
    # {???}
    #
    # AI:"""
    full_prompt = conversation_history  # TODO를 완성하세요

    with st.chat_message("assistant"):
        ai_response_stream = stream_text(complete_llm(session, "llama3.1-70b", full_prompt))
        ai_response = st.write_stream(ai_response_stream)

    st.session_state.messages.append({"role": "assistant", "content": ai_response})
