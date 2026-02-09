"""
Day 2 - Step 1: 문서 업로드 (정답)
"""

import streamlit as st
import pickle
import os
from PyPDF2 import PdfReader

DATA_DIR = os.path.dirname(os.path.abspath(__file__))

def get_snowflake_session():
    """Snowflake 세션 생성 (Day1에서 배운 내용)"""
    from snowflake.snowpark import Session
    connection_parameters = st.secrets["connections"]["snowflake"]
    return Session.builder.configs(connection_parameters).create()

def complete_llm(session, model, prompt):
    """SQL 방식으로 Cortex LLM 호출"""
    escaped_prompt = prompt.replace("'", "''")
    sql = f"SELECT SNOWFLAKE.CORTEX.COMPLETE('{model}', '{escaped_prompt}')"
    result = session.sql(sql).collect()
    return result[0][0]


session = get_snowflake_session()

st.title("📁 문서 업로드")

# 파일 업로더
uploaded_file = st.file_uploader("파일 선택", type=["pdf", "txt"])

if uploaded_file:
    text = ""

    if uploaded_file.type == "application/pdf":
        reader = PdfReader(uploaded_file)
        for page in reader.pages:
            text += page.extract_text()
    else:
        # TXT: 인코딩 자동 감지
        raw = uploaded_file.read()
        for encoding in ['utf-8', 'cp949', 'euc-kr', 'latin-1']:
            try:
                text = raw.decode(encoding)
                break
            except UnicodeDecodeError:
                continue

    # 세션 상태에 저장
    st.session_state['document_text'] = text

    # 파일로 저장 (다른 앱과 공유)
    with open(os.path.join(DATA_DIR, "document_text.pkl"), "wb") as f:
        pickle.dump(text, f)

    st.success("✅ 문서 업로드 완료!")
    st.write(f"총 {len(text)} 글자")

    if text:
        with st.expander("📄 미리보기"):
            st.write(text[:500] + "..." if len(text) > 500 else text)
