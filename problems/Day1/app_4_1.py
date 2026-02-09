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

# TODO: messages 초기화
# 힌트: st.session_state에 "messages" 키가 없으면 빈 리스트로 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []  # TODO를 완성하세요

st.write(f"### 저장된 메시지: {len(st.session_state.messages)}개")

new_message = st.text_input("새 메시지를 입력하세요")

# TODO: "추가" 버튼 만들기
# 힌트: st.button()으로 버튼 생성 → messages에 append → st.rerun()


# TODO: 모든 메시지 표시
# 힌트: for 루프로 st.session_state.messages를 순회하며 st.write()


# TODO: "모두 삭제" 버튼
# 힌트: messages를 빈 리스트로 초기화하고 st.rerun()

