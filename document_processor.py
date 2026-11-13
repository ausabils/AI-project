import os
import re
from docx import Document

def load_docx_knowledge_base(file_path):
    """
    Membaca paragraf berdasarkan 5 bagian heading utama dan seluruh baris tabel
    dari Informasi_Mata_Kuliah_AI_UNP.docx menjadi potongan pengetahuan (chunks).
    """
    if not os.path.exists(file_path):
        return []

    doc = Document(file_path)
    chunks = []
    current_section = "Informasi Umum Mata Kuliah AI"
    buffer = []

    # 1. Ekstrak paragraf per bagian (1. Informasi Umum, 2. Apa Itu AI, dst.)
    for para in doc.paragraphs:
        text = para.text.strip()
        if not text:
            continue

        if re.match(r"^\d+\.\s+", text):
            if buffer:
                chunks.append(f"[{current_section}] " + " ".join(buffer))
                buffer = []
            current_section = text
        else:
            buffer.append(text)

    if buffer:
        chunks.append(f"[{current_section}] " + " ".join(buffer))

    # 2. Ekstrak baris tabel Materi Pokok Perkuliahan (Pertemuan 1 - 16)
    for table in doc.tables:
        headers = [cell.text.strip() for cell in table.rows[0].cells]
        for row in table.rows[1:]:
            row_values = [cell.text.strip() for cell in row.cells]
            row_text = " | ".join(
                f"{headers[i]}: {row_values[i]}"
                for i in range(len(headers))
                if i < len(row_values)
            )
            if row_text:
                chunks.append(f"[Silabus & Materi Perkuliahan AI] {row_text}")

    return chunks