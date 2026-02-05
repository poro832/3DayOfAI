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

## 🎓 실습 진행

### 실습: 배포 준비 체크리스트

**파일**: `app_5_1.py`

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
