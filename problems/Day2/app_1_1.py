"""
Day 2 - Step 1: 문서 업로드

학습 목표:
- st.file_uploader로 PDF, TXT 업로드
- 파일 내용 읽기
- 세션 상태 저장

실행:
streamlit run app_1_1.py
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

# TODO: 파일 업로더 추가
# 힌트: uploaded_file = st.file_uploader("파일 선택", type=["pdf", "txt"])
uploaded_file = None  # TODO를 완성하세요

if uploaded_file:
    # TODO: 파일 타입에 따라 텍스트 추출
    # PDF: PdfReader 사용
    # TXT: read().decode("utf-8") 사용




    # TODO: 세션 상태에 저장
    # 힌트: st.session_state['document_text'] = text
    text = ""  # TODO를 완성하세요 (위 힌트 참고)

    # 파일로 저장 (다른 앱과 공유)
    with open(os.path.join(DATA_DIR, "document_text.pkl"), "wb") as f:
        pickle.dump(text, f)

    st.success("✅ 문서 업로드 완료!")
    st.write(f"총 {len(text)} 글자")
