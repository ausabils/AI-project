# 🤖 Chatbot Asisten Akademik Mata Kuliah AI - UNP

Aplikasi chatbot cerdas berbasis **Constrained Retrieval-Augmented Generation (Constrained RAG)** yang dirancang untuk menjawab pertanyaan seputar informasi perkuliahan, silabus, jadwal, dan komponen penilaian mata kuliah **Artificial Intelligence (Kecerdasan Buatan)** di Program Studi S1 Informatika, Universitas Negeri Padang (UNP).

---

## 🧠 Arsitektur Sistem (Constrained RAG)

Sistem ini menggabungkan pencarian berbasis kemiripan kata kunci (**TF-IDF + Cosine Similarity**) dengan **Google Gemini LLM** yang dibatasi secara ketat pada konteks dokumen lokal (`Informasi_Mata_Kuliah_AI_UNP.docx`):

1. **Input Pengguna → TF-IDF Matching** terhadap Knowledge Base lokal.
2. **Skor Tinggi ($\ge 0.45$) → Direct Match KB:** Menjawab langsung dari segmen dokumen paling relevan tanpa memanggil LLM.
3. **Skor Menengah ($0.12 - 0.44$) → Constrained LLM:** Mengambil *top-3* segmen dokumen paling mirip sebagai **KONTEKS** dan mengirimkannya ke Gemini dengan instruksi ketat hanya boleh menjawab berdasarkan konteks tersebut (dilengkapi mekanisme *fallback* lokal otomatis).
4. **Skor Rendah ($< 0.12$) / Di Luar Konteks → Penolakan Terkendali:** Chatbot wajib menjawab *"Maaf, saya tidak tahu. Informasi tersebut tidak tersedia di dalam Knowledge Base."* untuk mencegah halusinasi.

---

## 📜 Aturan & Panduan Penggunaan Chatbot

Agar jawaban akurat dan sesuai dengan mekanisme *Constrained RAG*, perhatikan aturan berikut saat berinteraksi dengan chatbot:

### 1. Batasan Ruang Lingkup Pengetahuan (*Strict Grounding*)
* Chatbot **hanya menjawab** pertanyaan yang bersumber dari dokumen Knowledge Base (`Informasi_Mata_Kuliah_AI_UNP.docx`).
* Chatbot **dilarang menebak atau mengarang** jawaban dari pengetahuan umum di luar dokumen. Jika pertanyaan berada di luar konteks mata kuliah AI UNP, chatbot akan secara otomatis menolak dan menyatakan ketidaktahuannya.

### 2. Aturan Penulisan Pertanyaan (*Prompting Rules*)
* **Gunakan Bahasa Indonesia yang jelas** dan sertakan kata kunci spesifik yang berkaitan dengan mata kuliah AI (contoh: *dosen pengampu, jadwal kuliah, tujuan belajar, pertemuan 1-16, UTS, UAS, komponen penilaian*).
* **Pertanyaan Langsung (*Direct Query*):** Jika kata kunci sangat mirip dengan isi dokumen (skor TF-IDF $\ge 0.45$), sistem menampilkan kutipan langsung dari dokumen tanpa pemrosesan LLM.
* **Pertanyaan Kompleks / Gabungan:** Jika pertanyaan menggabungkan beberapa topik (misalnya menanyakan nama dosen sekaligus jadwal kuliah), sistem akan meneruskan *top-3* konteks relevan ke Gemini untuk dirangkum dengan rapi.

### 3. Contoh Pertanyaan yang Didukung vs Ditolak
| Jenis Pertanyaan | Contoh Input Pengguna | Respons Sistem |
| :--- | :--- | :--- |
| **Valid (Informasi Umum)** | *"Siapa dosen pengampu dan jadwal kuliah AI?"* | Menjawab **5337 - Dr. Yeka Hendriyani, S.Kom., M.Kom.** & jadwal **Senin, 15.00 - 17.00 WIB**. |
| **Valid (Konsep & Silabus)** | *"Apa materi pertemuan 14 sampai 15?"* | Menjelaskan topik **Natural Language Processing (NLP) & RAG**. |
| **Valid (Penilaian)** | *"Bagaimana komponen penilaian mata kuliah AI?"* | Menampilkan rincian bobot Kehadiran (10%), Tugas (25%), UTS (25%), Proyek & UAS (40%). |
| **Di Luar Konteks** | *"Siapa rektor UNP saat ini?"* atau *"Resep nasi goreng"* | Menolak menjawab: *"Maaf, saya tidak tahu. Informasi tersebut tidak tersedia di dalam Knowledge Base."* |

---

## 📂 Struktur Proyek

```text
AI-project/
├── app.py                              # Antarmuka web interaktif berbasis Streamlit
├── rag_engine.py                       # Mesin TF-IDF retrieval & Constrained Gemini LLM
├── document_processor.py               # Ekstraktor paragraf & tabel dari dokumen .docx
├── Informasi_Mata_Kuliah_AI_UNP.docx   # Dokumen Knowledge Base utama mata kuliah AI
├── requirements.txt                    # Daftar pustaka Python yang dibutuhkan
├── .gitignore                          # Mengecualikan file .env dan cache dari Git
└── README.md                           # Dokumentasi proyek & aturan penggunaan
