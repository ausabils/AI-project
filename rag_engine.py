import os
import re
from dotenv import load_dotenv
from google import genai
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

load_dotenv(override=True)

NOT_FOUND_MESSAGE = "Maaf, saya tidak tahu. Informasi tersebut tidak tersedia di dalam Knowledge Base."

def tfidf_retrieval(user_query, documents, top_k=3):
    """Menghitung skor kemiripan TF-IDF + Cosine Similarity dan mengambil top-k dokumen."""
    if not documents:
        return 0.0, []

    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(documents + [user_query])
    similarities = cosine_similarity(tfidf_matrix[-1], tfidf_matrix[:-1])[0]

    max_score = float(similarities.max())
    top_indices = similarities.argsort()[::-1][:top_k]

    top_docs = [
        {"text": documents[i], "score": float(similarities[i])}
        for i in top_indices
        if similarities[i] > 0.05
    ]
    return max_score, top_docs

def format_local_fallback(top_docs):
    """Menyusun jawaban bersih dari Knowledge Base jika server LLM timeout/sibuk."""
    cleaned_items = []
    for doc in top_docs[:2]:
        text = re.sub(r"^\[.*?\]\s*", "", doc["text"]).strip()
        cleaned_items.append(text)
    return "\n\n".join(cleaned_items)

def ask_constrained_llm(user_query, top_docs):
    """Mengirim top-k dokumen ke Gemini dengan prompt terbatas dan fallback otomatis."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return format_local_fallback(top_docs)

    context = "\n\n".join(
        f"Konteks {idx+1} (Skor: {doc['score']:.2f}): {doc['text']}"
        for idx, doc in enumerate(top_docs)
    )

    prompt = f"""
    Kamu adalah asisten akademik Universitas Negeri Padang (UNP) untuk mata kuliah Artificial Intelligence (AI).
    Jawab pertanyaan pengguna HANYA berdasarkan KONTEKS di bawah ini.

    ATURAN KETAT:
    1. DILARANG menggunakan pengetahuan luar selain KONTEKS yang diberikan.
    2. DILARANG menebak atau mengarang informasi yang tidak tertulis di KONTEKS.
    3. Jika KONTEKS tidak cukup atau tidak relevan dengan pertanyaan, wajib jawab persis:
       "{NOT_FOUND_MESSAGE}"
    4. Jawab dengan bahasa Indonesia yang jelas, rapi, dan langsung ke inti pertanyaan.

    KONTEKS:
    {context}

    PERTANYAAN PENGGUNA:
    {user_query}

    JAWABAN:
    """

    # Timeout singkat (8000 ms = 8 detik) agar cepat pindah jika server lambat
    client = genai.Client(api_key=api_key, http_options={"timeout": 8000})
    candidate_models = ["gemini-3.8-flash-lite", "gemini-3.8-flash", "gemini-2.5-flash"]

    for model_name in candidate_models:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt
            )
            if response.text:
                return response.text.strip()
        except Exception:
            continue

    # Jika semua model Gemini sedang lambat/penuh, langsung tampilkan data akurat dari KB
    return format_local_fallback(top_docs)

def generate_rag_response(user_query, documents, high_threshold=0.45, low_threshold=0.12):
    """
    Alur Constrained RAG:
    - Skor >= high_threshold -> Jawab langsung dari Knowledge Base
    - low_threshold <= Skor < high_threshold -> Top-k ke LLM sebagai konteks
    - Skor < low_threshold -> Wajib menjawab tidak tahu
    """
    max_score, top_docs = tfidf_retrieval(user_query, documents, top_k=3)

    if not top_docs or max_score < low_threshold:
        return NOT_FOUND_MESSAGE, "Tidak Ditemukan (Skor Rendah)", max_score

    if max_score >= high_threshold:
        best_doc = re.sub(r"^\[.*?\]\s*", "", top_docs[0]["text"])
        return best_doc, "Direct Match KB (Tanpa LLM)", max_score

    llm_answer = ask_constrained_llm(user_query, top_docs)
    return llm_answer, "Constrained LLM (Top-K Konteks)", max_score