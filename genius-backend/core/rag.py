import os
import json
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Path locations
PROJECT_ROOT = Path(__file__).resolve().parent.parent
NCERT_CHUNKS_PATH = PROJECT_ROOT / "data" / "ncert_chunks.json"
CHROMA_DB_PATH = PROJECT_ROOT / "data" / "chroma_db"

HINGLISH_SYNONYMS = {
    "prakash sanshleshan": "photosynthesis",
    "prakash-sanshleshan": "photosynthesis",
    "प्रकाश संश्लेषण": "photosynthesis",
    "solid liquid gas": "states of matter",
    "padarth ki avastha": "states of matter",
    "padarth ki avasthayein": "states of matter",
    "parmanu sanrachna": "atomic structure",
    "parmanu structure": "atomic structure",
    "mitosis division": "mitosis",
    "cell division": "mitosis",
    "koshika vibhajan": "mitosis",
    "vidyut dhara": "current electricity",
    "bijli": "current electricity"
}

def normalize_query(query: str) -> str:
    """Normalizes Hinglish/Hindi queries to standard topic names."""
    query_clean = query.lower().strip()
    for key, val in HINGLISH_SYNONYMS.items():
        if key in query_clean:
            return val
    return query

def keyword_search(query: str) -> tuple[str, str]:
    """Helper that performs simple keyword overlap search against ncert_chunks.json.
    
    Returns:
        tuple: (chunk_text, source)
    """
    normalized_q = normalize_query(query).lower()
    
    # Load chunks
    if not os.path.exists(NCERT_CHUNKS_PATH):
        return "", ""
        
    try:
        with open(NCERT_CHUNKS_PATH, "r", encoding="utf-8") as f:
            chunks = json.load(f)
    except Exception as e:
        print(f"[RAG Error] Failed to read ncert_chunks.json: {e}")
        return "", ""

    # First, look for direct topic matches (e.g. "photosynthesis" in query)
    for topic, info in chunks.items():
        if topic in normalized_q or normalized_q in topic:
            return info["text"], info.get("source", "NCERT Syllabus")

    # Word-based matching count
    words = [w for w in normalized_q.split() if len(w) > 3 and w not in ["explain", "samjhao", "about", "what", "define"]]
    if not words:
        words = normalized_q.split()

    best_match = None
    best_score = 0
    
    for topic, info in chunks.items():
        score = 0
        topic_lower = topic.lower()
        text_lower = info["text"].lower()
        
        # Give higher weight to topic matches
        for word in words:
            if word in topic_lower:
                score += 5
            elif word in text_lower:
                score += 1
                
        if score > best_score:
            best_score = score
            best_match = info

    if best_match:
        return best_match["text"], best_match.get("source", "NCERT Syllabus")
        
    # Return a generic default
    return "", ""

def search_ncert_curriculum(query: str, grade: str = "9", subject: str = "Science") -> str:
    """Searches NCERT curriculum using ChromaDB or falls back to in-memory keyword matching."""
    normalized_q = normalize_query(query)
    
    # 1. Attempt ChromaDB Semantic Search
    try:
        if os.path.exists(CHROMA_DB_PATH):
            import chromadb
            from sentence_transformers import SentenceTransformer
            
            client = chromadb.PersistentClient(path=str(CHROMA_DB_PATH))
            collection = client.get_or_create_collection("ncert_collection")
            
            model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
            query_embedding = model.encode(normalized_q).tolist()
            
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=2,
                where={"subject": subject, "grade": grade}
            )
            
            if results and results.get("documents") and results["documents"][0]:
                docs = results["documents"][0]
                metas = results["metadatas"][0] if results.get("metadatas") else []
                
                context_parts = []
                for i, doc in enumerate(docs):
                    meta = metas[i] if i < len(metas) else {}
                    source = meta.get("source", "NCERT Book")
                    page = meta.get("page", "Unknown")
                    context_parts.append(f"[Source: {source}, Page {page}]\n{doc}")
                return "\n\n".join(context_parts)
    except Exception as e:
        print(f"[RAG Load Warning] ChromaDB/SentenceTransformer query failed or skipped: {e}. Using keyword fallback.")

    # 2. Keyword Search Fallback
    text, source = keyword_search(query)
    if text:
        return f"[Source: {source}]\n{text}"
        
    return f"NCERT curriculum details for '{query}' (Grade {grade} {subject})."
