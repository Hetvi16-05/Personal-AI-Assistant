import google.generativeai as genai
from sqlalchemy.orm import Session
from app.models.vector_memory import MemoryEmbedding
from app.config import settings

genai.configure(api_key=settings.GEMINI_API_KEY)


def _embed(text: str) -> list[float]:
    """Generate embedding using Gemini text-embedding-004."""
    result = genai.embed_content(
        model="models/text-embedding-004",
        content=text,
        task_type="retrieval_document"
    )
    return result["embedding"]


def store_memory(db: Session, user_id: int, text: str, tags: str = "") -> MemoryEmbedding:
    """Embed text and store in memory_embeddings table."""
    try:
        embedding = _embed(text)
        embedding_str = ",".join(str(x) for x in embedding)
    except Exception:
        embedding_str = None

    mem = MemoryEmbedding(
        user_id=user_id,
        memory_text=text,
        embedding=embedding_str,
        tags=tags
    )
    db.add(mem)
    db.commit()
    db.refresh(mem)
    return mem


def retrieve_relevant(db: Session, user_id: int, query: str, top_k: int = 5) -> list[str]:
    """
    Find top-k relevant memories using cosine similarity (pgvector).
    Falls back to recent memories if pgvector not available.
    """
    try:
        query_embedding = _embed(query)

        # pgvector cosine distance query
        from sqlalchemy import text as sql_text
        query_vec = f"[{','.join(str(x) for x in query_embedding)}]"

        results = db.execute(
            sql_text("""
                SELECT memory_text
                FROM memory_embeddings
                WHERE user_id = :uid
                ORDER BY embedding <=> CAST(:vec AS vector)
                LIMIT :k
            """),
            {"uid": user_id, "vec": query_vec, "k": top_k}
        ).fetchall()

        return [row[0] for row in results]

    except Exception:
        # Fallback: return most recent memories
        mems = db.query(MemoryEmbedding).filter(
            MemoryEmbedding.user_id == user_id
        ).order_by(MemoryEmbedding.created_at.desc()).limit(top_k).all()
        return [m.memory_text for m in mems]
