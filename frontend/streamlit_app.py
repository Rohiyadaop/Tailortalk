import streamlit as st
import requests
import os

BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:8000")

st.set_page_config(page_title="Drive Search Chat", layout="wide")

st.title("Drive Search Chat")

if "messages" not in st.session_state:
    st.session_state.messages = []

with st.form("user_input", clear_on_submit=True):
    user_input = st.text_input("Ask about files in the Drive folder:", "Find the financial report from last week")
    submitted = st.form_submit_button("Send")

if submitted and user_input:
    st.session_state.messages.append({"role": "user", "text": user_input})
    # call backend nl_search
    try:
        resp = requests.post(f"{BACKEND_URL}/nl_search", json={"query": user_input}, timeout=30)
        if resp.status_code == 200:
            files = resp.json()
            st.session_state.messages.append({"role": "system", "text": f"Found {len(files)} files:"})
            for f in files:
                st.session_state.messages.append({"role": "file", "text": f"{f.get('name')} ({f.get('mimeType')}) - {f.get('webViewLink')}"})
        else:
            st.session_state.messages.append({"role": "system", "text": f"Error: {resp.text}"})
    except Exception as e:
        st.session_state.messages.append({"role": "system", "text": f"Request error: {e}"})

for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f"**You:** {msg['text']}")
    elif msg["role"] == "system":
        st.markdown(f"**Agent:** {msg['text']}")
    else:
        st.write(msg['text'])
