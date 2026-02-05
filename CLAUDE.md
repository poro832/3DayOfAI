# 3DaysOfAI - 프로젝트 가이드

## 프로젝트 개요

**원본**: [streamlit/30DaysOfAI](https://github.com/streamlit/30DaysOfAI) - 30일 AI 학습 커리큘럼
**목표**: 30일 과정을 3일(24개 실습)로 압축한 실전 중심 AI 앱 개발 과정

**핵심 원칙**:
- 이론 최소화, 실습 최대화
- 모든 코드는 Snowflake Cortex AI 기반
- 각 파일 독립 실행 가능
- problems(TODO 포함) + solutions(정답) 구조

---

## 폴더 구조

```
3DaysOfAI/
├── .streamlit/secrets.toml     # Snowflake 연결 정보
├── problems/                   # 실습 문제 (TODO 주석 포함)
│   ├── Day1/                   # 11개 파일
│   ├── Day2/                   # 8개 파일
│   └── Day3/                   # 5개 파일
├── solutions/                  # 정답 코드
│   ├── Day1/
│   ├── Day2/
│   └── Day3/
├── sample_data/                # 실습용 샘플 데이터
│   └── animals.txt             # Day2 RAG 실습용
├── notion/Notion_Documents_Final/  # 노션 문서
└── requirements.txt
```

---

## 파일 명명 규칙

```
Day{N}/app_{step}_{sub}.py

예: Day1/app_1_1.py = Day1, Step 1, 실습 1
예: Day2/app_2_2.py = Day2, Step 2, 실습 2
```

---

## 커리큘럼 (총 24개 실습)

### Day 1: Streamlit & LLM 기초 (11개)

| Step | 파일 | 내용 |
|------|------|------|
| 1 | app_1_1.py | Snowflake 연결 설정 |
| 1 | app_1_2.py | 첫 LLM 호출 |
| 2 | app_2_1.py | 스트리밍 응답 |
| 2 | app_2_2.py | 캐싱 성능 개선 |
| 3 | app_3_1.py | 온도 조절 챗봇 |
| 3 | app_3_2.py | 모델 선택 챗봇 |
| 3 | app_3_3.py | 사이드바 활용 |
| 4 | app_4_1.py | 세션 상태 기초 |
| 4 | app_4_2.py | 채팅 UI 만들기 |
| 5 | app_5_1.py | 컨텍스트 챗봇 |
| 5 | app_5_2.py | 시스템 프롬프트 |

### Day 2: RAG 파이프라인 (8개)

| Step | 파일 | 내용 |
|------|------|------|
| 1 | app_1_1.py | 문서 업로드 (PDF/TXT) |
| 1 | app_1_2.py | 텍스트 청킹 |
| 2 | app_2_1.py | 벡터 임베딩 생성 |
| 2 | app_2_2.py | 유사도 검색 |
| 3 | app_3_1.py | 기본 RAG 챗봇 |
| 3 | app_3_2.py | 스트리밍 RAG 챗봇 |
| 4 | app_4_1.py | 채팅 히스토리 |
| 4 | app_4_2.py | 출처 표시 기능 |

### Day 3: Agent & 배포 (5개)

| Step | 파일 | 내용 |
|------|------|------|
| 1 | app_1_1.py | Function Calling 기초 |
| 2 | app_2_1.py | 날씨 조회 Agent |
| 3 | app_3_1.py | 다중 도구 Agent |
| 4 | app_4_1.py | 데이터 분석 Agent |
| 5 | app_5_1.py | 배포 준비 |

---

## 기술 스택

```python
# requirements.txt
streamlit==1.52.0
snowflake-ml-python==1.20.0
snowflake-snowpark-python==1.44.0
PyPDF2>=3.0.0
numpy>=1.24.0
```

### Snowflake Cortex AI 핵심 함수

```python
# LLM 호출 (SQL 방식 - 권장)
def complete_llm(session, model, prompt):
    escaped_prompt = prompt.replace("'", "''")
    sql = f"SELECT SNOWFLAKE.CORTEX.COMPLETE('{model}', '{escaped_prompt}')"
    result = session.sql(sql).collect()
    return result[0][0]

response = complete_llm(session, "llama3.1-70b", "...")

# 사용 가능한 모델: llama3.1-70b (권장), mixtral-8x7b, mistral-7b 등

# 벡터 임베딩 (SQL)
SELECT SNOWFLAKE.CORTEX.EMBED_TEXT_768('snowflake-arctic-embed-m', 'text')
```

### Streamlit 핵심 함수

```python
# 기본 UI
st.title(), st.write(), st.text_input(), st.button()

# 위젯
st.slider(), st.selectbox(), st.sidebar

# 캐싱
@st.cache_data

# 세션 상태
st.session_state.messages = []

# 채팅 UI
st.chat_message("user"), st.chat_input(), st.write_stream()
```

---

## 작업 현황

### 완료
- [x] Day1 코드 (11개) - problems + solutions
- [x] Day2 코드 (8개) - problems + solutions
- [x] Day3 코드 (5개) - problems + solutions
- [x] Day1 노션 문서 (Overview + Step 1-5)
- [x] Day2 노션 문서 (Overview + Step 1-4)
- [x] Day3 노션 문서 (Overview + Step 1-5)
- [x] 코드 실행 테스트 (문법 검증 완료)
- [x] Day2 pickle 기반 연계 실습 구현
- [x] Day3 Agent 시뮬레이션 명시 추가
- [x] 중복 파일 정리 (11개 삭제)
- [x] README.md 완성

### 진행 필요
- [ ] GitHub 배포
- [ ] Streamlit Cloud 배포 테스트 (선택)

---

## 노션 문서 구조

```
notion/Notion_Documents_Final/
├── 00_Course_Overview.md      # 전체 과정 소개
├── 01_Day1_Overview.md        # Day1 개요
├── 02_Day1_Step1.md ~ Step5   # Day1 상세
├── 03_Day2_Overview.md        # Day2 개요
├── 04_Day2_Step1.md           # 문서 처리
├── 04_Day2_Step2.md           # 벡터 검색
├── 04_Day2_Step3.md           # RAG 챗봇
├── 04_Day2_Step4.md           # 히스토리 & 출처
├── 05_Day3_Overview.md        # Day3 개요
├── 05_Day3_Step1.md           # Function Calling
├── 05_Day3_Step2.md           # 날씨 조회 Agent
├── 05_Day3_Step3.md           # 다중 도구 Agent
├── 05_Day3_Step4.md           # 데이터 분석 Agent
├── 05_Day3_Step5.md           # 배포 준비
└── README.md
```

---

## 참고 자료

- [Streamlit Docs](https://docs.streamlit.io)
- [Snowflake Cortex AI](https://docs.snowflake.com/en/user-guide/snowflake-cortex)
- [원본 30DaysOfAI](https://github.com/streamlit/30DaysOfAI)
