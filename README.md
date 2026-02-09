# 3DaysOfAI

**30일 AI 학습 과정을 3일로 압축한 실전 중심 AI 앱 개발 과정**

> 원본: [streamlit/30DaysOfAI](https://github.com/streamlit/30DaysOfAI)

---

## 소개

3DaysOfAI는 Streamlit과 Snowflake Cortex AI를 활용하여 **챗봇부터 RAG 시스템, 지능형 Agent까지** 단계별로 구현하는 실습 중심 교육 과정입니다.

### 특징

- **32개 실습** (Day1: 12개, Day2: 10개, Day3: 10개)
- **problems + solutions 구조** - 직접 코딩하고 정답 확인
- **Snowflake Cortex AI 기반** - 클라우드 LLM 활용
- **각 파일 독립 실행 가능** - 원하는 실습만 선택 가능

---

## 사전 준비

### 1. Snowflake 계정

- [Snowflake 무료 체험](https://signup.snowflake.com/) 가입 (120일 크레딧)
- 계정 생성 후 웨어하우스, 데이터베이스, 스키마 설정

### 2. Python 환경

- Python 3.11 이상 권장

### 3. 패키지 설치

```bash
pip install -r requirements.txt
```

### 4. Snowflake 연결 설정

`.streamlit/secrets.toml` 파일 생성:

```toml
[connections.snowflake]
account = "your-account"
user = "your-user"
password = "your-password"
warehouse = "your-warehouse"
database = "your-database"
schema = "your-schema"
```

---

## 프로젝트 구조

```
3DaysOfAI/
├── .streamlit/
│   └── secrets.toml          # Snowflake 연결 정보 (Git 제외)
├── problems/                  # 실습 문제 (TODO 포함)
│   ├── Day1/                  # 12개 파일
│   ├── Day2/                  # 10개 파일
│   └── Day3/                  # 10개 파일
├── solutions/                 # 정답 코드
│   ├── Day1/
│   ├── Day2/
│   └── Day3/
├── sample_data/               # 실습용 샘플 데이터
│   └── animals.txt            # Day2 RAG 실습용
├── requirements.txt
└── README.md
```

---

## 커리큘럼

### Day 1: Streamlit & LLM 기초 (12개 실습)

| Step | 파일 | 학습 내용 |
|------|------|----------|
| 1-1 | app_1_1.py | Snowflake 연결 설정 |
| 1-2 | app_1_2.py | 첫 LLM 호출 |
| 2-1 | app_2_1.py | 스트리밍 응답 |
| 2-2 | app_2_2.py | 캐싱 성능 개선 |
| 2-3 | app_2_3.py | AI 콘텐츠 생성기 |
| 3-1 | app_3_1.py | 온도 조절 챗봇 |
| 3-2 | app_3_2.py | 모델 선택 챗봇 |
| 3-3 | app_3_3.py | 사이드바 활용 |
| 4-1 | app_4_1.py | 세션 상태 기초 |
| 4-2 | app_4_2.py | 채팅 UI 만들기 |
| 5-1 | app_5_1.py | 컨텍스트 챗봇 |
| 5-2 | app_5_2.py | 시스템 프롬프트 |

### Day 2: RAG 파이프라인 (10개 실습)

| Step | 파일 | 학습 내용 |
|------|------|----------|
| 1-1 | app_1_1.py | 문서 업로드 (PDF/TXT) |
| 1-2 | app_1_2.py | 텍스트 청킹 |
| 2-1 | app_2_1.py | 벡터 임베딩 생성 |
| 2-2 | app_2_2.py | 유사도 검색 |
| 3-1 | app_3_1.py | 기본 RAG 챗봇 |
| 3-2 | app_3_2.py | 스트리밍 RAG 챗봇 |
| 4-1 | app_4_1.py | 채팅 히스토리 |
| 4-2 | app_4_2.py | 출처 표시 기능 |
| 5-1 | app_5_1.py | 모델 비교 (심화) |
| 5-2 | app_5_2.py | 하이브리드 검색 (심화) |

**Day2 실습은 연계 실습입니다** - 순서대로 진행하세요.

### Day 3: Agent & 배포 (10개 실습)

| Step | 파일 | 학습 내용 |
|------|------|----------|
| 1-1 | app_1_1.py | Function Calling 기초 |
| 1-2 | app_1_2.py | 도구 등록 시스템 (심화) |
| 2-1 | app_2_1.py | 날씨 조회 Agent |
| 2-2 | app_2_2.py | 다중 파라미터 Agent (심화) |
| 3-1 | app_3_1.py | 다중 도구 Agent |
| 3-2 | app_3_2.py | 대화형 Agent (심화) |
| 4-1 | app_4_1.py | 데이터 분석 Agent |
| 4-2 | app_4_2.py | 시각화 Agent (심화) |
| 5-1 | app_5_1.py | 배포 준비 |
| 5-2 | app_5_2.py | AI 만능 어시스턴트 (심화) |

> **참고**: Day3 Agent 실습은 개념 학습을 위한 시뮬레이션입니다.
> 실제 Snowflake Cortex Agents API와는 다릅니다.

---

## 실습 방법

### 1. 문제 풀기 (problems)

```bash
cd problems/Day1
streamlit run app_1_1.py
```

- 코드의 `TODO` 주석을 찾아 완성
- 힌트를 참고하여 구현

### 2. 정답 확인 (solutions)

```bash
cd solutions/Day1
streamlit run app_1_1.py
```

### 3. Day2 연계 실습

Day2는 이전 실습의 결과물이 필요합니다:

```bash
# 순서대로 실행
streamlit run app_1_1.py  # 문서 업로드 → document_text.pkl 저장
streamlit run app_1_2.py  # 청킹 → chunks.pkl 저장
streamlit run app_2_1.py  # 임베딩 → embeddings.pkl 저장
streamlit run app_2_2.py  # 이후 실습들은 위 파일들을 자동 로드
```

**샘플 데이터**: `sample_data/animals.txt` 파일을 Day2 실습에 활용하세요.

---

## 기술 스택

### 패키지

```
streamlit>=1.31.0
snowflake-snowpark-python>=1.11.1
snowflake-ml-python>=1.0.0
PyPDF2>=3.0.0
numpy>=1.24.0
pandas>=2.0.0
```

### Snowflake Cortex AI 함수

```python
# LLM 호출
SNOWFLAKE.CORTEX.COMPLETE('llama3.1-70b', 'prompt')

# 벡터 임베딩
SNOWFLAKE.CORTEX.EMBED_TEXT_768('snowflake-arctic-embed-m', 'text')
```

### 사용 가능한 모델

- `llama3.1-70b` (권장)
- `llama3.1-405b`
- `mixtral-8x7b`
- `mistral-7b`

---

## 참고 자료

- [Streamlit Documentation](https://docs.streamlit.io)
- [Snowflake Cortex AI](https://docs.snowflake.com/en/user-guide/snowflake-cortex)
- [Cortex Complete](https://docs.snowflake.com/en/sql-reference/functions/complete-snowflake-cortex)
- [Cortex Embed](https://docs.snowflake.com/en/user-guide/snowflake-cortex/embed)
- [원본 30DaysOfAI](https://github.com/streamlit/30DaysOfAI)

---

## 라이선스

이 프로젝트는 교육 목적으로 제작되었습니다.

---

**총 32개 실습** (문제 + 정답 = 64개 파일)

Made with ❤️ for AI Learners
