"""
Day 3 - Step 5: 배포 준비

학습 목표:
- Streamlit Cloud 배포 준비
- requirements.txt 확인
- secrets 설정

실행:
streamlit run app_5_1.py
"""

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


# 세션 연결 테스트
try:
    session = get_snowflake_session()
    connection_ok = True
except Exception as e:
    connection_ok = False
    error_msg = str(e)

st.title("🚀 배포 준비 체크리스트")

st.write("## 1️⃣ 연결 상태 확인")
if connection_ok:
    st.success("✅ Snowflake 연결 성공!")
else:
    st.error(f"❌ 연결 실패: {error_msg}")

st.write("## 2️⃣ 필수 파일 체크")

# TODO: 필수 파일 목록 작성
# 힌트:
# files = {
#     "requirements.txt": "패키지 목록",
#     ".streamlit/secrets.toml": "비밀 설정 (로컬용)",
#     "app.py 또는 메인 파일": "앱 진입점"
# }
# for file, desc in files.items():
#     st.write(f"- 📄 `{file}` - {desc}")

st.info("💡 TODO를 완성하세요")

st.write("## 3️⃣ requirements.txt 예시")
st.code("""
streamlit>=1.31.0
snowflake-snowpark-python>=1.11.1
snowflake-ml-python>=1.0.0
PyPDF2>=3.0.0
numpy>=1.24.0
pandas>=2.0.0
""", language="text")

st.write("## 4️⃣ Streamlit Cloud 배포 단계")
# TODO: 배포 단계 작성
# 힌트:
# 1. GitHub에 코드 푸시
# 2. streamlit.io/cloud 접속
# 3. New app 클릭
# 4. 레포지토리 선택
# 5. secrets 설정 (Advanced settings)
# 6. Deploy 클릭

st.write("## 5️⃣ Secrets 설정 (Streamlit Cloud)")
st.code("""
# .streamlit/secrets.toml 형식
[connections.snowflake]
account = "your-account"
user = "your-user"
password = "your-password"
warehouse = "your-warehouse"
database = "your-database"
schema = "your-schema"
""", language="toml")

st.write("---")
st.write("### 🎉 축하합니다!")
st.write("3일간의 AI 앱 개발 과정을 완료했습니다!")
