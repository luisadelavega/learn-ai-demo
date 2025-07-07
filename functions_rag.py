import fitz  # PyMuPDF
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List, Tuple

#Step 1: Read and split PDF into chunks
def extract_pdf_chunks(pdf_path: str, chunk_size: int = 500) -> List[str]:
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()

    # Simple chunking by sentence length
    chunks = []
    current_chunk = ""
    for sentence in text.split(". "):
        if len(current_chunk) + len(sentence) < chunk_size:
            current_chunk += sentence + ". "
        else:
            chunks.append(current_chunk.strip())
            current_chunk = sentence + ". "
    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks

# Step 2: Embed chunks
def embed_chunks(chunks: List[str], model_name: str = "all-MiniLM-L6-v2") -> Tuple[np.ndarray, List[str]]:
    model = SentenceTransformer(model_name)
    embeddings = model.encode(chunks, convert_to_numpy=True)
    return embeddings, chunks

# Step 3: Store in FAISS index
def create_faiss_index(embeddings: np.ndarray) -> faiss.IndexFlatL2:
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)
    return index

# Step 4: Query and retrieve top-k relevant chunks
def retrieve_relevant_chunks(query: str, index: faiss.IndexFlatL2, chunks: List[str], model: SentenceTransformer, k: int = 3) -> List[str]:
    query_embedding = model.encode([query], convert_to_numpy=True)
    distances, indices = index.search(query_embedding, k)
    return [chunks[i] for i in indices[0]]

# RAG pipeline
def rag_from_pdf(pdf_path: str, query: str, k: int = 3):
    print("Extracting and chunking PDF...")
    chunks = extract_pdf_chunks(pdf_path)
    
    print("Embedding chunks...")
    model = SentenceTransformer("all-MiniLM-L6-v2")
    embeddings, chunks = embed_chunks(chunks, model_name="all-MiniLM-L6-v2")
    
    print("Creating FAISS index...")
    index = create_faiss_index(embeddings)
    
    print("Retrieving relevant chunks...")
    relevant_chunks = retrieve_relevant_chunks(query, index, chunks, model, k)
    
    return relevant_chunks
