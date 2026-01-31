"""
Memory Module - Pinecone Vector Database Integration
Handles embedding generation and memory storage/retrieval
"""

import os
from typing import List, Dict, Any
from datetime import datetime
from pinecone import Pinecone, ServerlessSpec
import google.generativeai as genai
from termcolor import colored

# Initialize Pinecone
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "kuro-memory")

# Initialize Gemini for embeddings
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def get_embedding(text: str) -> List[float]:
    """Generate embedding using Google's text-embedding-004 model (768 dimensions)"""
    try:
        result = genai.embed_content(
            model="models/text-embedding-004",
            content=text,
            task_type="retrieval_document"
        )
        return result['embedding']
    except Exception as e:
        print(colored(f"❌ Embedding Error: {e}", "red"))
        return [0.0] * 768  # Return zero vector on error

def init_pinecone():
    """Initialize Pinecone index if it doesn't exist"""
    try:
        if INDEX_NAME not in pc.list_indexes().names():
            print(colored(f"🔧 Creating Pinecone index: {INDEX_NAME}", "yellow"))
            pc.create_index(
                name=INDEX_NAME,
                dimension=768,
                metric="cosine",
                spec=ServerlessSpec(
                    cloud="aws",
                    region=os.getenv("PINECONE_ENV", "us-east-1")
                )
            )
        print(colored(f"✅ Pinecone index ready: {INDEX_NAME}", "green"))
        return pc.Index(INDEX_NAME)
    except Exception as e:
        print(colored(f"❌ Pinecone Init Error: {e}", "red"))
        return None

def upsert_memory(text: str, metadata: Dict[str, Any]) -> bool:
    """Store memory in Pinecone with metadata"""
    try:
        index = pc.Index(INDEX_NAME)
        embedding = get_embedding(text)
        
        # Generate unique ID based on timestamp
        memory_id = f"mem_{int(datetime.now().timestamp() * 1000)}"
        
        # Add timestamp to metadata
        metadata["timestamp"] = datetime.now().isoformat()
        metadata["content"] = text
        
        # Upsert to Pinecone
        index.upsert(vectors=[(memory_id, embedding, metadata)])
        
        print(colored(f"💾 Memory saved: {text[:50]}...", "cyan"))
        return True
    except Exception as e:
        print(colored(f"❌ Memory Save Error: {e}", "red"))
        return False

def retrieve_context(query: str, top_k: int = 3) -> List[Dict[str, Any]]:
    """Retrieve relevant memories from Pinecone"""
    try:
        index = pc.Index(INDEX_NAME)
        query_embedding = get_embedding(query)
        
        # Query Pinecone
        results = index.query(
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True
        )
        
        # Extract matches
        memories = []
        for match in results.matches:
            memories.append({
                "content": match.metadata.get("content", ""),
                "score": match.score,
                "metadata": match.metadata
            })
        
        if memories:
            print(colored(f"🧠 Retrieved {len(memories)} memories", "magenta"))
        
        return memories
    except Exception as e:
        print(colored(f"❌ Memory Retrieval Error: {e}", "red"))
        return []

def list_all_memories(limit: int = 10) -> List[Dict[str, Any]]:
    """List recent memories (for debugging/admin)"""
    try:
        index = pc.Index(INDEX_NAME)
        # Note: Pinecone doesn't have a direct "list all" - this is a placeholder
        # In production, you'd maintain a separate metadata store
        print(colored("⚠️ List all memories not fully implemented", "yellow"))
        return []
    except Exception as e:
        print(colored(f"❌ List Memories Error: {e}", "red"))
        return []

def delete_memory(memory_id: str) -> bool:
    """Delete a specific memory"""
    try:
        index = pc.Index(INDEX_NAME)
        index.delete(ids=[memory_id])
        print(colored(f"🗑️ Memory deleted: {memory_id}", "yellow"))
        return True
    except Exception as e:
        print(colored(f"❌ Delete Memory Error: {e}", "red"))
        return False
