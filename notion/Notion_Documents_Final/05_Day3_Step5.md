# Day 3 - Step 5: 배포 준비

---

## 🎯 학습 목표

Streamlit Cloud에 AI 앱을 배포하기 위한 준비 및 체크리스트 확인

---

## 📚 실습 목록 (1개)

### app_5_1.py: 배포 준비 체크리스트

---

## 💡 핵심 개념

### Streamlit Cloud 배포 장점

- **무료 호스팅**: 공개 저장소 무료 배포
- **자동 배포**: GitHub 푸시 시 자동 업데이트
- **Secrets 관리**: 환경 변수 안전하게 관리

### 필수 파일 구조

```
your-app/
├── app.py              # 메인 애플리케이션
├── requirements.txt    # 패키지 의존성
├── .gitignore          # Git 제외 파일
└── .streamlit/
    └── secrets.toml    # 로컬 전용 (Git에 올리지 않음!)
```

---

## 📖 배포 가이드

### 1. requirements.txt 준비

```
streamlit>=1.31.0
snowflake-snowpark-python>=1.11.1
snowflake-ml-python>=1.0.0
PyPDF2>=3.0.0
numpy>=1.24.0
pandas>=2.0.0
```

### 2. .gitignore 설정

```
.streamlit/secrets.toml
__pycache__/
*.pyc
.env
venv/
*.pkl
```

### 3. GitHub에 코드 푸시

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/your-username/your-repo.git
git push -u origin main
```

### 4. Streamlit Cloud 배포

1. [streamlit.io/cloud](https://streamlit.io/cloud) 접속
2. GitHub 계정으로 로그인
3. "New app" 클릭
4. 레포지토리 선택
5. **Advanced settings** → Secrets 설정
6. Deploy 클릭

### 5. Secrets 설정 (Streamlit Cloud)

```toml
[connections.snowflake]
account = "your-account"
user = "your-user"
password = "your-password"
warehouse = "your-warehouse"
database = "your-database"
schema = "your-schema"
```

⚠️ **secrets.toml은 절대 GitHub에 올리지 마세요!**

---

## 🎓 상세 실습 내용

### 실습: 배포 준비 체크리스트

**파일**: `app_5_1.py`

**핵심 코드**:
```python
import streamlit as st
from snowflake.snowpark import Session

def get_snowflake_session():
    connection_parameters = st.secrets["connections"]["snowflake"]
    return Session.builder.configs(connection_parameters).create()

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
    result = session.sql("SELECT CURRENT_USER(), CURRENT_WAREHOUSE()").collect()
    st.write(f"- 사용자: `{result[0][0]}`")
    st.write(f"- 웨어하우스: `{result[0][1]}`")
else:
    st.error("❌ 연결 실패")
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
    "**streamlit.io/cloud 접속** - GitHub 계정으로 로그인",
    "**'New app' 클릭** - 새 앱 배포 시작",
    "**레포지토리 선택** - Branch와 메인 파일 경로 지정",
    "**Advanced settings** - Secrets 설정",
    "**Deploy 클릭** - 배포 시작"
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
*.pkl
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
```

**실행**:
```bash
streamlit run app_5_1.py
```

**확인 사항**:
- Snowflake 연결 상태
- 현재 사용자 및 웨어하우스
- 필수 파일 체크리스트

**체크포인트**:
- [ ] Snowflake 연결 테스트 완료
- [ ] requirements.txt 준비 완료
- [ ] .gitignore 설정 완료

---

## ✅ 완료 체크리스트

- [ ] app_5_1.py - 배포 준비 체크리스트 확인
- [ ] GitHub 저장소 생성
- [ ] Streamlit Cloud 배포 (선택)

---

## 🎉 3DaysOfAI 완료!

### 학습 내용 요약

| Day | 주제 | 실습 수 |
|-----|------|--------|
| Day 1 | Streamlit & LLM 기초 | 11개 |
| Day 2 | RAG 파이프라인 | 8개 |
| Day 3 | Agent & 배포 | 5개 |
| **총합** | | **24개** |

### 다음 단계

- 자신만의 AI 앱 만들어보기
- 실제 데이터로 RAG 시스템 구축
- Snowflake Cortex 고급 기능 탐색
  - [Cortex Search](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-search)
  - [Cortex Analyst](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-analyst)
  - [Cortex Agents](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-agents)

---

**축하합니다! 🏆 3DaysOfAI 과정을 완료했습니다!**
