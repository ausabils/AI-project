import streamlit as st
from document_processor import load_docx_knowledge_base
from rag_engine import generate_rag_response

DOCX_PATH = "Informasi_Mata_Kuliah_AI_UNP.docx"

st.set_page_config(
    page_title="Chatbot Mata Kuliah AI - UNP",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS untuk memperbesar tulisan & mempercantik tampilan agar nyaman di mata
st.markdown("""
<style>
    /* Perbesar font utama di seluruh halaman */
    html, body, [class*="css"] {
        font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
        font-size: 17px !important;
    }

    /* Area utama lebih lega & rapi */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 5rem !important;
        max-width: 1050px !important;
    }

    /* Banner Header Modern */
    .hero-banner {
        background: linear-gradient(135deg, #1e3a8a 0%, #2563eb 100%);
        color: white;
        padding: 1.8rem 2rem;
        border-radius: 16px;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 15px rgba(37, 99, 235, 0.2);
    }
    .hero-banner h1 {
        color: white !important;
        font-size: 2rem !important;
        margin-bottom: 0.4rem !important;
        font-weight: 700 !important;
    }
    .hero-banner p {
        color: #e0e7ff !important;
        font-size: 1.05rem !important;
        margin: 0 !important;
    }

    /* Tombol Pertanyaan Cepat lebih besar & empuk */
    div.stButton > button {
        font-size: 16px !important;
        padding: 0.75rem 1rem !important;
        border-radius: 12px !important;
        border: 1px solid #cbd5e1 !important;
        background-color: #f8fafc !important;
        color: #1e293b !important;
        text-align: left !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05) !important;
    }
    div.stButton > button:hover {
        background-color: #eff6ff !important;
        border-color: #3b82f6 !important;
        color: #1d4ed8 !important;
        transform: translateY(-1px);
    }

    /* Perbesar teks di dalam gelembung chat */
    [data-testid="stChatMessageContent"] p,
    [data-testid="stChatMessageContent"] li {
        font-size: 17.5px !important;
        line-height: 1.65 !important;
    }

    /* Perbesar teks di Sidebar */
    [data-testid="stSidebar"] {
        background-color: #f8fafc !important;
    }
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] li {
        font-size: 15.5px !important;
        line-height: 1.5 !important;
    }

    /* Perbesar kotak input chat bawah */
    [data-testid="stChatInput"] textarea {
        font-size: 17px !important;
        padding: 0.8rem !important;
    }
</style>
""", unsafe_allow_html=True)

# Muat Knowledge Base dari file Word
documents = load_docx_knowledge_base(DOCX_PATH)

# Sidebar status Knowledge Base & Panduan Kata Kunci
with st.sidebar:
    st.markdown("## 📚 Knowledge Base")
    if documents:
        st.success(f"**Aktif:** `{DOCX_PATH}`\n\nTotal **{len(documents)} segmen** siap dicari.")
    else:
        st.error(f"File `{DOCX_PATH}` tidak ditemukan di folder proyek!")

    st.markdown("---")
    st.markdown("### 🔑 Kata Kunci Pencarian")
    st.markdown(
        """
        Gunakan topik berikut saat bertanya:
        - **Dosen & Jadwal:** `dosen pengampu`, `5337`, `jadwal kuliah`, `ruang lab`, `SKS`
        - **Konsep & Tujuan:** `apa itu AI`, `tujuan belajar AI`, `agen cerdas`, `weak AI`
        - **Silabus Pertemuan:** `pertemuan 1`, `BFS DFS`, `UTS`, `machine learning`, `ANN`, `NLP RAG`, `UAS`
        - **Penilaian:** `komponen penilaian`, `bobot tugas`, `praktikum Python`
        """
    )
    st.markdown("---")
    if st.button("🗑️ Bersihkan Obrolan", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# Header Banner Utama
st.markdown("""
<div class="hero-banner">
    <h1>🤖 Asisten Akademik Mata Kuliah AI - UNP</h1>
    <p>Sistem Tanya Jawab Berbasis <b>Constrained RAG</b> (TF-IDF Matching + Grounded Gemini LLM)</p>
</div>
""", unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []

# Tombol Pertanyaan Cepat (Quick Prompts) dalam 2 kolom lega
st.markdown("#### 💡 Pilih Pertanyaan Cepat atau Ketik Sendiri di Bawah:")
quick_questions = [
    "👩‍🏫 Siapa dosen pengampu dan jadwal kuliah AI?",
    "🧠 Apa itu Artificial Intelligence (AI)?",
    "🎯 Apa saja tujuan belajar mata kuliah AI?",
    "📖 Materi pertemuan 14-15 membahas apa?",
    "📊 Bagaimana komponen penilaian mata kuliah AI?",
    "❓ Siapa rektor UNP saat ini?"
]

cols = st.columns(2)
selected_prompt = None
for idx, question in enumerate(quick_questions):
    if cols[idx % 2].button(question, key=f"btn_{idx}", use_container_width=True):
        # Bersihkan emoji di depan saat dikirim sebagai pertanyaan
        selected_prompt = question.split(" ", 1)[1]

st.markdown("---")

# Tampilkan riwayat percakapan
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "meta" in msg:
            st.caption(msg["meta"])

# Terima input baik dari klik tombol maupun ketikan manual
chat_input_text = st.chat_input("Ketik pertanyaanmu seputar mata kuliah AI UNP di sini...")
user_query = selected_prompt if selected_prompt else chat_input_text

if user_query:
    st.session_state.messages.append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.markdown(user_query)

    with st.chat_message("assistant"):
        with st.spinner("Sedang mencari informasi di Knowledge Base..."):
            jawaban, jalur, skor = generate_rag_response(user_query, documents)
            st.markdown(jawaban)
            meta_info = f"🔍 Jalur: **{jalur}** | Skor TF-IDF: **{skor:.2f}**"
            st.caption(meta_info)

    st.session_state.messages.append({
        "role": "assistant",
        "content": jawaban,
        "meta": meta_info
    })