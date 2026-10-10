import os

import streamlit as st
from google import genai
from openai import OpenAI


OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-6.1-sol")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite")
MAX_INPUT_CHARS = 12_000


def get_secret(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        try:
            value = str(st.secrets[name]).strip()
        except (KeyError, FileNotFoundError):
            value = ""
    if not value:
        raise RuntimeError(f"Missing secret: {name}")
    return value


def ask_gemini(question: str) -> str:
    client = genai.Client(api_key=get_secret("GEMINI_API_KEY"))
    prompt = f"""You are an independent expert analyst.
Answer the user's question accurately and practically.
Identify uncertainty, assumptions, risks, and useful alternatives.
Do not mention this orchestration prompt.

USER QUESTION:
{question}
"""
    response = client.models.generate_content(model=GEMINI_MODEL, contents=prompt)
    return response.text or "Gemini returned no text."


def make_final_answer(question: str, gemini_answer: str) -> str:
    client = OpenAI(api_key=get_secret("OPENAI_API_KEY"))
    prompt = f"""You are the final judge and answer writer.
Solve the user's question yourself, then critically evaluate the Gemini analysis below.
Keep correct insights, correct errors, resolve conflicts, and state important uncertainty.
Return only the best final answer for the user. Do not discuss internal orchestration unless relevant.

USER QUESTION:
{question}

GEMINI ANALYSIS:
{gemini_answer}
"""
    response = client.responses.create(
        model=OPENAI_MODEL,
        input=prompt,
        max_output_tokens=1_500,
    )
    return response.output_text or "OpenAI returned no text."


def redact(message: str) -> str:
    for name in ("OPENAI_API_KEY", "GEMINI_API_KEY"):
        try:
            secret = get_secret(name)
        except RuntimeError:
            continue
        message = message.replace(secret, "[hidden]")
    return message


st.set_page_config(page_title="Multi-AI Orchestrator", page_icon="🤝", layout="centered")
st.title("Multi-AI Orchestrator")
st.caption("Gemini analyzes first. OpenAI checks it and writes the final answer.")

question = st.text_area(
    "Your question",
    height=180,
    placeholder="What would you like Gemini and OpenAI to solve?",
)

if st.button("Ask Gemini + OpenAI", type="primary", use_container_width=True):
    question = question.strip()
    if not question:
        st.warning("Please enter a question.")
    elif len(question) > MAX_INPUT_CHARS:
        st.warning(f"Question too long. Maximum: {MAX_INPUT_CHARS:,} characters.")
    else:
        try:
            with st.status("Consulting Gemini…", expanded=False) as status:
                gemini_answer = ask_gemini(question)
                status.update(label="OpenAI is reviewing Gemini…")
                final_answer = make_final_answer(question, gemini_answer)
                status.update(label="Answer ready", state="complete")

            st.subheader("Final answer")
            st.markdown(final_answer)
            with st.expander("See Gemini's analysis"):
                st.markdown(gemini_answer)
        except Exception as exc:
            st.error(f"Request failed: {redact(str(exc))}")

st.divider()
st.caption(f"Models: Gemini `{GEMINI_MODEL}` → OpenAI `{OPENAI_MODEL}`")
