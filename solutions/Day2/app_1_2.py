"""
Day 2 - Step 1-2: 텍스트 청킹 (정답)
"""

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

# 저장된 문서 로드 시도
doc_path = os.path.join(DATA_DIR, "document_text.pkl")
if os.path.exists(doc_path):
    with open(doc_path, "rb") as f:
        st.session_state['document_text'] = pickle.load(f)
    st.success(f"✅ 저장된 문서 로드 완료! ({len(st.session_state['document_text'])} 글자)")

# 파일 업로드
uploaded_file = st.file_uploader("파일 선택 (새 문서 업로드)", type=["pdf", "txt"])

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

    # 파일로 저장
    with open(doc_path, "wb") as f:
        pickle.dump(text, f)
    st.success(f"✅ 문서 로드 완료! ({len(text)} 글자)")

if 'document_text' in st.session_state:
    text = st.session_state['document_text']
else:
    st.info("📁 파일을 업로드하거나 app_1_1.py를 먼저 실행하세요.")
    st.stop()

chunk_size = st.slider("청크 크기", 100, 1000, 500)
overlap = st.slider("오버랩 크기", 0, 200, 50)

if st.button("청킹 실행"):
    chunks = chunk_text(text, chunk_size, overlap)
    st.session_state['chunks'] = chunks

    # 파일로 저장 (다른 앱과 공유)
    with open(os.path.join(DATA_DIR, "chunks.pkl"), "wb") as f:
        pickle.dump(chunks, f)

    st.write(f"✅ 총 {len(chunks)}개 청크 생성")

    for i, chunk in enumerate(chunks[:3]):
        st.write(f"**청크 {i+1}:** {chunk[:100]}...")
