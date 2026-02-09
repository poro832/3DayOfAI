"""
Day 2 - Step 5-1: LLM 모델 비교 도구

학습 목표:
- 여러 LLM 모델 성능 비교
- 응답 시간, 토큰 수 측정
- 모델별 특성 이해

실행: streamlit run problems/Day2/app_5_1.py
"""

import streamlit as st
import time
from snowflake.snowpark import Session


def get_snowflake_session():
    connection_parameters = st.secrets["connections"]["snowflake"]
    return Session.builder.configs(connection_parameters).create()


# TODO 1: 메트릭 수집 함수 완성
def complete_llm_with_metrics(session, model, prompt):
    """LLM 호출 + 메트릭 수집"""
    escaped_prompt = prompt.replace("'", "''")
    sql = f"SELECT SNOWFLAKE.CORTEX.COMPLETE('{model}', '{escaped_prompt}')"

    # 시간 측정
    start_time = time.time()
    result = session.sql(sql).collect()
    latency = time.time() - start_time
    response = result[0][0]

    return {
        "response": response,
        "latency": latency,
        "word_count": len(response.split()),
        "char_count": len(response)
    }


try:
    session = get_snowflake_session()
except Exception as e:
    st.error(f"Snowflake 연결 실패: {e}")
    st.stop()

# 세션 상태 초기화 - 비교 히스토리 저장
if "comparison_history" not in st.session_state:
    st.session_state.comparison_history = []

st.title("⚖️ LLM 모델 비교 도구")

with st.expander("💡 모델 비교가 중요한 이유", expanded=False):
    st.markdown("""
    ### 어떤 모델을 사용해야 할까?

    | 모델 | 특징 | 적합한 용도 |
    |------|------|-------------|
    | **llama3.1-70b** | 고성능, 느림 | 복잡한 추론, 코딩 |
    | **llama3.1-8b** | 빠름, 가벼움 | 간단한 Q&A, 챗봇 |
    | **mixtral-8x7b** | 균형잡힌 성능 | 범용 |
    | **mistral-large** | 고품질 | 문서 작성 |

    ### 비교 지표
    - **응답 시간 (Latency)**: 첫 응답까지 걸린 시간
    - **토큰 수**: 출력 길이 (비용과 연관)
    - **품질**: 정확성, 상세함, 형식
    """)

# 사용 가능한 모델 목록
AVAILABLE_MODELS = [
    "llama3.1-70b",
    "llama3.1-8b",
    "mixtral-8x7b",
    "mistral-7b",
    "mistral-large"
]

st.write("### ⚙️ 비교 설정")

# 모델 선택
col1, col2 = st.columns(2)
with col1:
    model_a = st.selectbox("모델 A", AVAILABLE_MODELS, index=0)
with col2:
    model_b = st.selectbox("모델 B", AVAILABLE_MODELS, index=1)

# 프롬프트 입력
prompt_options = {
    "간단한 질문": "대한민국의 수도는 어디인가요?",
    "설명 요청": "인공지능이란 무엇인지 간단히 설명해주세요.",
    "창작": "봄에 대한 짧은 시를 써주세요.",
    "코드 작성": "Python으로 피보나치 수열을 출력하는 함수를 작성해주세요.",
    "직접 입력": ""
}

prompt_type = st.selectbox("프롬프트 유형", list(prompt_options.keys()))

if prompt_type == "직접 입력":
    prompt = st.text_area("프롬프트 입력", height=100)
else:
    prompt = st.text_area("프롬프트", value=prompt_options[prompt_type], height=100)

# 비교 실행
if st.button("🔄 모델 비교 실행") and prompt:
    st.write("### 📊 비교 결과")

    results = {}

    # TODO 2: 두 모델 실행 및 결과 비교
    progress = st.progress(0)

    for i, model in enumerate([model_a, model_b]):
        with st.spinner(f"{model} 실행 중..."):
            try:
                result = complete_llm_with_metrics(session, model, prompt)
                if result:
                    results[model] = result
                else:
                    results[model] = {"error": "TODO를 완성하세요"}
            except Exception as e:
                results[model] = {"error": str(e)}

        progress.progress((i + 1) / 2)

    # 결과 표시 (나란히)
    col1, col2 = st.columns(2)

    for col, model in zip([col1, col2], [model_a, model_b]):
        with col:
            st.write(f"#### {model}")

            if "error" in results.get(model, {}):
                st.error(f"오류: {results[model]['error']}")
            elif results.get(model):
                r = results[model]

                # 메트릭
                st.metric("응답 시간", f"{r.get('latency', 0):.2f}초")
                st.metric("글자 수", f"{r.get('char_count', 0):,}")

                # 응답 내용
                st.text_area(
                    "응답",
                    value=r.get("response", ""),
                    height=200,
                    disabled=True,
                    key=f"response_{model}"
                )

    # 비교 분석
    if "error" not in results.get(model_a, {}) and "error" not in results.get(model_b, {}):
        st.divider()
        st.write("### 📈 비교 분석")

        r_a = results[model_a]
        r_b = results[model_b]

        # 속도 비교
        faster = model_a if r_a['latency'] < r_b['latency'] else model_b
        speed_diff = abs(r_a['latency'] - r_b['latency'])
        speed_ratio = max(r_a['latency'], r_b['latency']) / min(r_a['latency'], r_b['latency'])

        st.write(f"**⚡ 속도**: {faster}가 {speed_diff:.2f}초 더 빠름 ({speed_ratio:.1f}배)")

        # 길이 비교
        longer = model_a if r_a['char_count'] > r_b['char_count'] else model_b
        length_diff = abs(r_a['char_count'] - r_b['char_count'])

        st.write(f"**📝 길이**: {longer}가 {length_diff}자 더 긴 응답")

        # 히스토리에 저장
        import datetime
        st.session_state.comparison_history.append({
            "시간": datetime.datetime.now().strftime("%H:%M:%S"),
            "프롬프트": prompt[:30] + "..." if len(prompt) > 30 else prompt,
            "모델A": model_a,
            "모델B": model_b,
            "A 응답시간": f"{r_a['latency']:.2f}초",
            "B 응답시간": f"{r_b['latency']:.2f}초",
            "승자(속도)": faster
        })

# 히스토리 보기
if st.checkbox("📋 비교 히스토리 보기"):
    if st.session_state.comparison_history:
        import pandas as pd
        history_df = pd.DataFrame(st.session_state.comparison_history)
        st.dataframe(history_df, use_container_width=True)

        if st.button("🗑️ 히스토리 초기화"):
            st.session_state.comparison_history = []
            st.rerun()
    else:
        st.info("아직 비교 기록이 없습니다.")

# 사이드바
with st.sidebar:
    st.write("### 💡 모델 선택 가이드")

    st.markdown("""
    **빠른 응답이 중요하면:**
    - llama3.1-8b
    - mistral-7b

    **높은 품질이 중요하면:**
    - llama3.1-70b
    - mistral-large

    **균형이 필요하면:**
    - mixtral-8x7b
    """)
