
import os
import json
import streamlit as st

st.set_page_config(page_title="Groq Chat • Streaming", page_icon="💬", layout="wide")
st.title("💬 Groq LLM Chat (Streaming)")

with st.sidebar:
    st.header("Settings")
    default_key = os.environ.get("GROQ_API_KEY", "")
    api_key = st.text_input("GROQ_API_KEY", type="password", value=default_key, help="Paste your Groq API key or set env var GROQ_API_KEY")
    model = st.selectbox("Model", [
        "llama3-70b-8192",
        "llama3-8b-8192",
    ], index=0)
    system_prompt = st.text_area("System prompt (optional)", "You are a helpful assistant.", height=100)
    temperature = st.slider("Temperature", 0.0, 1.0, 0.7, 0.1)
    max_tokens = st.slider("Max tokens (response)", 64, 4096, 512, 64)
    if st.button("Clear chat"):
        st.session_state.messages = []

if "messages" not in st.session_state:
    st.session_state.messages = []

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

user_input = st.chat_input("Say something...")

def stream_groq(messages, model, api_key, temperature=0.7, max_tokens=512):
    from groq import Groq
    client = Groq(api_key=api_key)
    stream = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
        stream=True,
    )
    for chunk in stream:
        delta = chunk.choices[0].delta
        if delta and delta.content:
            yield delta.content

if user_input:
    if not api_key:
        st.error("Please enter your GROQ_API_KEY in the sidebar.")
        st.stop()

    if system_prompt.strip():
        base_msgs = [m for m in st.session_state.messages if m["role"] != "system"]
        st.session_state.messages = [{"role": "system", "content": system_prompt}] + base_msgs
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        placeholder = st.empty()
        partial = ""
        try:
            for token in stream_groq(st.session_state.messages, model, api_key, temperature, max_tokens):
                partial += token
                placeholder.markdown(partial)
        except Exception as e:
            st.error(f"Error: {e}")
        else:
            st.session_state.messages.append({"role": "assistant", "content": partial})


