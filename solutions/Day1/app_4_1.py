"""
Step 4-1: 세션 상태 기초 (정답)
"""

import streamlit as st

st.title("💾 세션 상태 기초")

if "messages" not in st.session_state:
    st.session_state.messages = []

st.write(f"### 저장된 메시지: {len(st.session_state.messages)}개")

new_message = st.text_input("새 메시지를 입력하세요")

if st.button("추가") and new_message:
    st.session_state.messages.append(new_message)
    st.rerun()

for i, msg in enumerate(st.session_state.messages):
    st.write(f"{i+1}. {msg}")

if st.button("모두 삭제"):
    st.session_state.messages = []
    st.rerun()
