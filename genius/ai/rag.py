import os
import json
from pathlib import Path
from dotenv import load_dotenv

# Load env variables
load_dotenv()

# Path locations
PROJECT_ROOT = Path(__file__).parent.parent.parent
FAISS_INDEX_PATH = PROJECT_ROOT / "data" / "faiss_index"
NCERT_DIR = PROJECT_ROOT / "data" / "ncert"

# In-memory keyword fallback dictionary for offline/first-time launch without FAISS
MOCK_NCERT_CORPUS = {
    "photosynthesis": "Photosynthesis is the process by which green plants and some other organisms use sunlight to synthesize nutrients from carbon dioxide and water. Photosynthesis in plants generally involves the green pigment chlorophyll and generates oxygen as a byproduct. Equation: 6CO2 + 6H2O + Light energy -> C6H12O6 + 6O2. Occurs in chloroplasts.",
    "states of matter": "Matter around us exists in three different states: solid, liquid and gas. These states of matter arise due to the variation in the characteristics of the particles of matter. Solids have a fixed shape and volume. Liquids have a fixed volume but no fixed shape. Gases have neither fixed shape nor fixed volume.",
    "atomic structure": "An atom consists of a charged nucleus surrounded by electrons. Dalton proposed atoms were indivisible. J.J. Thomson discovered electrons. Rutherford discovered the atomic nucleus with alpha-scattering. Bohr proposed electrons rotate in discrete shells. Neutrons were discovered by Chadwick in the nucleus.",
    "mitosis": "Mitosis is a process of cell division that results in two genetically identical daughter cells developing from a single parent cell. It is divided into four main stages: Prophase, Metaphase, Anaphase, and Telophase. Mitosis is used for growth, repair, and asexual reproduction.",
    "dna": "Deoxyribonucleic acid (DNA) is a molecule that carries the genetic instructions used in the growth, development, functioning and reproduction of all known living organisms and many viruses. DNA is a double helix formed by two complementary strands of nucleotides bound by hydrogen bonds.",
}

# Synonyms for query translation (transliteration normalizer)
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
}

def normalize_query(query: str) -> str:
    """Normalizes Hinglish/Hindi classroom queries to core concepts."""
    query_clean = query.lower().strip()
    for key, val in HINGLISH_SYNONYMS.items():
        if key in query_clean:
            return val
    return query

def search_ncert_curriculum(query: str, grade: str = "9", subject: str = "Science") -> str:
    """Searches the NCERT textbook curriculum.
    
    Tries to load FAISS index. If missing, falls back to localized keyword match.
    """
    normalized_q = normalize_query(query)
    normalized_q_lower = normalized_q.lower()
    
    # 1. Try Loading FAISS Database
    try:
        if os.path.exists(FAISS_INDEX_PATH):
            from langchain_community.vectorstores import FAISS
            from langchain_community.embeddings import HuggingFaceEmbeddings
            
            # Load embeddings (sentence-transformers MiniLM-L12 multilingual)
            embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
                model_kwargs={'device': 'cpu'}
            )
            
            # Load stored FAISS database
            db = FAISS.load_local(str(FAISS_INDEX_PATH), embeddings, allow_dangerous_deserialization=True)
            
            # Filter results by grade and subject if possible by metadata
            search_query = f"{subject} Class {grade} {normalized_q}"
            results = db.similarity_search(search_query, k=3)
            
            if results:
                context = "\n\n".join([f"[Source: {doc.metadata.get('source', 'NCERT Book')}, Page {doc.metadata.get('page', 'Unknown')}]\n{doc.page_content}" for doc in results])
                return context
    except Exception as e:
        print(f"[RAG Load Warning] FAISS loader bypassed or failed: {e}. Falling back to in-memory corpus.")
        
    # 2. In-Memory Fallback
    # Check if we can find keywords in our fallback list
    matches = []
    for concept, text in MOCK_NCERT_CORPUS.items():
        if concept in normalized_q_lower or normalized_q_lower in concept:
            matches.append(f"[Source: Class {grade} NCERT textbook placeholder]\n{text}")
            
    if matches:
        return "\n\n".join(matches)
        
    return f"NCERT curriculum details for '{query}' (Grade {grade} {subject})."

def build_vector_index():
    """Reads PDF files from data/ncert, chunks them, and builds a FAISS index.
    
    Designed to be run as a setup script.
    """
    if not os.path.exists(NCERT_DIR):
        print(f"[RAG Index Builder] NCERT PDF directory '{NCERT_DIR}' does not exist.")
        return False
        
    pdf_files = list(Path(NCERT_DIR).glob("**/*.pdf"))
    if not pdf_files:
        print(f"[RAG Index Builder] No PDF files found in '{NCERT_DIR}'. Please run scripts/download_ncert.py first.")
        return False
        
    try:
        from langchain_community.document_loaders import PyPDFDirectoryLoader
        from langchain_text_splitters import RecursiveCharacterTextSplitter
        from langchain_community.embeddings import HuggingFaceEmbeddings
        from langchain_community.vectorstores import FAISS
        
        print(f"[RAG Index Builder] Reading {len(pdf_files)} PDFs from {NCERT_DIR}...")
        loader = PyPDFDirectoryLoader(str(NCERT_DIR))
        documents = loader.load()
        
        print(f"[RAG Index Builder] Splitting {len(documents)} document pages...")
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        docs = text_splitter.split_documents(documents)
        
        print("[RAG Index Builder] Initializing sentence-transformer multilingual embeddings...")
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
            model_kwargs={'device': 'cpu'}
        )
        
        print(f"[RAG Index Builder] Computing embeddings and building FAISS index with {len(docs)} chunks...")
        db = FAISS.from_documents(docs, embeddings)
        
        # Save to disk
        os.makedirs(os.path.dirname(FAISS_INDEX_PATH), exist_ok=True)
        db.save_local(str(FAISS_INDEX_PATH))
        print(f"[RAG Index Builder] FAISS index saved successfully to '{FAISS_INDEX_PATH}'!")
        return True
    except Exception as e:
        print(f"[RAG Index Builder Error] Failed to compile vector index: {e}")
        return False
