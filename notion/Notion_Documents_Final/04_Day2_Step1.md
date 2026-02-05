# Day 2 - Step 1: 문서 처리

---

## 🎯 학습 목표

PDF/TXT 파일을 업로드하고 검색 가능한 청크로 분할

---

## 📚 실습 목록 (2개)

### app_1_1.py: 문서 업로드 (PDF/TXT)

### app_1_2.py: 텍스트 청킹

---

## 💡 핵심 개념

### 파일 업로드

```python
uploaded_file = st.file_uploader("파일 선택", type=["pdf", "txt"])
```

### PDF 텍스트 추출

```python
from PyPDF2 import PdfReader

reader = PdfReader(uploaded_file)
text = ""
for page in reader.pages:
    text += page.extract_text()
```

### 텍스트 청킹

긴 문서를 작은 조각으로 분할 (오버랩 포함):

```python
def chunk_text(text, chunk_size=500, overlap=50):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks
```

### Pickle 데이터 공유

Day2 실습은 연계 실습이므로 pickle로 데이터 공유:

```python
import pickle
with open("document_text.pkl", "wb") as f:
    pickle.dump(text, f)
```

---

## 📖 실습 가이드

### 실습 순서

1. **문서 업로드** (app_1_1.py) → `document_text.pkl` 생성
2. **텍스트 청킹** (app_1_2.py) → `chunks.pkl` 생성

### 진행 방법

```bash
cd problems/Day2
streamlit run app_1_1.py
```

---

## 🎓 상세 실습 내용

### 실습 1: 문서 업로드 (PDF/TXT)

**파일**: `app_1_1.py`

**목표**: PDF/TXT 파일을 업로드하고 텍스트 추출

**핵심 코드**:
```python
import streamlit as st
import pickle
import os
from PyPDF2 import PdfReader
from snowflake.snowpark import Session

DATA_DIR = os.path.dirname(os.path.abspath(__file__))

def get_snowflake_session():
    connection_parameters = st.secrets["connections"]["snowflake"]
    return Session.builder.configs(connection_parameters).create()

session = get_snowflake_session()

st.title("📁 문서 업로드")

uploaded_file = st.file_uploader("파일 선택", type=["pdf", "txt"])

if uploaded_file:
    if uploaded_file.type == "application/pdf":
        reader = PdfReader(uploaded_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
    else:
        # 여러 인코딩 시도 (UTF-8, CP949, EUC-KR)
        raw = uploaded_file.read()
        for encoding in ['utf-8', 'cp949', 'euc-kr', 'latin-1']:
            try:
                text = raw.decode(encoding)
                break
            except UnicodeDecodeError:
                continue

    st.session_state['document_text'] = text

    # 파일로 저장 (다른 앱과 공유)
    with open(os.path.join(DATA_DIR, "document_text.pkl"), "wb") as f:
        pickle.dump(text, f)

    st.success("✅ 문서 업로드 완료!")
    st.write(f"총 {len(text)} 글자")
```

**체크포인트**:
- [ ] PDF 텍스트 추출 완료
- [ ] TXT 파일 인코딩 처리 완료
- [ ] pickle 파일 저장 완료

---

### 실습 2: 텍스트 청킹

**파일**: `app_1_2.py`

**목표**: 텍스트를 지정된 크기의 청크로 분할

**핵심 코드**:
```python
import streamlit as st
import pickle
import os
from PyPDF2 import PdfReader

DATA_DIR = os.path.dirname(os.path.abspath(__file__))

st.title("✂️ 텍스트 청킹")

def chunk_text(text, chunk_size=500, overlap=50):
    """텍스트를 청크로 분할"""
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks

# 저장된 문서 로드
doc_path = os.path.join(DATA_DIR, "document_text.pkl")
if os.path.exists(doc_path):
    with open(doc_path, "rb") as f:
        st.session_state['document_text'] = pickle.load(f)
    st.success(f"✅ 저장된 문서 로드 완료!")

# 파일 업로드 (새 문서)
uploaded_file = st.file_uploader("파일 선택 (새 문서 업로드)", type=["pdf", "txt"])

if uploaded_file:
    if uploaded_file.type == "application/pdf":
        reader = PdfReader(uploaded_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
    else:
        raw = uploaded_file.read()
        for encoding in ['utf-8', 'cp949', 'euc-kr', 'latin-1']:
            try:
                text = raw.decode(encoding)
                break
            except UnicodeDecodeError:
                continue
    st.session_state['document_text'] = text
    with open(doc_path, "wb") as f:
        pickle.dump(text, f)

if 'document_text' not in st.session_state:
    st.info("📁 파일을 업로드하거나 app_1_1.py를 먼저 실행하세요.")
    st.stop()

text = st.session_state['document_text']
st.write(f"문서 길이: {len(text)} 글자")

chunk_size = st.slider("청크 크기", 100, 1000, 500)
overlap = st.slider("오버랩 크기", 0, 200, 50)

if st.button("청킹 실행"):
    chunks = chunk_text(text, chunk_size, overlap)
    st.session_state['chunks'] = chunks

    # 파일로 저장
    with open(os.path.join(DATA_DIR, "chunks.pkl"), "wb") as f:
        pickle.dump(chunks, f)

    st.write(f"✅ 총 {len(chunks)}개 청크 생성")

    for i, chunk in enumerate(chunks[:3]):
        st.write(f"**청크 {i+1}:** {chunk[:100]}...")
```

**체크포인트**:
- [ ] chunk_text() 함수 구현 완료
- [ ] 슬라이더로 청크 크기 조절 완료
- [ ] chunks.pkl 파일 저장 완료

---

## ✅ 완료 체크리스트

- [ ] app_1_1.py - 문서 업로드 완료
- [ ] app_1_2.py - 텍스트 청킹 완료

---

## 🔗 관련 문서

- [PyPDF2 Documentation](https://pypdf2.readthedocs.io/)
- [Streamlit File Uploader](https://docs.streamlit.io/library/api-reference/widgets/st.file_uploader)

---

**다음 단계**: [Day 2 - Step 2: 벡터 검색] →
