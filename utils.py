# utils.py - All helper functions
import hashlib
import json
from datetime import datetime
from langdetect import detect, DetectorFactory
from sentence_transformers import SentenceTransformer
import chromadb
import numpy as np

# Make language detection consistent
DetectorFactory.seed = 0

# Load the free embedding model (runs on your computer)
embedder = SentenceTransformer('all-MiniLM-L6-v2')

# Setup free vector database (stores knowledge locally)
chroma_client = chromadb.PersistentClient(path="./knowledge_db")
collection = chroma_client.get_or_create_collection(
    name="global_knowledge",
    metadata={"hnsw:space": "cosine"}
)

# Simple cache to remember answers
cache = {}

def detect_language(text):
    """Detect what language the user is speaking"""
    try:
        lang = detect(text)
        return lang
    except:
        return "en"  # Default to English if detection fails

def get_embedding(text):
    """Convert text to numbers (embeddings) for searching"""
    return embedder.encode(text).tolist()

def search_knowledge(query, top_k=3):
    """Search your local knowledge base"""
    try:
        query_embedding = get_embedding(query)
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )
        if results['documents']:
            return results['documents'][0]
        return []
    except:
        return []

def add_to_knowledge(text, metadata=None):
    """Add new knowledge to your local database"""
    try:
        embedding = get_embedding(text)
        collection.add(
            documents=[text],
            embeddings=[embedding],
            metadatas=[metadata or {"source": "user"}],
            ids=[hashlib.md5(text.encode()).hexdigest()]
        )
        return True
    except:
        return False

def get_from_cache(query):
    """Check if we've answered this question before"""
    # Get embedding of the question
    query_emb = np.array(get_embedding(query))
    
    for cached_q, cached_data in cache.items():
        cached_emb = np.array(cached_data['embedding'])
        # Check if questions are similar (cosine similarity)
        similarity = np.dot(query_emb, cached_emb) / (np.linalg.norm(query_emb) * np.linalg.norm(cached_emb))
        if similarity > 0.85:  # 85% similar = same question
            return cached_data['answer']
    return None

def save_to_cache(query, answer):
    """Save Q&A to memory"""
    # Keep cache from growing too big
    if len(cache) > 100:
        # Remove oldest item
        oldest_key = list(cache.keys())[0]
        del cache[oldest_key]
    
    cache[query] = {
        'answer': answer,
        'embedding': get_embedding(query),
        'timestamp': datetime.now().isoformat()
    }

def format_response(text, language):
    """Make the response look nice"""
    # Add language emoji
    lang_emojis = {
        "en": "🇬🇧", "hi": "🇮🇳", "es": "🇪🇸", "fr": "🇫🇷",
        "de": "🇩🇪", "zh": "🇨🇳", "ar": "🇸🇦", "ja": "🇯🇵"
    }
    emoji = lang_emojis.get(language, "🌍")
    return f"{emoji} {text}"