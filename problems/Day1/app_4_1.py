"""
Step 4-1: 세션 상태 기초

학습 목표:
- st.session_state 이해하기
- 메시지 리스트 관리하기

실행:
streamlit run app_4_1.py
"""

import streamlit as st

st.title("💾 세션 상태 기초")

# messages 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []

st.write(f"### 저장된 메시지: {len(st.session_state.messages)}개")

new_message = st.text_input("새 메시지를 입력하세요")

# TODO: "추가" 버튼 만들기 (2줄)
# 힌트: st.button("추가") and new_message → messages.append() + st.rerun()


# 모든 메시지 표시
for i, msg in enumerate(st.session_state.messages):
    st.write(f"{i+1}. {msg}")

# 모두 삭제 버튼
if st.button("모두 삭제"):
    st.session_state.messages = []
    st.rerun()

