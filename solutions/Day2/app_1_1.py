"""
Day 2 - Step 1: 문서 업로드 (정답)
"""

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
        text = uploaded_file.read().decode("utf-8")

    st.session_state['document_text'] = text

    # 파일로 저장 (다른 앱과 공유)
    with open(os.path.join(DATA_DIR, "document_text.pkl"), "wb") as f:
        pickle.dump(text, f)

    st.success("✅ 문서 업로드 완료!")
    st.write(f"총 {len(text)} 글자")
