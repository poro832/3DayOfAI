"""
Day 3 - Step 5: 배포 준비 (정답)
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

    # 간단한 테스트 쿼리
    result = session.sql("SELECT CURRENT_USER(), CURRENT_WAREHOUSE()").collect()
    st.write(f"- 사용자: `{result[0][0]}`")
    st.write(f"- 웨어하우스: `{result[0][1]}`")
else:
    st.error(f"❌ 연결 실패")
    st.write("secrets.toml 설정을 확인하세요.")

st.write("## 2️⃣ 필수 파일 체크")
files = {
    "requirements.txt": "패키지 의존성 목록",
    ".streamlit/secrets.toml": "비밀 설정 (로컬 전용, Git에 포함 금지)",
    "app.py": "앱 진입점 (또는 메인 파일)"
}
for file, desc in files.items():
    st.write(f"- 📄 `{file}` - {desc}")

st.write("## 3️⃣ requirements.txt")
requirements = """streamlit>=1.31.0
snowflake-snowpark-python>=1.11.1
snowflake-ml-python>=1.0.0
PyPDF2>=3.0.0
numpy>=1.24.0
pandas>=2.0.0"""

st.code(requirements, language="text")

if st.button("requirements.txt 다운로드"):
    st.download_button(
        label="📥 다운로드",
        data=requirements,
        file_name="requirements.txt",
        mime="text/plain"
    )

st.write("## 4️⃣ Streamlit Cloud 배포 단계")
steps = [
    "**GitHub에 코드 푸시** - 레포지토리 생성 후 코드 업로드",
    "**[streamlit.io/cloud](https://streamlit.io/cloud) 접속** - GitHub 계정으로 로그인",
    "**'New app' 클릭** - 새 앱 배포 시작",
    "**레포지토리 선택** - Branch와 메인 파일 경로 지정",
    "**Advanced settings** - Secrets 설정 (아래 형식 참고)",
    "**Deploy 클릭** - 배포 시작 (수 분 소요)"
]
for i, step in enumerate(steps, 1):
    st.write(f"{i}. {step}")

st.write("## 5️⃣ Secrets 설정 (Streamlit Cloud)")
secrets_template = """[connections.snowflake]
account = "your-account"
user = "your-user"
password = "your-password"
warehouse = "your-warehouse"
database = "your-database"
schema = "your-schema"
"""
st.code(secrets_template, language="toml")
st.warning("⚠️ secrets.toml은 절대 GitHub에 올리지 마세요!")

st.write("## 6️⃣ .gitignore 예시")
gitignore = """.streamlit/secrets.toml
__pycache__/
*.pyc
.env
venv/
"""
st.code(gitignore, language="text")

st.write("---")

st.write("## 🎉 3DaysOfAI 완료!")
st.balloons()

col1, col2, col3 = st.columns(3)
with col1:
    st.write("### Day 1")
    st.write("Streamlit & LLM 기초")
    st.write("✅ 11개 실습 완료")
with col2:
    st.write("### Day 2")
    st.write("RAG 파이프라인")
    st.write("✅ 8개 실습 완료")
with col3:
    st.write("### Day 3")
    st.write("Agent & 배포")
    st.write("✅ 5개 실습 완료")

st.success("🏆 총 24개 실습을 완료했습니다! 축하합니다!")
