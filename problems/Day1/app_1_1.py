"""
Step 1-1: Snowflake 연결 설정

학습 목표:
- Snowflake 계정 연결하기
- secrets.toml 파일 설정
- Session 객체 생성

실행:
streamlit run app_1_1.py
"""

import streamlit as st
from snowflake.snowpark import Session

# TODO: Snowflake 세션을 생성하는 함수를 작성하세요
def get_snowflake_session():
    """
    secrets.toml에서 연결 정보를 읽어와 Snowflake 세션을 생성합니다.
    """
    # TODO: st.secrets에서 연결 정보 가져오기
    # 힌트: connection_parameters = st.secrets["connections"]["snowflake"]
    
    
    # TODO: Session 객체 생성 및 반환
    # 힌트: return Session.builder.configs(connection_parameters).create()

def complete_llm(session, model, prompt):
    """SQL 방식으로 Cortex LLM 호출"""
    escaped_prompt = prompt.replace("'", "''")
    sql = f"SELECT SNOWFLAKE.CORTEX.COMPLETE('{model}', '{escaped_prompt}')"
    result = session.sql(sql).collect()
    return result[0][0]

    


st.title("🎈 Snowflake 연결 테스트")

# TODO: 세션 생성
# 힌트: session = get_snowflake_session()


# TODO: 연결 성공 메시지 출력
# 힌트: st.success("✅ Snowflake 연결 성공!")


# TODO: 현재 사용자 확인
# 힌트: current_user = session.sql("SELECT CURRENT_USER()").collect()
#       st.write("현재 사용자:", current_user[0][0])

