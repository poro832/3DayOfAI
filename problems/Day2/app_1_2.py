"""
Day 2 - Step 1-2: 텍스트 청킹

학습 목표:
- 긴 텍스트를 작은 청크로 분할
- 오버랩 구현
- 청크 저장

실행:
streamlit run app_1_2.py
"""

import streamlit as st
import pickle
import os
from PyPDF2 import PdfReader

DATA_DIR = os.path.dirname(os.path.abspath(__file__))

st.title("✂️ 텍스트 청킹")

# 청킹과 오버랩 설명
with st.expander("💡 청크(Chunk)와 오버랩(Overlap)이란?", expanded=True):
    st.markdown("""
    **청크(Chunk)**: 긴 문서를 작은 조각으로 나눈 것
    - AI가 한 번에 처리할 수 있는 텍스트 양에는 한계가 있습니다
    - 예: 1000자 문서 → 500자씩 2개의 청크로 분할

    **오버랩(Overlap)**: 청크 사이에 겹치는 부분
    - 문장이 청크 경계에서 잘리면 의미가 손실될 수 있습니다
    - 오버랩을 주면 앞 청크의 끝부분이 다음 청크의 시작에 포함됩니다
    - 예: 500자 청크 + 50자 오버랩 → 450자마다 새 청크 시작

    ```
    [----청크1----]
              [----청크2----]  ← 50자 겹침(오버랩)
                        [----청크3----]
    ```
    """)

# TODO: 청킹 함수 작성
def chunk_text(text, chunk_size=500, overlap=50):
    """
    텍스트를 청크로 분할

    Args:
        text: 원본 텍스트
        chunk_size: 청크 크기
        overlap: 중복 크기
    """
    # TODO: 청크를 만들어 리스트에 추가하세요
    # 힌트: text[start:end]로 슬라이싱, start는 chunk_size - overlap만큼 이동
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        pass  # TODO: chunks에 텍스트 조각 추가 + start 이동 (2줄)
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
