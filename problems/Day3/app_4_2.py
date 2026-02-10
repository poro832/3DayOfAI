"""
Day 3 - Step 4-2: LangChain 스타일 Agent (실습)

[학습 목표]
- LangChain 패턴 이해
- 체이닝과 파이프라인
- 재사용 가능한 컴포넌트

[핵심 개념]
LangChain 스타일의 체이닝 패턴을 Snowflake Cortex로 구현합니다.
(실제 LangChain 라이브러리 없이 패턴만 학습)
"""

import streamlit as st
import json
from datetime import datetime
from snowflake.snowpark import Session


def get_snowflake_session():
    connection_parameters = st.secrets["connections"]["snowflake"]
    return Session.builder.configs(connection_parameters).create()


def complete_llm(session, model, prompt):
    escaped_prompt = prompt.replace("'", "''")
    sql = f"SELECT SNOWFLAKE.CORTEX.COMPLETE('{model}', '{escaped_prompt}')"
    result = session.sql(sql).collect()
    return result[0][0]


try:
    session = get_snowflake_session()
except Exception as e:
    st.error(f"Snowflake 연결 실패: {e}")
    st.stop()

st.title("🔗 LangChain 스타일 Agent")

with st.expander("💡 LangChain 패턴이란?", expanded=True):
    st.markdown("""
    ### 체이닝 (Chaining) 패턴

    ```python
    # LangChain 스타일
    chain = prompt | llm | parser

    # 파이프라인처럼 연결
    result = chain.invoke({"input": "질문"})
    ```

    ### 주요 컴포넌트

    | 컴포넌트 | 역할 |
    |----------|------|
    | **PromptTemplate** | 프롬프트 템플릿 |
    | **LLM** | 언어 모델 |
    | **OutputParser** | 출력 파싱 |
    | **Tool** | 외부 도구 |
    | **Agent** | 도구 선택 + 실행 |

    ### 왜 유용한가?
    - 재사용 가능한 컴포넌트
    - 테스트 용이성
    - 유연한 조합
    """)


# LangChain 스타일 컴포넌트들
class PromptTemplate:
    """프롬프트 템플릿"""
    def __init__(self, template: str, input_variables: list):
        self.template = template
        self.input_variables = input_variables

    def format(self, **kwargs):
        result = self.template
        for var in self.input_variables:
            result = result.replace(f"{{{var}}}", str(kwargs.get(var, "")))
        return result


class OutputParser:
    """출력 파서"""
    @staticmethod
    def parse_json(text):
        try:
            json_start = text.find('{')
            json_end = text.rfind('}') + 1
            if json_start >= 0:
                return json.loads(text[json_start:json_end])
        except:
            pass
        return {"raw": text}

    @staticmethod
    def parse_list(text):
        lines = text.strip().split('\n')
        return [line.strip('- ').strip() for line in lines if line.strip()]


class LLMChain:
    """LLM 체인"""
    def __init__(self, llm_session, model, prompt_template, output_parser=None):
        self.session = llm_session
        self.model = model
        self.prompt_template = prompt_template
        self.output_parser = output_parser

    def run(self, **kwargs):
        prompt = self.prompt_template.format(**kwargs)
        response = complete_llm(self.session, self.model, prompt)
        if self.output_parser:
            if self.output_parser == "json":
                return OutputParser.parse_json(response)
            elif self.output_parser == "list":
                return OutputParser.parse_list(response)
        return response


class Tool:
    """도구"""
    def __init__(self, name, description, func):
        self.name = name
        self.description = description
        self.func = func

    def run(self, *args, **kwargs):
        return self.func(*args, **kwargs)


