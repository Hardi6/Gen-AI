import os
import streamlit as st
from openai import OpenAI

st.set_page_config(page_title="LLM Chat • Streamlit + OpenAI", page_icon="💬", layout="centered")

# -----------------
# Sidebar controls
# -----------------
st.sidebar.title("⚙️ Settings")

# Prefer Streamlit Secrets if available
default_key = st.secrets.get("OPENAI_API_KEY", "") if hasattr(st, "secrets") else ""
api_key = st.sidebar.text_input(
    "OpenAI API key",
    type="password",
    value=default_key,
    help="Add in Settings > Secrets on Streamlit Cloud as OPENAI_API_KEY for production",
)

model = st.sidebar.text_input(
    "Model",
    value="gpt-4o-mini",
    help="Any available OpenAI chat model (e.g., gpt-5, gpt-4.1, gpt-4o, gpt-4o-mini, o4-mini)",
)

temperature = st.sidebar.slider("Temperature", 0.0, 2.0, 0.7, 0.1)
max_tokens = st.sidebar.slider("Max tokens", 32, 4096, 1024, 32)

with st.sidebar.expander("System prompt", expanded=False):
    system_prompt = st.text_area(
        "",
        value=(
            "You are a helpful assistant. Answer clearly, and format with Markdown where helpful."
        ),
        height=120,
    )

col1 = st.sidebar.columns(2)
with col1:
    clear_chat = st.button("🧹 Clear chat", use_container_width=True)

if clear_chat:
    st.session_state.pop("messages", None)
    st.session_state.pop("last_response", None)

# -----------------
# Helpers
# -----------------
@st.cache_resource(show_spinner=False)
def get_client(_api_key: str):
    if not _api_key:
        return None
    return OpenAI(api_key=_api_key)


def init_session():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    # Ensure we always start with a system message (not shown in UI)
    has_system = any(m.get("role") == "system" for m in st.session_state.messages)
    if not has_system and system_prompt:
        st.session_state.messages.insert(0, {"role": "system", "content": system_prompt})


def render_history():
    for m in st.session_state.messages:
        if m["role"] == "system":
            continue  # don't render system msg
        with st.chat_message("user" if m["role"] == "user" else "assistant"):
            st.markdown(m["content"])  # content is plain text/markdown


# -----------------
# UI: Header & Chat
# -----------------
st.title("💬 Streamlit Chat (OpenAI)")

client = get_client(api_key)

if not api_key:
    st.info(
        "Enter your OpenAI API key in the sidebar to start chatting. On Streamlit Cloud, store it in Secrets as `OPENAI_API_KEY`."
    )

init_session()
render_history()

# Chat input
prompt = st.chat_input("Type your message and hit Enter…")

if prompt and client:
    # Add user message to state and render
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Create streaming placeholder for assistant
    with st.chat_message("assistant"):
        stream_area = st.empty()
        streamed_text = ""

        # Call the Chat Completions API with streaming
        try:
            stream = client.chat.completions.create(
                model=model,
                messages=[
                    m for m in st.session_state.messages if m["role"] in {"system", "user", "assistant"}
                ],
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True,
            )

            # Stream chunks as they arrive
            for chunk in stream:
                if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
                    token = chunk.choices[0].delta.content
                    streamed_text += token
                    stream_area.markdown(streamed_text)

        except Exception as e:
            streamed_text = f"⚠️ Error: {e}"
            stream_area.markdown(streamed_text)

        # Persist assistant response
        st.session_state.messages.append({"role": "assistant", "content": streamed_text})

elif prompt and not client:
    st.warning("Please provide a valid OpenAI API key to send messages.")

