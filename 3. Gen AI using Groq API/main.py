import streamlit as st
import requests
import random

st.set_page_config(page_title="Groq Prompt Playground", page_icon="⚡", layout="centered")

# --- Sidebar for API key & model selection ---
st.sidebar.header("Groq API Settings")
groq_api_key = st.sidebar.text_input("Groq API Key", type="password")
model_id = st.sidebar.selectbox(
    "Model",
    [
        "llama3-8b-8192",       # Fast, small model
    ],
    index=0
)

# --- UI Header ---
st.title("Generative AI")
st.write("Experiment with prompts using Groq's ultra-fast LLMs.")

# --- Prompt Input ---
prompt = st.text_area("✍️ Enter your prompt:", "Explain how rainbows are formed.")

# --- Auto parameter chooser ---
def auto_parameters(prompt_text):
    temperature = round(random.uniform(0.6, 1.0), 2)
    max_tokens = min(len(prompt_text.split()) * 10, 5000)
    top_p = round(random.uniform(0.85, 0.95), 2)
    return temperature, max_tokens, top_p

if st.button("🚀 Generate Text"):
    if not groq_api_key:
        st.error("Please enter your Groq API key in the sidebar.")
    else:
        temp, max_tok, top_p = auto_parameters(prompt)
        with st.spinner("Generating..."):
            try:
                # Groq API endpoint
                url = "https://api.groq.com/openai/v1/chat/completions"

                headers = {
                    "Authorization": f"Bearer {groq_api_key}",
                    "Content-Type": "application/json"
                }

                payload = {
                    "model": model_id,
                    "messages": [
                        {"role": "system", "content": "You are a helpful AI assistant."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": temp,
                    "max_tokens": max_tok,
                    "top_p": top_p
                }

                response = requests.post(url, headers=headers, json=payload)
                response.raise_for_status()
                data = response.json()

                generated_text = data["choices"][0]["message"]["content"]

                st.subheader("📝 Generated Text")
                st.write(generated_text)
                st.caption(f"Parameters → temperature={temp}, max_tokens={max_tok}, top_p={top_p}")

            except Exception as e:
                st.error(f"Error: {e}")


