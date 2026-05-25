import streamlit as st
import os
import sys
from openai import OpenAI
import uuid
from datetime import datetime

# ==================== CONFIGURATION ====================
st.set_page_config(
    page_title="Aura AI",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)
# ==================== SESSION STATE INITIALIZATION ====================
if "chats" not in st.session_state:
    st.session_state.chats = {}

if "current_chat_id" not in st.session_state:
    initial_id = str(uuid.uuid4())
    st.session_state.chats[initial_id] = {
        "id": initial_id,
        "title": "New Chat",
        "messages": [],
        "created_at": datetime.now()
    }
    st.session_state.current_chat_id = initial_id

if "user_name" not in st.session_state:
    st.session_state.user_name = "Kashish"

if "show_attachments" not in st.session_state:
    st.session_state.show_attachments = False

if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = 0

if "current_uploaded_files" not in st.session_state:
    st.session_state.current_uploaded_files = []

# ==================== FREE API CORE SETUP (GROQ) ====================
if "GROQ_API_KEY" in st.secrets:
    api_key = st.secrets["GROQ_API_KEY"]
else:
    api_key = os.getenv("GROQ_API_KEY", "")

active_model_name = "llama-3.3-70b-versatile" 

# Kisi bhi extra verification check ko bypass karke direct client initialize kar rahe hain
if api_key:
    client = OpenAI(
        base_url="https://api.groq.com/openai/v1",
        api_key=api_key
    )
else:
    client = None
