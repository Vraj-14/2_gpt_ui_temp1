import os
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
import ollama
from app.config import EMBEDDER_MODEL, FAISS_INDEX_PATH, EMBEDDINGS_PATH, TOP_K

# Initialize embedder
embedder = SentenceTransformer(EMBEDDER_MODEL)

# === Build FAISS index from scratch ===
def build_faiss_index(chunks, index_path=FAISS_INDEX_PATH, emb_path=EMBEDDINGS_PATH):
    texts = [c['text'] for c in chunks]
    embs = embedder.encode(texts, convert_to_numpy=True)
    dim = embs.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(embs)
    faiss.write_index(index, index_path)
    np.save(emb_path, embs)
    return index, embs

# === Load FAISS index and embeddings ===
def load_index(chunks):
    if not (os.path.exists(FAISS_INDEX_PATH) and os.path.exists(EMBEDDINGS_PATH)):
        return build_faiss_index(chunks)
    index = faiss.read_index(FAISS_INDEX_PATH)
    embs = np.load(EMBEDDINGS_PATH)
    return index, embs

# === Main RAG inference ===
def rag_answer(chunks, question, index=None, embeddings=None):
    if index is None or embeddings is None:
        index, embeddings = load_index(chunks)

    q_emb = embedder.encode([question])
    D, I = index.search(q_emb, TOP_K)
    selected = [chunks[i]['text'] for i in I[0] if i < len(chunks)]
    context = "\n\n".join(selected)
    prompt = f"Context:\n{context}\n\nQuestion: {question}\nAnswer:"
    
    response = ollama.chat(
        model="qwen3:8b",  # or your preferred Ollama model
        messages=[{"role": "user", "content": prompt}]
    )
    return response['message']['content'].strip()

# === Expose to app.py ===
def get_or_build_index(text_chunks):
    return load_index(text_chunks)