class Agent:
    """Agent (도구 선택 + 실행)"""
    def __init__(self, llm_session, model, tools):
        self.session = llm_session
        self.model = model
        self.tools = {t.name: t for t in tools}

    def run(self, query):
        # 도구 설명 생성 + LLM 호출 (이미 구현됨)
        tools_desc = "\n".join([f"- {t.name}: {t.description}" for t in self.tools.values()])

        decide_prompt = f"""도구를 선택하세요.

도구: {tools_desc}

질문: "{query}"

JSON: {{"tool": "도구명", "input": "입력값"}} 또는 {{"tool": null, "answer": "직접답변"}}"""

        response = complete_llm(self.session, self.model, decide_prompt)
        decision = OutputParser.parse_json(response)

        # TODO: 선택된 도구 실행 후 결과 반환 (3줄)
        # 힌트: tool = self.tools[도구명], result = tool.run(입력값)
        #       {"tool": 도구명, "result": 결과} 반환
        if decision.get("tool") and decision["tool"] in self.tools:
            pass  # TODO를 완성하세요

        return {"answer": decision.get("answer", response)}


# 도구 정의
tools = [
    Tool("get_time", "현재 시간 반환", lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
    Tool("calculate", "수학 계산", lambda expr: str(eval(expr)) if all(c in "0123456789+-*/(). " for c in expr) else "오류"),
    Tool("summarize", "텍스트 요약", lambda text: f"요약: {text[:50]}..."),
]

# Agent 생성
agent = Agent(session, "llama3.1-70b", tools)

# 체인 예시
summary_template = PromptTemplate(
    template="다음 텍스트를 {style} 스타일로 요약하세요:\n\n{text}\n\n요약:",
    input_variables=["text", "style"]
)

summary_chain = LLMChain(session, "llama3.1-70b", summary_template)

# UI
st.write("### 🧪 LangChain 패턴 테스트")

tab1, tab2, tab3 = st.tabs(["🔗 체인", "🛠️ Agent", "📝 템플릿"])

with tab1:
    st.write("**요약 체인 테스트**")

    sample_text = st.text_area(
        "텍스트",
        "인공지능(AI)은 인간의 학습능력, 추론능력, 지각능력을 컴퓨터 프로그램으로 실현한 기술입니다. "
        "최근에는 딥러닝과 대규모 언어 모델의 발전으로 다양한 분야에서 활용되고 있습니다."
    )

    style = st.selectbox("스타일", ["간결한", "학술적인", "친근한"])

    if st.button("체인 실행", key="chain"):
        with st.spinner("체인 실행 중..."):
            result = summary_chain.run(text=sample_text, style=style)
        st.success(result)

with tab2:
    st.write("**Agent 테스트**")

    st.write("사용 가능한 도구:")
    for tool in tools:
        st.write(f"- **{tool.name}**: {tool.description}")

    agent_query = st.text_input("질문", "지금 몇 시야?", key="agent_query")

    if st.button("Agent 실행", key="agent"):
        with st.spinner("Agent 실행 중..."):
            result = agent.run(agent_query)

        if "tool" in result:
            st.info(f"🔧 사용된 도구: {result['tool']}")
            st.success(f"결과: {result['result']}")
        else:
            st.write(result.get("answer", ""))

with tab3:
    st.write("**프롬프트 템플릿 테스트**")

    template_str = st.text_area(
        "템플릿 (변수는 {변수명} 형식)",
        "{topic}에 대해 {audience}를 위한 설명을 작성하세요."
    )

    # 변수 추출
    import re
    variables = re.findall(r'\{(\w+)\}', template_str)

    var_values = {}
    cols = st.columns(len(variables)) if variables else [st]
    for i, var in enumerate(variables):
        with cols[i]:
            var_values[var] = st.text_input(f"{var}", key=f"var_{var}")

    if st.button("템플릿 실행", key="template"):
        template = PromptTemplate(template_str, variables)
        formatted = template.format(**var_values)

        st.write("**생성된 프롬프트:**")
        st.code(formatted)

        with st.spinner("LLM 호출 중..."):
            result = complete_llm(session, "llama3.1-70b", formatted)
        st.success(result)