# ==================== STYLING ====================
st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #0f0f0f 0%, #1a1a1a 100%); }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    [data-testid="stSidebar"] { background: linear-gradient(180deg, #1e1e1e 0%, #161616 100%); border-right: 1px solid #2d2d2d; }
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p { color: #e0e0e0; font-size: 14px; }
    [data-testid="stChatMessage"] { background: transparent !important; padding: 1.5rem 1rem !important; margin-bottom: 0.5rem; }
    [data-testid="stChatMessage"][data-testid*="user"] { background: rgba(40, 40, 40, 0.3) !important; border-radius: 12px; }
    [data-testid="stChatMessage"][data-testid*="assistant"] { background: rgba(30, 30, 30, 0.2) !important; border-radius: 12px; }
    .stMarkdown { color: #f0f0f0 !important; font-size: 16px; line-height: 1.7; }
    code { background: #2d2d2d !important; color: #00ff88 !important; padding: 2px 6px; border-radius: 4px; font-size: 14px; }
    pre { background: #1a1a1a !important; border: 1px solid #2d2d2d; border-radius: 8px; padding: 1rem; }
    [data-testid="stChatInput"] { background: #1e1e1e !important; border: 1px solid #3d3d3d !important; border-radius: 24px !important; padding: 0.75rem 1.5rem !important; }
    [data-testid="stChatInput"] textarea { color: #f0f0f0 !important; font-size: 16px !important; }
    [data-testid="stChatInput"] textarea::placeholder { color: #808080 !important; }
    .stButton button { background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%); color: white; border: none; border-radius: 12px; padding: 0.6rem 1.5rem; font-weight: 600; font-size: 14px; transition: all 0.3s ease; box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3); }
    .stButton button:hover { transform: translateY(-2px); box-shadow: 0 6px 16px rgba(99, 102, 241, 0.4); }
    [data-testid="stSidebar"] .stButton button { background: transparent; color: #d0d0d0; border: 1px solid #3d3d3d; box-shadow: none; width: 100%; text-align: left; justify-content: flex-start; padding: 0.75rem 1rem; }
    [data-testid="stSidebar"] .stButton button:hover { background: rgba(99, 102, 241, 0.1); border-color: #6366f1; transform: none; }
    .welcome-container { text-align: center; padding: 4rem 2rem; max-width: 800px; margin: 0 auto; }
    .welcome-title { font-size: 3.5rem; font-weight: 800; background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #ec4899 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; margin-bottom: 1rem; line-height: 1.2; }
    .welcome-subtitle { font-size: 1.25rem; color: #a0a0a0; margin-bottom: 3rem; }
    .attachment-badge { display: inline-flex; align-items: center; gap: 0.5rem; background: rgba(99, 102, 241, 0.2); border: 1px solid rgba(99, 102, 241, 0.4); border-radius: 20px; padding: 0.4rem 1rem; margin: 0.25rem; font-size: 0.85rem; color: #d0d0d0; }
    .user-profile-box { position: fixed; bottom: 1rem; left: 0.5rem; width: 260px; background: rgba(30, 30, 30, 0.9); padding: 0.75rem; border-radius: 12px; border: 1px solid #2d2d2d; z-index: 999; }
</style>
""", unsafe_allow_html=True)

# ==================== HELPER FUNCTIONS ====================
def get_chat():
    return st.session_state.chats[st.session_state.current_chat_id]

def create_new_chat():
    new_id = str(uuid.uuid4())
    st.session_state.chats[new_id] = {
        "id": new_id,
        "title": "New Chat",
        "messages": [],
        "created_at": datetime.now()
    }
    st.session_state.current_chat_id = new_id
    st.session_state.current_uploaded_files = []
    st.rerun()

def delete_chat(chat_id):
    if chat_id in st.session_state.chats:
        del st.session_state.chats[chat_id]
        if chat_id == st.session_state.current_chat_id:
            if st.session_state.chats:
                st.session_state.current_chat_id = list(st.session_state.chats.keys())[0]
            else:
                create_new_chat()
        st.rerun()

def switch_chat(chat_id):
    st.session_state.current_chat_id = chat_id
    st.session_state.current_uploaded_files = []
    st.rerun()

def generate_chat_title(first_message):
    if len(first_message) > 30:
        return first_message[:27] + "..."
    return first_message

# ==================== SIDEBAR LAYER ====================
with st.sidebar:
    st.markdown(f"""
        <div style='text-align: center; padding: 1rem 0 1rem 0;'>
            <div style='font-size: 2.5rem; margin-bottom: 0.5rem;'>✨</div>
            <div style='font-size: 1.8rem; font-weight: 800; 
                        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
                        -webkit-background-clip: text;
                        -webkit-text-fill-color: transparent;'>
                Aura AI
            </div>
            <div style='font-size: 0.85rem; color: #a0a0a0; margin-top: 0.25rem;'>
                Active Core: {active_model_name}
            </div>
        </div>
    """, unsafe_allow_html=True)

    if st.button("➕ New Chat", use_container_width=True, key="new_chat_btn"):
        create_new_chat()

    st.markdown("<hr style='border: 0; height: 1px; background: #2d2d2d; margin: 1rem 0;'>", unsafe_allow_html=True)
    st.markdown("<div style='color: #808080; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 1rem;'>Chat History</div>", unsafe_allow_html=True)

    sorted_chats = sorted(
        st.session_state.chats.items(),
        key=lambda x: x[1]["created_at"],
        reverse=True
    )

    for chat_id, chat_data in sorted_chats:
        is_active = chat_id == st.session_state.current_chat_id
        col1, col2 = st.columns([4, 1])

        with col1:
            if st.button(
                f"✨ {chat_data['title']}" if is_active else f"💬 {chat_data['title']}",
                key=f"chat_{chat_id}",
                use_container_width=True,
                type="primary" if is_active else "secondary"
            ):
                switch_chat(chat_id)

        with col2:
            if st.button("🗑️", key=f"del_{chat_id}", use_container_width=True):
                delete_chat(chat_id)

    st.markdown("<hr style='border: 0; height: 1px; background: #2d2d2d; margin: 1.5rem 0;'>", unsafe_allow_html=True)

    st.markdown(f"""
        <div class="user-profile-box">
            <div style='display: flex; align-items: center; gap: 0.75rem;'>
                <div style='width: 36px; height: 36px; border-radius: 50%; 
                            background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
                            display: flex; align-items: center; justify-content: center;
                            font-weight: 700; font-size: 1.1rem; color: white;'>
                    {st.session_state.user_name[0].upper()}
                </div>
                <div>
                    <div style='color: #f0f0f0; font-weight: 600; font-size: 0.9rem;'>
                        {st.session_state.user_name}
                    </div>
                    <div style='color: #808080; font-size: 0.75rem;'> Academic Workspace </div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

# ==================== MAIN CHAT FRAME ====================
current_chat = get_chat()

if len(current_chat["messages"]) > 0:
    for message in current_chat["messages"]:
        avatar = "👤" if message["role"] == "user" else "🤖"
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])

else:
    st.markdown("""
        <div class='welcome-container'>
            <div class='welcome-title'>Welcome to Aura AI</div>
            <div class='welcome-subtitle'>Select an automated task strategy or initialize prompt context inputs below.</div>
        </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    suggestions = [
        {"icon": "💡", "title": "Explain a concept", "prompt": "Can you explain quantum computing in simple terms?"},
        {"icon": "📊", "title": "Analyze data", "prompt": "I have a dataset I'd like to analyze. Can you help me identify trends?"},
        {"icon": "✍️", "title": "Write content", "prompt": "Can you help me write a professional email?"},
        {"icon": "🔧", "title": "Solve a problem", "prompt": "I'm having an issue with my code. Can you help me debug it?"}
    ]

    for i, suggestion in enumerate(suggestions):
        with col1 if i % 2 == 0 else col2:
            if st.button(f"{suggestion['icon']} {suggestion['title']}", key=f"sug_{i}", use_container_width=True):
                st.session_state.suggestion_prompt = suggestion['prompt']
                st.rerun()

suggestion_target = st.session_state.pop("suggestion_prompt", None)

# ==================== ENGINE INFERENCE LOGIC ====================
if prompt := st.chat_input("Ask me anything...", key="chat_input") or suggestion_target:
    actual_prompt = prompt if prompt else suggestion_target
    user_msg = {"role": "user", "content": actual_prompt, "timestamp": datetime.now()}
    current_chat["messages"].append(user_msg)

    if current_chat["title"] == "New Chat":
        current_chat["title"] = generate_chat_title(actual_prompt)

    st.rerun()

if len(current_chat["messages"]) > 0 and current_chat["messages"][-1]["role"] == "user":
    last_user_message = current_chat["messages"][-1]
    
    with st.chat_message("assistant", avatar="🤖"):
        message_placeholder = st.empty()
        full_response = ""

        if not client:
            full_response = "⚠️ Please configure your GROQ_API_KEY inside the core initialization module thread."
            message_placeholder.markdown(full_response)
        else:
            try:
                api_messages = []
                for m in current_chat["messages"]:
                    api_messages.append({"role": m["role"], "content": m["content"]})

                response = client.chat.completions.create(
                    model=active_model_name,
                    messages=api_messages,
                    stream=True
                )
                
                for chunk in response:
                    if chunk.choices[0].delta.content:
                        full_response += chunk.choices[0].delta.content
                        message_placeholder.markdown(full_response + "▌")
                message_placeholder.markdown(full_response)
                
            except Exception as e:
                full_response = f"❌ Core API Runtime Fault: {str(e)}"
                message_placeholder.markdown(full_response)

    current_chat["messages"].append({
        "role": "assistant",
        "content": full_response,
        "timestamp": datetime.now()
    })
    st.rerun()
