# import streamlit as st
# import requests
# import os

# BACKEND_URL = os.environ.get("BACKEND_URL", "https://drive-search-backend.onrender.com")

# st.set_page_config(page_title="Drive Search Chat", layout="wide")

# st.title("Drive Search Chat")

# if "messages" not in st.session_state:
#     st.session_state.messages = []

# with st.form("user_input", clear_on_submit=True):
#     user_input = st.text_input("Ask about files in the Drive folder:", "Find the financial report from last week")
#     submitted = st.form_submit_button("Send")

# if submitted and user_input:
#     st.session_state.messages.append({"role": "user", "text": user_input})
#     # call backend nl_search
#     try:
#         resp = requests.post(f"{BACKEND_URL}/nl_search", json={"query": user_input}, timeout=30)
#         if resp.status_code == 200:
#             files = resp.json()
#             st.session_state.messages.append({"role": "system", "text": f"Found {len(files)} files:"})
#             for f in files:
#                 st.session_state.messages.append({"role": "file", "text": f"{f.get('name')} ({f.get('mimeType')}) - {f.get('webViewLink')}"})
#         else:
#             st.session_state.messages.append({"role": "system", "text": f"Error: {resp.text}"})
#     except Exception as e:
#         st.session_state.messages.append({"role": "system", "text": f"Request error: {e}"})

# for msg in st.session_state.messages:
#     if msg["role"] == "user":
#         st.markdown(f"**You:** {msg['text']}")
#     elif msg["role"] == "system":
#         st.markdown(f"**Agent:** {msg['text']}")
#     else:
#         st.write(msg['text'])















import streamlit as st
import requests
import os
from datetime import datetime

# =========================
# CONFIG
# =========================

BACKEND_URL = os.environ.get(
    "BACKEND_URL",
    "https://drive-search-backend.onrender.com"
)

st.set_page_config(
    page_title="Drive Search AI",
    page_icon="🔍",
    layout="wide"
)

# =========================
# CUSTOM CSS
# =========================

st.markdown("""
<style>
.main {
    background-color: #0E1117;
    color: white;
}

.stTextInput input {
    border-radius: 12px;
    padding: 12px;
}

.user-msg {
    background: #1F6FEB;
    padding: 14px;
    border-radius: 15px;
    margin-bottom: 10px;
    color: white;
}

.bot-msg {
    background: #262730;
    padding: 14px;
    border-radius: 15px;
    margin-bottom: 10px;
    color: white;
}

.file-card {
    background: #161B22;
    padding: 15px;
    border-radius: 15px;
    margin-top: 10px;
    border: 1px solid #30363D;
}

.title {
    text-align: center;
    font-size: 42px;
    font-weight: bold;
    margin-bottom: 10px;
}

.subtitle {
    text-align: center;
    color: #8B949E;
    margin-bottom: 30px;
}

</style>
""", unsafe_allow_html=True)

# =========================
# HEADER
# =========================

st.markdown('<div class="title">🔍 Drive Search AI</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">Search files intelligently using natural language</div>',
    unsafe_allow_html=True
)

# =========================
# SESSION STATE
# =========================

if "messages" not in st.session_state:
    st.session_state.messages = []

# =========================
# SIDEBAR
# =========================

with st.sidebar:
    st.title("⚡ Quick Searches")

    quick_queries = [
        "Find the financial report from last week",
        "Show presentation files",
        "Find invoices from April",
        "Search PDF files",
        "Find meeting notes"
    ]

    for q in quick_queries:
        if st.button(q):
            st.session_state["quick_query"] = q

    st.divider()

    if st.button("🗑 Clear Chat"):
        st.session_state.messages = []
        st.rerun()

# =========================
# INPUT
# =========================

default_query = st.session_state.get(
    "quick_query",
    ""
)

query = st.chat_input(
    "Ask about files in your Drive...",
)

if default_query and not query:
    query = default_query
    st.session_state["quick_query"] = ""

# =========================
# PROCESS QUERY
# =========================

if query:
    current_time = datetime.now().strftime("%H:%M")

    st.session_state.messages.append({
        "role": "user",
        "text": query,
        "time": current_time
    })

    with st.spinner("🔎 Searching Drive..."):

        try:
            response = requests.post(
                f"{BACKEND_URL}/nl_search",
                json={"query": query},
                timeout=60
            )

            if response.status_code == 200:
                files = response.json()

                if len(files) == 0:
                    st.session_state.messages.append({
                        "role": "assistant",
                        "text": "No matching files found.",
                        "time": current_time
                    })

                else:
                    st.session_state.messages.append({
                        "role": "assistant",
                        "text": f"Found {len(files)} matching files.",
                        "files": files,
                        "time": current_time
                    })

            else:
                st.session_state.messages.append({
                    "role": "assistant",
                    "text": f"❌ Backend Error:\n\n{response.text}",
                    "time": current_time
                })

        except Exception as e:
            st.session_state.messages.append({
                "role": "assistant",
                "text": f"⚠ Request Failed:\n\n{str(e)}",
                "time": current_time
            })

# =========================
# CHAT DISPLAY
# =========================

for msg in st.session_state.messages:

    if msg["role"] == "user":

        st.markdown(f"""
        <div class="user-msg">
            <b>🧑 You</b><br><br>
            {msg['text']}
            <div style="font-size:12px;opacity:0.7;margin-top:8px;">
                {msg['time']}
            </div>
        </div>
        """, unsafe_allow_html=True)

    else:

        st.markdown(f"""
        <div class="bot-msg">
            <b>🤖 Agent</b><br><br>
            {msg['text']}
            <div style="font-size:12px;opacity:0.7;margin-top:8px;">
                {msg['time']}
            </div>
        </div>
        """, unsafe_allow_html=True)

        if "files" in msg:

            for file in msg["files"]:

                file_name = file.get("name", "Unknown File")
                mime_type = file.get("mimeType", "Unknown")
                link = file.get("webViewLink", "#")

                st.markdown(f"""
                <div class="file-card">
                    <h4>📄 {file_name}</h4>
                    <p><b>Type:</b> {mime_type}</p>
                    <a href="{link}" target="_blank">
                        🔗 Open File
                    </a>
                </div>
                """, unsafe_allow_html=True)