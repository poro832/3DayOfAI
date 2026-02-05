"""
Step 1-1: Snowflake 연결 설정 (정답)

학습 목표:
- Snowflake 계정 연결하기
- secrets.toml 파일 설정
- Session 객체 생성

실행:
streamlit run app_1_1.py
"""

import streamlit as st
from snowflake.snowpark import Session

def get_snowflake_session():
    """
    secrets.toml에서 연결 정보를 읽어와 Snowflake 세션을 생성합니다.
    """
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
