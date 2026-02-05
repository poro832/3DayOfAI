import streamlit as st
from snowflake.snowpark import Session

# 1. Snowflake 세션 연결 함수
def get_snowflake_session():
    connection_parameters = st.secrets["connections"]["snowflake"]
    return Session.builder.configs(connection_parameters).create()

st.title("🤖 나의 첫 AI 대화")

# 2. 세션 연결 시도
try:
    session = get_snowflake_session()
    # 연결 성공! (메시지는 생략)
except Exception as e:
    st.error(f"Snowflake 연결 실패: {e}")
    st.stop()

# 3. 사용자 질문 입력
user_question =                                                                                                                 .text_input("질문을 입력하세요")

if user_question:
    st.info("⏳ AI가 생각 중입니다...")
    
    try:     
        # 질문 안에 있는 따옴표(')가 SQL을 망가뜨리지 않도록 처리
        safe_question = user_question.replace("'", "\\'")
        
        # SQL 쿼리 만들기
        sql_query = f"SELECT SNOWFLAKE.CORTEX.COMPLETE('claude-3-5-sonnet', '{safe_question}')"
        
        # SQL 실행 및 결과 가져오기
        result = session.sql(sql_query).collect()
        
        # 결과에서 텍스트만 쏙 뽑아내기
        ai_response = result[0][0]
        
        st.write("### 💬 AI 답변")
        st.write(ai_response)

    except Exception as e:
        st.error(f"오류 발생: {e}")