import os
import streamlit as st
from openai import OpenAI
import pypdf
from openai import OpenAI 

st.set_page_config(page_title="SmartDocs AI Assistant", page_icon="🧠", layout="centered")

st.markdown("""
<style>
    body { background-color: #f0f4ff; }
    #MainMenu, footer { visibility: hidden; }
    
    .main { background-color: #f0f4ff; }
            
    section[data-testid="stSidebar"] {
    background: #f0f4ff !important;
}

section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] .stMarkdown {
    color: #1a1a2e !important;
}     
    
    .hero {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 20px;
        text-align: center;
        margin-bottom: 1.5rem;
        color: white;
    }
    
    .hero h1 {
        font-size: 2.2rem;
        font-weight: 800;
        margin: 0;
        color: white;
    }
    
    .hero p {
        font-size: 1rem;
        opacity: 0.9;
        margin: 0.5rem 0 0 0;
        color: white;
    }
    
    .feature-box {
        background: rgba(255,255,255,0.15);
        border-radius: 15px;
        padding: 1rem 1.5rem;
        margin-bottom: 1rem;
        border-left: 5px solid #667eea;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }
    
    .upload-box {
        background: white;
        border-radius: 15px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        border: 2px dashed #667eea;
        text-align: center;
    }

    .stChatMessage {
        border-radius: 15px;
        margin-bottom: 8px;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.5rem 1rem;
        font-weight: 600;
    }
    
    .success-badge {
        background: #d4edda;
        color: #155724;
        padding: 0.5rem 1rem;
        border-radius: 10px;
        font-weight: 600;
        display: inline-block;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Hero header
st.markdown("""
<div class="hero">
    <h1>🧠 SmartDocs AI Assistant</h1>
    <p>Upload any PDF and instantly ask questions about it ✨</p>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### 🧠 SmartDocs")
    st.markdown("""
    <div class="feature-box">
    <b>How it works:</b><br><br>
    📄 Step 1 — Upload your PDF<br><br>
    💬 Step 2 — Ask any question<br><br>
    ✅ Step 3 — Get instant answers!
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("**Works great for:**")
    st.markdown("""
    - 📋 Business documents
    - 🏨 Hotel bookings
    - 📜 Legal contracts
    - 🍽️ Restaurant menus
    - 📦 Product catalogues
    - 🏥 Medical reports
    """)
    
    st.divider()
    
    api_key = st.text_input("🔑 OpenAI API Key", type="password",
                            value=os.getenv("OPENAI_API_KEY", ""),
                            help="Get your key at platform.openai.com")
    st.divider()
    
    if st.button("🔄 Start Fresh"):
        st.session_state.messages = []
        st.session_state.pdf_text = ""
        st.session_state.pdf_name = ""
        st.rerun()
    
    st.markdown("*Built with Python + OpenAI + Streamlit* 🚀")

# Session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "pdf_text" not in st.session_state:
    st.session_state.pdf_text = ""
if "pdf_name" not in st.session_state:
    st.session_state.pdf_name = ""

def extract_pdf_text(pdf_file):
    reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

# Upload section
st.markdown("### 📄 Upload Your Document")
uploaded_file = st.file_uploader(
    "Drop your PDF here",
    type="pdf",
    help="Upload any PDF — invoices, menus, contracts, reports and more!"
)

if uploaded_file:
    if uploaded_file.name != st.session_state.pdf_name:
        st.session_state.pdf_text = extract_pdf_text(uploaded_file)
        st.session_state.pdf_name = uploaded_file.name
        st.session_state.messages = []
    
    st.markdown(f"""
    <div class="success-badge">
    ✅ {uploaded_file.name} — Ready to answer questions!
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("💡 Try: What is this document about?")
    with col2:
        st.info("💡 Try: What are the key details?")
    with col3:
        st.info("💡 Try: Summarise this for me")

st.divider()

# Chat section
if st.session_state.pdf_text:
    st.markdown("### 💬 Ask Anything About Your Document")

if not st.session_state.messages and st.session_state.pdf_text:
    with st.chat_message("assistant"):
        st.markdown(f"Hey there! 👋 I've read **{st.session_state.pdf_name}** and I'm ready to answer your questions! What would you like to know? 🧠✨")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Ask me anything about your document..."):
    if not api_key:
        st.error("🔑 Please enter your OpenAI API key in the sidebar.")
        st.stop()
    if not st.session_state.pdf_text:
        st.warning("📄 Please upload a PDF first!")
        st.stop()

    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        with st.spinner("🧠 Reading your document..."):
            try:
                client = OpenAI(api_key=api_key)
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": f"""You are SmartDocs, a friendly 
                        and helpful document assistant. Answer questions ONLY based on 
                        this document:
                        
                        {st.session_state.pdf_text[:4000]}
                        
                        If the answer is not in the document say: 
                        'I could not find that information in the uploaded document. 
                        Could you check if it is mentioned elsewhere in your file? 📄'
                        
                        Keep answers clear, friendly and use bullet points for lists.
                        Use emojis occasionally to keep it friendly! ✨"""},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=500,
                )
                reply = response.choices[0].message.content
                st.markdown(reply)
                st.session_state.messages.append(
                    {"role": "assistant", "content": reply})
            except Exception as e:
                st.error(f"Error: {e}")
